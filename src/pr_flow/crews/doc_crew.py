from crewai import Agent, Crew, Process, Task
from ..llm import Groq
from textwrap import dedent
import time


def doc_agent():
	return Agent(
        role = 'Documentation Reviewer',
        goal = 'Ensure that the documentation is as per the standards for Hasicorp terraform providers.',
        backstory=dedent("""
            You are an experienced documentation reviewer. 
            You are highly customer oriented.
			You ensures that the documentation is readable, maintainable, and free of redundancy.
			You have experience understanding the format and content of Hasicorp terraform official documentation.
            """),
        allow_delegation=False,
		llm=Groq,
	)

def doc_review_task():
	return Task(
        description=dedent("""
        Ensure that the documentation is of high quality and adheres to the language standards.

		**Instructions:**
		- The input follows the GitHub diff format, with '+' indicating added code and '-' indicating removed code.
		- Only recommend improvements based on the given diff.
		- Provide grammatical corrections when needed.
		- Keep responses brief and adhere to Hasicorp terraform offical documentation standards.
		**Human Input:**
		  {diff}     
        """),
        expected_output="A detailed report summarizing the documentation quality issues, with clear examples, and suggestions for improvement.",
		agent=doc_agent()
	)

def DocCrew():
	"""Creates the Review Crew"""
	return Crew(
		agents=[doc_agent()], 
		tasks=[doc_review_task()],
		process=Process.sequential,
		verbose=True,
	)
