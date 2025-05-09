import logging

from fastapi import HTTPException

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from com.mhire.app.config.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICoach:
    def __init__(self):
        try:
            config = Config()
            self.llm = ChatOpenAI(
                openai_api_key=config.openai_api_key,
                model=config.model_name,
                temperature=1
            )
        except Exception as e:
            logger.error(f"Error initializing AICoach: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI Coach: {str(e)}")

    async def chat(self, user_message: str) -> str:
        try:
            # Define the base system prompt for a friendly AI gym coach
            system_prompt = """You are a friendly and supportive AI gym coach named Coach AI. Your role is to:
            1. Provide helpful fitness and nutrition advice in a conversational, friendly manner
            2. Naturally incorporate motivational encouragement in your responses
            3. Answer health-related questions clearly while maintaining a supportive tone
            4. Give scientifically-backed recommendations in an easy-to-understand way
            5. Be empathetic and understanding while helping users achieve their fitness goals
            
            Always maintain a friendly, conversational tone while being helpful and professional."""

            # Create the chat prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_message)
            ])

            # Get the response from the model
            response = self.llm.invoke(prompt.format_messages())
            
            return response.content

        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")