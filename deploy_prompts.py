import os
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

def deploy_prompts():
    host = os.getenv("LANGFUSE_HOST") or "https://us.cloud.langfuse.com"
    print(f"Connecting to Langfuse host: {host}")
    
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=host
    )

    prompts_to_deploy = ["rag_qa", "meeting_extraction"]

    for name in prompts_to_deploy:
        print(f"Deploying prompt '{name}' to production...")
        try:
            # In a real CI/CD, we might want to tag a specific version that was tested.
            # Here we just promote the latest version to 'production'.
            prompt = langfuse.get_prompt(name)
            langfuse.create_prompt(
                name=name,
                prompt=prompt.prompt,
                config=prompt.config,
                labels=["production"]
            )
            print(f"OK: '{name}' is now in production.")
        except Exception as e:
            print(f"ERROR deploying '{name}': {e}")

if __name__ == "__main__":
    deploy_prompts()
