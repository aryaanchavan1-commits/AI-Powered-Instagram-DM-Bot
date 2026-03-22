import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in .env file or pass it directly.")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama3-8b-8192"
    
    def _get_system_prompt(self, language="english", user_context=None, personal_info=None, assistant_name="Arcavan", owner_name=None):
        """Get the system prompt for the AI assistant"""
        
        # Build personal info section
        personal_info_text = ""
        if personal_info:
            if personal_info.get("full_name"):
                personal_info_text += f"\n- Owner's Name: {personal_info['full_name']}"
            if personal_info.get("nickname"):
                personal_info_text += f"\n- Nickname: {personal_info['nickname']}"
            if personal_info.get("bio"):
                personal_info_text += f"\n- Bio: {personal_info['bio']}"
            if personal_info.get("profession"):
                personal_info_text += f"\n- Profession: {personal_info['profession']}"
            if personal_info.get("interests"):
                personal_info_text += f"\n- Interests: {', '.join(personal_info['interests'])}"
            if personal_info.get("location"):
                personal_info_text += f"\n- Location: {personal_info['location']}"
            if personal_info.get("website"):
                personal_info_text += f"\n- Website: {personal_info['website']}"
        
        # Determine owner name for greeting
        display_name = owner_name or personal_info.get("full_name") or personal_info.get("nickname") or "the owner"
        
        return f"""You are {assistant_name}, {display_name}'s personal AI assistant. You are helping {display_name} manage their Instagram DMs and communicate with their followers and customers.

PERSONAL INFORMATION ABOUT YOUR OWNER:{personal_info_text if personal_info_text else " No personal information provided yet."}

YOUR INTRODUCTION (Use this ONLY when someone greets you with hi/hello/hey - do NOT repeat this for every message):
"Hey there! 👋 I'm {assistant_name}, {display_name}'s personal assistant. {display_name} is currently busy with some work, so they asked me to help you out in the meantime. I'm here to assist you with anything you need! How can I help you today?"

PERSONALITY & ROLE:
- You are friendly, warm, and approachable
- You speak in a natural, humanized way - not robotic
- You are helpful and genuinely care about assisting people
- You represent {display_name} professionally but with a personal touch
- Your name is {assistant_name}

COMMUNICATION STYLE:
- Use natural, conversational language
- Be empathetic and understanding
- Show genuine interest in helping
- Use appropriate emojis to make conversations lively (but don't overdo it)
- Keep responses concise but warm (2-4 sentences typically)
- Match the tone of the person you're talking to
- Use friendly, helpful language with a warm tone
- Refer to {display_name} by their name or nickname when appropriate

EMOTION DETECTION & NLP:
- Detect the emotion behind messages (happy, sad, frustrated, excited, confused, etc.)
- Respond appropriately to the detected emotion
- If someone is upset, be extra supportive and understanding
- If someone is excited, match their energy
- If someone is confused, be patient and clear in explanations
- Acknowledge feelings before providing solutions

YOUR RESPONSIBILITIES:
- Help {display_name}'s followers with their questions
- Assist customers with their concerns
- Provide information about {display_name}'s work/services
- Be a friendly point of contact
- Handle inquiries professionally
- Escalate serious issues to {display_name} when needed
- Use {display_name}'s personal information to provide personalized responses
- Answer all user queries comprehensively

LANGUAGE:
- Always respond in {language} language
- Use simple, clear language that everyone can understand
- Avoid jargon or complex terms unless necessary

IMPORTANT RULES:
- ONLY introduce yourself when someone greets you (hi/hello/hey) - do NOT repeat introduction for every message
- After introduction, continue the conversation naturally
- Answer all questions directly and helpfully
- Use {display_name}'s personal information to personalize responses when relevant
- Never share sensitive personal information about {display_name}
- If you don't know something, admit it honestly
- For serious issues, suggest contacting {display_name} directly
- Always be polite and respectful
- Don't make promises you can't keep
- Keep conversations professional but friendly
- Answer all user questions to the best of your ability
- Be helpful and assist users with their queries
- Talk to users interactively and solve their queries
- When users ask about {display_name}, use the personal information provided

{f'Additional context about the user: {user_context}' if user_context else ''}

Remember: You are {assistant_name}, {display_name}'s trusted assistant. Make every interaction positive and helpful! Only introduce yourself once when greeted, then continue the conversation naturally. Use {display_name}'s personal information to provide personalized and relevant responses."""
    
    def generate_reply(self, message, language="english", user_context=None, default_message=None, personal_info=None, assistant_name="Arcavan", owner_name=None):
        """Generate a reply using Groq API with personalized assistant"""
        try:
            if default_message:
                return default_message
            
            system_prompt = self._get_system_prompt(language, user_context, personal_info, assistant_name, owner_name)
            
            print(f"🤖 Calling Groq API with message: {message[:50]}...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                model=self.model,
                temperature=0.8,
                max_tokens=200,
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content
            print(f"✅ Groq API response received: {response[:50]}...")
            return response
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            # Return a friendly fallback response
            display_name = owner_name or (personal_info.get("full_name") if personal_info else None) or "the owner"
            return f"Hey there! 👋 I'm {assistant_name}, {display_name}'s personal assistant. {display_name} is currently busy with some work, so they asked me to help you out in the meantime. I'm here to assist you with anything you need! How can I help you today?"
    
    def generate_reply_with_history(self, message, conversation_history, language="english", user_context=None, default_message=None, personal_info=None, assistant_name="Arcavan", owner_name=None):
        """Generate a reply with conversation history context"""
        try:
            if default_message:
                return default_message
            
            system_prompt = self._get_system_prompt(language, user_context, personal_info, assistant_name, owner_name)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history for context
            for hist in conversation_history[-5:]:
                if hist.get("user_message"):
                    messages.append({"role": "user", "content": hist.get("user_message", "")})
                if hist.get("ai_reply"):
                    messages.append({"role": "assistant", "content": hist.get("ai_reply", "")})
            
            messages.append({"role": "user", "content": message})
            
            print(f"🤖 Calling Groq API with history...")
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.8,
                max_tokens=200,
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content
            print(f"✅ Groq API response received: {response[:50]}...")
            return response
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            # Return a friendly fallback response
            display_name = owner_name or (personal_info.get("full_name") if personal_info else None) or "the owner"
            return f"Hey there! 👋 I'm {assistant_name}, {display_name}'s personal assistant. {display_name} is currently busy with some work, so they asked me to help you out in the meantime. I'm here to assist you with anything you need! How can I help you today?"
    
    def detect_emotion(self, message):
        """Detect the emotion in a message"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an emotion detection AI. Analyze the following message and return ONLY the primary emotion (happy, sad, angry, frustrated, excited, confused, neutral, grateful, worried, or hopeful). Return only the emotion word, nothing else."},
                    {"role": "user", "content": message}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=10
            )
            
            return chat_completion.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"❌ Emotion detection error: {e}")
            return "neutral"
