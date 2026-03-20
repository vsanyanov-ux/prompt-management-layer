import os
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

def upload_prompts():
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )

    # 1. RAG QA Prompt
    langfuse.create_prompt(
        name="rag_qa",
        prompt="""Context information is below.
---------------------
{{context}}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {{query}}
Answer:""",
        config={"model": "mistral-large-latest", "temperature": 0.0},
        labels=["production"]
    )

    # 2. Meeting Extraction Prompt
    langfuse.create_prompt(
        name="meeting_extraction",
        prompt="""Extract meeting information. Use the same language for names as in the source text. Be precise.
Text: {{text}}
""",
        config={"model": "mistral-nemo", "temperature": 0.0},
        labels=["production"]
    )

    print("OK All prompts uploaded successfully to Langfuse Registry!")
if __name__ == "__main__":
    upload_prompts()
