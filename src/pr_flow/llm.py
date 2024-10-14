from crewai import LLM
import os



Ollama = LLM(
    model="ollama/llama3.2:1b",
    base_url="http://localhost:11434",
    )

Groq = LLM(
    model="groq/llama3-8b-8192",
    max_tokens=1024,
    top_p=1,
    temperature=1,
    )