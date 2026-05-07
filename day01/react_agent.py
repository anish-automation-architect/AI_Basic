import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Simulate the ReAct loop manually first
# so you SEE what frameworks hide from you
def think_act_bserve(goal:str):
    messages= []
    system = """You are a ReAct agent. For every task:
    1. Start with your THOUGHT: (your reasoning)
    2. Then ACTION: (what you'd do- search/calculate/read)
    3. Then OBSERVATION:(what you got back - make it up for now)
    4. Repeat until you reach ANSWER:

    Be explicit Show ALL steps. Never skip answer directly """
    messages.append({"role": "user","content": goal})
    #Groq uses chat.completions.create — NOT client.messages.create
    response = llm.chat.completions.create(
        model="llama-3.1-8b-instant",   # free, fast, small
        # system = system, # Groq dont use background
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": goal}
        ] ,
        max_tokens=1024,

    )
    # ✅ Groq response path is also different from Anthropic
    return response.choices[0].message.content

#Test it
goal = "What is the best approach to wtite test cases for a new feature?"
result = think_act_bserve(goal)
print(result)


"""
**Task: Determine best approach to write test cases for a new feature**

**THOUGHT:** To identify the best approach to write test cases for a new feature, I need to consider the following factors:
- The nature of the feature: is it simple or complex, user-facing or backend-facing?
- The scope of the feature: how many components are involved, and are there any potential edge cases?
- The testing pyramid: should I focus on unit tests, integration tests, or UI tests?
- The testing framework: what tools and libraries are available to me?

**ACTION:** Research and read relevant guidelines and best practices for writing test cases, such as:
- The testing pyramid concept
- Example test cases for common scenarios
- Best practices for writing effective test cases

**OBSERVATION:** After researching, I came across a few guidelines and best practices that can help me write effective test cases:
- The testing pyramid recommends a 80/20 distribution of unit tests, integration tests, and UI tests.
- A good test case should cover the happy path, edge cases, and potential failure scenarios.
- The ARRANGE-ACT-ASSERT (AAA) pattern can help me structure my test cases.

**THOUGHT:** Based on the guidelines and best practices, I need to outline the specific steps to write test cases for the new feature.
- Identify the components involved in the feature.
- Determine the scope of the feature and potential edge cases.
- Decide on the testing framework and libraries to use.
- Create test cases using the ARRANGE-ACT-ASSERT pattern, focusing on the happy path, edge cases, and potential failure scenarios.

**ACTION:** Use the ARRANGE-ACT-ASSERT pattern to structure each test case, and consider the testing pyramid to guide the distribution of test cases across unit tests, integration tests, and UI tests.

**OBSERVATION:** After outlining the specific steps, I realized that I need to consider the following:
- The ARRANGE step should cover the setup and setup of the test environment.
- The ACT step should perform the action being tested.
- The ASSERT step should verify the expected outcome.
- I should also consider mocking dependencies and using a mocking framework to isolate and test the feature in isolation.

**THOUGHT:** To make the test cases more effective, I should also consider the following:
- Test case prioritization: prioritize the most critical test cases first.
- Test data management: plan how to manage test data, such as creating test data, deleting test data after each test, and handling duplicate test data.
- Test case dependencies: identify and manage dependencies between test cases.

**ACTION:** Develop a test data management plan to ensure test data is effectively managed and deleted after each test.

**OBSERVATION:** After considering the test data management plan, I realized that I need to:
- Create test data management scripts or tools to automate test data creation and deletion.
- Design a data management strategy to handle duplicate test data, errors, and other edge cases.

**ANSWER:** The best approach to write test cases for a new feature involves:
1. Researching and applying the testing pyramid concept and the ARRANGE-ACT-ASSERT pattern.
2. Determining the scope and nature of the feature.
3. Deciding on the testing framework and libraries to use.
4. Creating test cases using the ARRANGE-ACT-ASSERT pattern, focusing on the happy path, edge cases, and potential failure scenarios.
5. Considering test case prioritization, test data management, and test case dependencies.
6. Developing a test data management plan to manage test data effectively.
7. Identifying and managing dependencies between test cases.
8. Prioritizing and executing the most critical test cases first.
"""