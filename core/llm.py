from langchain_google_genai import ChatGoogleGenerativeAI 
from dotenv import load_dotenv 
import getpass
import os 
from langchain_ollama import ChatOllama

load_dotenv() 



if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

def get_llm()->ChatGoogleGenerativeAI:

    return ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    streaming=True
    
)
"""
def get_llm() -> ChatOllama:
    
    Creates and returns a ChatOllama LLM instance.

    return ChatOllama(
        model="deepseek-v3.2:cloud",
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {
                "Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"
            }
        },
        
            
         
    )
 """   