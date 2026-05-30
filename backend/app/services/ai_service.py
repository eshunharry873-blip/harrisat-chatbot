from app.config import settings
from app.logger import logger
from typing import Optional, List
import openai
import json

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-3.5-turbo"
    
    async def generate_response(self, messages: List[dict], temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Service error: {str(e)}")
            raise
    
    async def stream_response(self, messages: List[dict], temperature: float = 0.7):
        try:
            with self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
                max_tokens=2000
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"AI Stream error: {str(e)}")
            raise
    
    async def generate_title(self, first_message: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate a short, concise title (max 50 chars) for a conversation starting with the user's message."},
                    {"role": "user", "content": first_message}
                ],
                temperature=0.5,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Title generation error: {str(e)}")
            return "New Conversation"
