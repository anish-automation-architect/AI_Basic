import os
import json
import uuid
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ─── ID GENERATOR ─────────────────────────────────────────────────────────────
# def generate_bug_id() -> str:
#     """Always generate IDs in code — never let the LLM do it"""
#     number = str(uuid.uuid4().int)[:4]        # 4 random digits
#     return f"BUG-{number}"                    # → BUG-4821

COUNTER_FILE = "bug_counter.json"

def generate_bug_id() -> str:
    # Read current counter
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            data = json.load(f)
        counter = data["last"] + 1
    else:
        counter = 1000             # start from BUG-1000

    # Save incremented counter
    with open(COUNTER_FILE, "w") as f:
        json.dump({"last": counter}, f)

    return f"BUG-{counter}"        # → BUG-1000, BUG-1001, BUG-1002 ...

# ─── TOOL DEFINITION (no id field — Python owns that) ────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_bug_report",
            "description": """Creates and saves a structured bug report.
Call with flat key-value pairs only.
Do NOT include an id field — that is auto-generated.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":    {"type": "string",
                                 "description": "Short bug title"},
                    "severity": {"type": "string",
                                 "enum": ["low", "medium", "high", "critical"]},
                    "steps":    {"type": "string",
                                 "description": "Steps to reproduce"},
                    "expected": {"type": "string",
                                 "description": "Expected result"},
                    "actual":   {"type": "string",
                                 "description": "Actual result"}
                },
                "required": ["title", "severity", "steps", "expected", "actual"]
            }
        }
    }
]

# ─── TOOL IMPLEMENTATION ───────────────────────────────────────────────────────
def create_bug_report(title, severity, steps, expected, actual) -> str:
    bug_id   = generate_bug_id()
    filename = f"{bug_id}.json"

    report = {
        "id":         bug_id,
        "title":      title,
        "severity":   severity,
        "steps":      steps,
        "expected":   expected,
        "actual":     actual,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ timestamp
    }

    os.makedirs("bugs", exist_ok=True)
    with open(f"bugs/{filename}", "w") as f:
        json.dump(report, f, indent=2)

    # ✅ Richer return string → gives LLM enough to form a proper sentence
    return (
        f"Bug report created successfully.\n"
        f"ID       : {bug_id}\n"
        f"File     : bugs/{filename}\n"
        f"Severity : {severity}\n"
        f"Created  : {report['created_at']}"
    )
# ─── TOOL DISPATCHER ──────────────────────────────────────────────────────────
def execute_tool(name: str, args: dict) -> str:

    # Unwrap if nested
    if "properties" in args and isinstance(args["properties"], dict):
        args = args["properties"]

    if name == "create_bug_report":
        # ✅ Only keep fields your function actually accepts
        allowed = {"title", "severity", "steps", "expected", "actual"}
        args = {k: v for k, v in args.items() if k in allowed}

        # Validate required fields still present
        missing = [f for f in allowed if f not in args]
        if missing:
            return f"Error: missing required fields: {missing}"

        return create_bug_report(**args)

    return f"Unknown tool: {name}"

# ─── AGENT ────────────────────────────────────────────────────────────────────
def run_agent(user_message: str):
    print(f"\n🎯 Task: {user_message}\n{'='*50}")

    messages = [
        {
            "role": "system",
            "content": """You are a QA agent. When asked to file a bug, use create_bug_report tool.
After the tool runs, respond in this exact format:
✅ Bug filed successfully!
   ID       : <id from result>
   Severity : <severity from result>
   Created  : <timestamp from result>
   File     : <filename from result>"""
   },
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        tools=tools,
        tool_choice="auto",
        temperature=0,              # ✅ critical for tool calling reliability
        messages=messages
    )

    msg           = response.choices[0].message
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "stop":
        print(f"\n🤖 Agent: {msg.content}")
        return

    if finish_reason == "tool_calls":
        for tc in msg.tool_calls:
            tool_args = json.loads(tc.function.arguments)
            print(f"🔧 Tool   : {tc.function.name}")
            print(f"   Args  : {json.dumps(tool_args, indent=2)}")

            result = execute_tool(tc.function.name, tool_args)
            print(f"   Result: {result}")

        messages.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name,
                              "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]
        })
        messages.append({
            "role": "tool",
            "tool_call_id": msg.tool_calls[0].id,
            "content": result
        })

        final = client.chat.completions.create(
            model=MODEL, max_tokens=128, messages=messages
        )
        print(f"\n✅ Agent: {final.choices[0].message.content}")

# ─── RUN ──────────────────────────────────────────────────────────────────────
run_agent(
    "File a bug: Login button does nothing after entering username & password on tapping . "
)

"""



"""