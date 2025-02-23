from abc import ABC, abstractmethod
import google.generativeai as genai
from typing import List, Dict

class ChatService(ABC):
    @abstractmethod
    def get_followup_questions(self, query: str) -> List[str]:
        pass

    @abstractmethod
    def generate_response(self, query: str, context: Dict) -> str:
        pass

class GeminiChatService(ChatService):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def get_followup_questions(self, query: str) -> List[str]:
        prompt = f"""
        The user has described the following symptom: "{query}".
        Before providing possible causes, recommended medicines, and precautions,
        generate a list of **two to three** follow-up questions that will help in better diagnosis.
        """
        response = self.model.generate_content(prompt)
        questions = response.text.strip().split("\n") if response else []
        return [q for q in questions if q.strip()]

    def generate_response(self, query: str, context: Dict) -> str:
        prompt = f"""
        Previous History:
        {context.get('history', '')}

        Current Query: {query}
        Follow-up Responses:
        {context.get('followup_responses', {})}

        Please provide medical advice considering the user's history and current symptoms.
        """
        response = self.model.generate_content(prompt)
        return response.text if response else "I'm sorry, I couldn't generate a response."
