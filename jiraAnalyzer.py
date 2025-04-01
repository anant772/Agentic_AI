import os
import json
from crewai import LLM, Crew, Agent, Task
from langchain_openai import ChatOpenAI


os.environ["OPENAI_API_KEY"] = ""

llm = ChatOpenAI(
    model="ollama/llama3.2",
    base_url="http://localhost:11434/v1"
)


# os.environ["GROQ_API_KEY"] = ""

# llm = LLM(
#     model="groq/llama3-8b-8192",
#     temperature=0.7
# )


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

def analyze_jira(ticket):
    return f"Analyzed Jira Ticket: {ticket['title']} - {ticket['description']}"

# Test Case Recommender Agent
test_case_recommender = Agent(
    name="Test Case Recommender",
    role="Suggests relevant test cases based on Jira ticket details",
    goal="Match Jira details with relevant predefined test cases",
    backstory="An expert QA assistant capable of mapping issues to test cases.",
    verbose=True,
    llm= llm
)

def recommend_test_cases(ticket, test_cases):
    relevant_cases = [tc["test_case"] for tc in test_cases if tc["category"] in ticket["title"]]
    return f"Suggested Test Cases: {relevant_cases if relevant_cases else 'No matching test cases found.'}"

# Report Generator Agent
report_generator = Agent(
    name="Report Generator",
    role="Generates a structured report with suggested test cases",
    goal="Compile a well-formatted test case recommendation report",
    backstory="A meticulous report compiler that ensures clarity and completeness.",
    verbose=True,
    llm= llm
)

def generate_report(analysis, recommendations):
    return f"\nReport:\n{analysis}\n{recommendations}\n"

# Define Tasks
analyze_jira_task = Task(
    name="Analyze Jira Ticket",
    agent=jira_analyzer,
    description=f"Extract key details from the provided Jira ticket and categorize the issue. Here is the Jira details - \n{jira_ticket}",
    execute=lambda: analyze_jira(jira_ticket),
    expected_output="A summary of the Jira ticket including title, description, and key details.",
    output_file='analyze_jira_test.txt'
)

recommend_test_cases_task = Task(
    name="Recommend Test Cases",
    agent=test_case_recommender,
    description=f"Map Jira ticket details to a relevant list of test cases and suggest applicable ones. Here are the list of test cases - \n{test_cases} \n and the jira ticket - \n{jira_ticket}",
    execute=lambda: recommend_test_cases(jira_ticket, test_cases),
    expected_output="A list of suggested test cases that match the Jira ticket category.",
    output_file='recommend_test.txt'
)

generate_report_task = Task(
    name="Generate Test Case Report",
    agent=report_generator,
    description="Create a structured report with suggested test cases based on Jira ticket analysis.",
    execute=lambda: generate_report(analyze_jira_task.execute(), recommend_test_cases_task.execute()),
    expected_output="A structured report summarizing the Jira analysis and recommended test cases.",
    output_file='generate_report_test.txt'
)


# Crew AI Team
crew = Crew(
    agents=[jira_analyzer, test_case_recommender, report_generator],
    tasks=[analyze_jira_task, recommend_test_cases_task, generate_report_task]
)

# Run Crew
results = crew.kickoff()
print(results)