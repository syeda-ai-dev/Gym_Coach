from typing import Dict, Any
from fastapi import HTTPException
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from mhire.com.config.config import Config

class AICoach:
    def __init__(self, config: Config):
        """Initialize the AI Coach"""
        self.llm = ChatOpenAI(
            openai_api_key=config.openai_api_key,
            model=config.model,
            temperature=0.7
        )
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        self.system_prompt = """You are an AI Health & Gym Coach, equipped to:
        1. Answer general fitness and nutrition questions with scientific accuracy
        2. Provide motivational support and encouragement
        3. Give personalized advice based on user context
        4. Share relevant fitness tips and best practices
        
        Always maintain a supportive and professional tone. If asked about medical conditions, 
        remind users to consult healthcare professionals for medical advice."""

    async def chat(self, message: str) -> Dict[str, Any]:
        """Process a chat message"""
        if not message or not message.strip():
            raise HTTPException(400, "Message cannot be empty")

        if len(message) > 2000:
            raise HTTPException(400, "Message exceeds maximum length of 2000 characters")

        try:
            full_prompt = (
                f"{self.system_prompt}\n\nUser: {message}"
                if not self.memory.chat_memory.messages
                else message
            )

            response = self.conversation.predict(input=full_prompt)
            return {"response": response}
            
        except Exception as e:
            # Pass through the actual error message
            raise HTTPException(500, f"{type(e).__name__}: {str(e)}")

