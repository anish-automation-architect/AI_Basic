"""
ANTHROPIC SDK                    GROQ SDK
─────────────────────────────────────────────────────
client.messages.create(...)      client.chat.completions.create(...)

messages=[                       messages=[
  {"role": "user", ...}    →       {"role": "user", ...}   ← same ✅
]                                ]

system="..."          →          {"role": "system", "content": "..."}
                                 as first item in messages list

response.content[0].text  →     response.choices[0].message.content
=============================================================================================================================
📅 DAY 1 — The Mental Model Nobody Gives You
🧩 Core Lesson: Agents ≠ Chatbots
Chatbot       AI Agent
Responds      Decides
One shot      Multi-step loop
Stateless     Has memory + goals
Passive       Takes actions


🔥 The Analogy That Changes Everything
Think of an agent like a junior developer you hired:
You give them a goal (not instructions)
They have tools (browser, code, files)
They plan → act → observe → repeat
They stop when goal is met or they're stuck
📖 The Agent Loop (Tattoo This In Your Brain)
GOAL → PLAN → ACT → OBSERVE → REFLECT → PLAN → ACT → ...DONE
----------------------------------------------------------------------------------------------------------------------------------------
✅ Practice Task
Open Claude.ai (free)
Prompt: "Act as an agent. Your goal is to plan a test automation framework. Think step by step, tell me your plan BEFORE doing anything, then execute each step."
Observe: Notice how it plans first. That's the agent loop in text form.
🤯 Mind-Expander
Agents don't "know" things — they reason about what to do NEXT. Intelligence = good next-step selection, not memorized facts.
----------------------------------------------------------------------------------------------------------------------------------------
📅 DAY 2 — How Agents Actually "Think"
🧩 Core Lesson: The ReAct Pattern
Most courses skip this. ReAct = Reasoning + Acting — the backbone of every real agent.
Thought  → "I need to find X"
Action   → call_tool(search, "X")
Observe  → "Results say Y"
Thought  → "Now I need Z"
Action   → call_tool(calculate, Z)
...
Answer   → Final response
----------------------------------------------------------------------------------------------------------------------------------------

✅ Practice Task
Run it — read every THOUGHT/ACTION/OBSERVATION
Change the goal to something from your real QA work
Notice: agent PLANS before acting — this is what separates it from a chatbot
🤯 Mind-Expander
The model isn't "thinking" — it's predicting what a thinking entity would write next. But the OUTPUT is indistinguishable from reasoning. That's enough.
----------------------------------------------------------------------------------------------------------------------------------------
📅 DAY 3 — Tools: How Agents Get Superpowers
🧩 Core Lesson: Tools = Agent's Hands
Without tools, an agent is just a smart talker. With tools, it can read files, call APIs, run code, browse web.
Agent Brain (LLM)
      ↓ decides to call
   Tool: search_web("X")
      ↓ gets result back
Agent Brain (LLM)
      ↓ decides next step
   Tool: write_file("report.md")
----------------------------------------------------------------------------------------------------------------------------------------














"""