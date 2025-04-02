import os
import json
from crewai import LLM, Crew, Agent, Task


# os.environ["OPENAI_API_KEY"] = ""

# llm = LLM(
#     model="ollama/llama3.2",
#     base_url="http://localhost:11434"
# )


os.environ["GROQ_API_KEY"] = "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"

llm = LLM(
    model="groq/llama3-8b-8192",
    temperature=0.7
)


# Load Jira Ticket Data
def load_jira_ticket():
    with open("jira.json", "r") as file:
        return json.load(file)

# Load Test Cases
def load_test_cases():
    with open("testcases.json", "r") as file:
        return json.load(file)

jira_ticket = load_jira_ticket()
test_cases = load_test_cases()

# Jira Analyzer Agent
jira_analyzer = Agent(
    name="Jira Analyzer",
    role="Extracts details from Jira tickets and categorizes them",
    goal="Identify key details like title, description, labels, and status",
    backstory="A highly efficient AI agent specializing in Jira ticket analysis.",
    verbose=True,
    llm= llm
)


# Test Case Recommender Agent
test_case_recommender = Agent(
    name="Test Case Recommender",
    role="Suggests relevant test cases based on analysed Jira report",
    goal="Match analysed jira details with relevant predefined test cases",
    backstory="An expert QA assistant capable of mapping issues to test cases.",
    verbose=True,
    llm= llm
)

# Define Tasks
analyze_jira_task = Task(
    name="Analyze Jira Ticket",
    agent=jira_analyzer,
    description=f"Extract key details from the provided Jira ticket and categorize the issue. Here is the Jira details - \n{jira_ticket}",
    expected_output="A summary of the Jira ticket including title, description, and key details.",
    output_file='local/analyze_jira_test.txt'
)



recommend_test_cases_task = Task(
    name="Recommend Test Cases",
    agent=test_case_recommender,
    description=f'Take the data from analyzed report placed at local/analyze_jira_test.txt and map the data to a list of predefined test cases and suggest applicable ones.Here are the list of test cases - \n{test_cases}',#f"Map Jira ticket details to a relevant list of test cases and suggest applicable ones. Here are the list of test cases - \n{test_cases} \n and the jira ticket - \n{jira_ticket}",
    expected_output="A list of suggested test cases from the available test cases which match the details with analyzer report in a json format ",#with same title and id only mentioned in the test cases that matches the Jira ticket.",
    output_file='local/recommend_test.json'
)

# Crew AI Team
crew = Crew(
    agents=[jira_analyzer, test_case_recommender],
    tasks=[analyze_jira_task, recommend_test_cases_task]
)

# Run Crew
results = crew.kickoff()
print(results)