import os

from dotenv import load_dotenv

load_dotenv()

email = os.getenv("EMAIL") 
email_pwd = os.getenv("EMAIL_PWD")
ai_token = os.getenv("AI_TOKEN")  # Your Hugging Face token for AI model access