from crewai import Agent, Crew, Process, Task
from ..llm import Groq
from textwrap import dedent


def code_agent():
    return Agent(
        role = 'Expert Code Reviewer ',
		goal = 'Review code diffs for the go code for best practices as per the Hasicorp terraform standards for implementing the terraform providers.',
        backstory=dedent("""
            You are an experienced AI assistant specializing in reviewing pull requests. 
            With an access to the codebase, you have the ability to review the go language code.
			You understand the best practices as per the standards required to implements the Hasicorp terraform providers.
            """),
        allow_delegation=False,
		llm=Groq,
	)

def code_review_task():
	return Task(
        description=dedent("""
        Review the provided pull request diff and suggest improvements. 
        Use concise language to explain what can be enhanced, keeping in mind that 
        the full code isn't available. Follow the input format rules and language conventions.
        **Instructions:**
        - The input follows the GitHub diff format, with '+' indicating added code and '-' indicating removed code.
        - Only recommend improvements based on the given diff.
        - Provide code snippets when necessary.
        - Keep responses brief and adhere to coding standards for the go language.
        **Human Input:**
        {diff}
        """),
        expected_output="A concise report listing improvements along with code snippets as applicable.",
		agent=code_agent()
	)
	
def CodeCrew():
	"""Creates the Review Crew"""
	return Crew(
		agents=[code_agent()], 
		tasks=[code_review_task()],
		process=Process.sequential,
		verbose=True,
	)
