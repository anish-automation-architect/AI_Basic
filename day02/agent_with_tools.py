import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import glob

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ─── CONFIG (single source of truth — change here, works everywhere) ──────────
BUGS_FOLDER  = r"F:\Anish\PycharmProjects\PythonProjects\AL learning\AI-Practice\basic\bugs"
COUNTER_FILE = os.path.join(BUGS_FOLDER, "bug_counter.json")  # ✅ lives in bugs folder

# ─── ID GENERATOR ─────────────────────────────────────────────────────────────
def generate_bug_id() -> str:
    os.makedirs(BUGS_FOLDER, exist_ok=True)                   # ensure folder exists

    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE) as f:
            data = json.load(f)
        counter = data["last"] + 1
    else:
        counter = 1000                                         # start from BUG-1000

    with open(COUNTER_FILE, "w") as f:
        json.dump({"last": counter}, f)

    return f"BUG-{counter}"

# ─── TOOL DEFINITIONS ─────────────────────────────────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_open_bugs",
            "description": "Returns the total count and list of all filed bug report IDs.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_bug_report",
            "description": """Creates and saves a structured bug report.
Call with flat key-value pairs only.
Do NOT include an id field — that is auto-generated.
Do NOT add any extra fields like created, reporter, status.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":    {"type": "string",  "description": "Short bug title"},
                    "severity": {"type": "string",  "enum": ["low", "medium", "high", "critical"]},
                    "steps":    {"type": "string",  "description": "Steps to reproduce"},
                    "expected": {"type": "string",  "description": "Expected result"},
                    "actual":   {"type": "string",  "description": "Actual result"}
                },
                "required": ["title", "severity", "steps", "expected", "actual"]
            }
        }
    }
]

# ─── TOOL IMPLEMENTATIONS ─────────────────────────────────────────────────────
def create_bug_report(title, severity, steps, expected, actual) -> str:
    bug_id   = generate_bug_id()
    filename = os.path.join(BUGS_FOLDER, f"{bug_id}.json")    # ✅ uses BUGS_FOLDER

    report = {
        "id":         bug_id,
        "title":      title,
        "severity":   severity,
        "steps":      steps,
        "expected":   expected,
        "actual":     actual,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(BUGS_FOLDER, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    return (
        f"Bug report created successfully.\n"
        f"ID       : {bug_id}\n"
        f"File     : {filename}\n"
        f"Severity : {severity}\n"
        f"Created  : {report['created_at']}"
    )


def get_open_bugs() -> str:
    pattern = os.path.join(BUGS_FOLDER, "BUG-*.json")
    files   = glob.glob(pattern)

    if not files:
        return "FACT: Zero bug reports exist in the system."

    bug_ids = sorted([os.path.splitext(os.path.basename(f))[0] for f in files])

    return (
        f"CONFIRMED FACT FROM FILE SYSTEM:\n"
        f"Total bugs filed = {len(bug_ids)}\n"
        f"Bug IDs = {', '.join(bug_ids)}\n"
        f"Source = {BUGS_FOLDER}\n"
        f"This data is real. Report it exactly as shown."   # ✅ leaves no room for doubt
    )

# ─── TOOL DISPATCHER ──────────────────────────────────────────────────────────
def execute_tool(name: str, args: dict) -> str:
        # ✅ Handle null args — tools with no parameters send None
    if args is None:
        args = {}

    # Safety unwrap — some models wrap args inside "properties"
    if "properties" in args and isinstance(args["properties"], dict):
        args = args["properties"]

    if name == "create_bug_report":
        allowed = {"title", "severity", "steps", "expected", "actual"}
        args    = {k: v for k, v in args.items() if k in allowed}  # strip unknown fields

        missing = [f for f in allowed if f not in args]
        if missing:
            return f"Error: missing required fields: {missing}"

        return create_bug_report(**args)

    elif name == "get_open_bugs":
        return get_open_bugs()                                 # ✅ calls fixed function

    return f"Unknown tool: {name}"


# ─── AGENT LOOP ───────────────────────────────────────────────────────────────
def run_agent(user_message: str):
    print(f"\n🎯 Task: {user_message}\n{'=' * 50}")

    messages = [
        {
    "role": "system",
    "content": """You are a QA agent with two tools:
1. create_bug_report — file a new bug
2. get_open_bugs     — list all filed bugs

CRITICAL RULES:
- Tool results are ALWAYS accurate — never question or doubt them
- When get_open_bugs returns data, report it EXACTLY as received
- Never say the result is fictional, default, or needs fixing

When listing bugs respond exactly like:
Total bugs filed: <count>
IDs: <comma separated list>"""
},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        tools=tools,
        tool_choice="auto",
        temperature=0,
        messages=messages
    )

    msg           = response.choices[0].message
    finish_reason = response.choices[0].finish_reason

    # Agent answered without tool
    if finish_reason == "stop":
        print(f"\n🤖 Agent: {msg.content}")
        return

    # Agent called a tool
    if finish_reason == "tool_calls":
        for tc in msg.tool_calls:
            # ✅ Safe args parsing — replace the existing json.loads line
            raw = tc.function.arguments
            tool_args = json.loads(raw) if raw and raw.strip() not in ("null", "") else {}

            print(f"🔧 Tool   : {tc.function.name}")
            print(f"   Args  : {json.dumps(tool_args, indent=2)}")

            result = execute_tool(tc.function.name, tool_args)
            print(f"   Result: {result}")

        # Feed result back to agent
        messages.append({
            "role":       "assistant",
            "content":    msg.content,
            "tool_calls": [
                {
                    "id":       tc.id,
                    "type":     "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]
        })
        messages.append({
            "role":         "tool",
            "tool_call_id": msg.tool_calls[0].id,
            "content":      result
        })

        final = client.chat.completions.create(
            model=MODEL,
            max_tokens=256,
            messages=messages
        )
        print(f"\n✅ Agent: {final.choices[0].message.content}")


# ─── TEST RUNS ────────────────────────────────────────────────────────────────
# if __name__ == "__main__":

    # Test 1: File a bug
# run_agent(
#     "File a bug: Login button fails to appear in the home page for first launch and after refresh it appear on home page ")

# Test 2: List all bugs
run_agent("How many bugs have been filed so far?")