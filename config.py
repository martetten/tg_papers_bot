from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAG_API_URL = os.getenv("RAG_API_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env")
if not RAG_API_URL:
    raise ValueError("RAG_API_URL не указан в .env")