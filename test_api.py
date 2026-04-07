import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables (GITHUB_TOKEN)
load_dotenv()

# Initialize ChatOpenAI for GitHub Models using GitHub PAT
# The base_url points to the GitHub Models inference endpoint
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

# Test the connection with a simple привет (Xin chào?)
response = llm.invoke("Xin chào?")
print(response.content)

