import os
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI


os.environ["OPENAI_API_KEY"] = ""

llm = ChatOpenAI(
    model="ollama/llama3.2",
    base_url="http://localhost:11434/v1"
)

# Function to read code files from a given path
def read_code_from_directory(directory):
    code_snippets = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".java")):  # Add other extensions if needed
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    code_snippets.append(f"\nFile: {file_path}\n" + f.read())
    return "\n".join(code_snippets)

# Get project directory from user
project_path = r"C:\\Users\\Administrator\\Desktop\\Automation games"
code_to_review = read_code_from_directory(project_path)

# Define Agents
# ✅ Define AI Agents
linter_agent = Agent(
    role="Linter",
    goal="Analyze the code for syntax and style issues",
    backstory="Expert in code linting using Pylint, ESLint, and Checkstyle.",
    verbose=True,
    llm=llm
)

# security_agent = Agent(
#     role="Security Scanner",
#     goal="Detect security vulnerabilities in the code",
#     backstory="Finds SQL injections, hardcoded credentials, and other security flaws.",
#     verbose=True,
#     llm=llm
# )

# reviewer_agent = Agent(
#     role="Code Reviewer",
#     goal="Review the code and provide best practice suggestions",
#     backstory="Expert in clean code, performance, and maintainability.",
#     verbose=True,
#     llm=llm
# )

# report_generator_agent = Agent(
#     role="Report Generator",
#     goal="Summarize findings from all agents into a structured report",
#     backstory="Compiles linting, security, and review feedback into a readable report.",
#     verbose=True,
#     llm=llm
# )

# ✅ Define Tasks for Each Agent
linting_task = Task(
    description=f"Check the following code for style issues:\n{code_to_review}",
    agent=linter_agent,
    expected_output="List of syntax and style issues."
)

# security_task = Task(
#     description=f"Scan the following code for vulnerabilities:\n{code_to_review}",
#     agent=security_agent,
#     expected_output="List of security vulnerabilities."
# )

# review_task = Task(
#     description=f"Analyze the following code and suggest improvements:\n{code_to_review}",
#     agent=reviewer_agent,
#     expected_output="Best practices and performance improvements."
# )

# report_task = Task(
#     description="Compile a final review report based on all findings.",
#     agent=report_generator_agent,
#     expected_output="Structured review report summarizing all issues and suggestions."
# )


# ✅ Create Crew & Assign Tasks
code_review_crew = Crew(
    agents=[linter_agent, ],
    tasks=[linting_task,]
)

# ✅ Run the Crew (Start Code Review)
result = code_review_crew.kickoff()

print("\n--- Final Code Review Report ---\n")
print(result)