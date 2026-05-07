import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL       = "llama-3.1-8b-instant"
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "agent_memory.json")

# ─── MEMORY ENGINE ────────────────────────────────────────────────────────────
def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {"facts": []}

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_fact(fact: str):
    memory = load_memory()
    # Avoid duplicate facts
    existing = [f["fact"].lower() for f in memory["facts"]]
    if fact.lower() not in existing:
        memory["facts"].append({
            "fact":      fact,
            "saved_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        memory["facts"] = memory["facts"][-30:]   # keep last 30 only
        save_memory(memory)
        return True
    return False                                   # duplicate — not saved

# ─── EXTRACT FACTS USING A DEDICATED CALL ─────────────────────────────────────
# Instead of relying on the main model to remember to say "REMEMBER:"
# we make a SEPARATE call just to extract facts — much more reliable
def extract_facts(user_input: str, agent_reply: str) -> list[str]:
    prompt = f"""You are a fact extractor. Read this conversation snippet and extract
any personal facts the user revealed about themselves (name, location, job, skills, 
goals, preferences, experience, etc.).

User said: "{user_input}"
Agent replied: "{agent_reply}"

Output a JSON array of short fact strings. Examples:
["User's name is Anish", "User is from India", "User is looking for a job"]

If no personal facts were shared, return an empty array: []
Return ONLY the JSON array. No explanation."""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text if hasattr(response, 'content') else response.choices[0].message.content

    try:
        # Clean markdown code blocks if model adds them
        raw = raw.strip().strip("```json").strip("```").strip()
        facts = json.loads(raw)
        return facts if isinstance(facts, list) else []
    except json.JSONDecodeError:
        return []

# ─── MAIN CHAT FUNCTION ───────────────────────────────────────────────────────
def chat_with_memory(user_input: str) -> str:
    memory = load_memory()

    # Build memory context for the agent
    if memory["facts"]:
        facts_text = "\n".join([f"- {f['fact']}" for f in memory["facts"]])
        memory_context = f"\nWhat you remember about this user:\n{facts_text}\n"
    else:
        memory_context = "\nYou have no memory of this user yet.\n"

    system = f"""You are a helpful personal assistant with memory.
{memory_context}
Use what you remember to give personalized responses.
Keep responses concise and relevant."""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=256,
        temperature=0.7,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user_input}
        ]
    )

    reply = response.choices[0].message.content

    # Extract and save facts in background (separate call — reliable)
    new_facts = extract_facts(user_input, reply)
    saved = []
    for fact in new_facts:
        if add_fact(fact):
            saved.append(fact)

    if saved:
        print(f"\n   💾 Saved to memory: {saved}")

    return reply

# ─── INTERACTIVE LOOP ─────────────────────────────────────────────────────────
def main():
    print("🤖 Memory Agent Ready")
    print("   Commands: 'quit' to exit | 'memory' to see stored facts | 'clear' to reset\n")

    while True:
        user = input("You: ").strip()

        if not user:
            continue

        if user.lower() == "quit":
            print("Goodbye!")
            break

        if user.lower() == "memory":
            memory = load_memory()
            if not memory["facts"]:
                print("\n📚 Memory is empty — tell me something about yourself!\n")
            else:
                print(f"\n📚 Memory ({len(memory['facts'])} facts stored):")
                for f in memory["facts"]:
                    print(f"   • {f['fact']}  [{f['saved_at']}]")
                print()
            continue

        if user.lower() == "clear":
            save_memory({"facts": []})
            print("\n🗑️  Memory cleared.\n")
            continue

        reply = chat_with_memory(user)
        print(f"\n🤖 Agent: {reply}\n")

if __name__ == "__main__":
    main()