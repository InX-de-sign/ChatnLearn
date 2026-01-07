"""
Real-time Interview Bot - Conducts a full interview without intermediate feedback
"""
import asyncio
import json
import os
from typing import List, Dict
from loguru import logger
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class InterviewBot:
    def __init__(self, interview_setup=None):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.interview_setup = interview_setup or {}
        
        # Customize questions based on setup
        job_title = self.interview_setup.get('jobTitle', 'this position')
        focus_areas = self.interview_setup.get('focusAreas', [])
        
        # Interview questions pool - customize based on focus areas
        self.questions = []
        
        # Always start with tell me about yourself
        self.questions.append("Tell me about yourself and your background.")
        
        # Add role-specific question
        self.questions.append(f"What interests you most about the {job_title} role?")
        
        # Add questions based on focus areas
        if 'technical' in focus_areas:
            self.questions.append("Describe a technically challenging project you've worked on recently. What was your approach?")
        if 'behavioral' in focus_areas or 'leadership' in focus_areas:
            self.questions.append("Tell me about a time when you had to deal with a difficult team member or conflict.")
        if 'problem-solving' in focus_areas:
            self.questions.append("Walk me through your problem-solving process when facing a complex challenge.")
        if 'communication' in focus_areas:
            self.questions.append("Describe a situation where you had to explain a complex concept to someone without technical knowledge.")
        
        # Add general questions
        self.questions.append("How do you handle tight deadlines and pressure?")
        self.questions.append("Where do you see yourself in five years?")
        
        self.current_question_index = 0
        self.conversation_history = []
        self.qa_pairs = []  # Store all Q&A pairs for final analysis
        
    def get_next_question(self) -> str:
        """Get the next interview question"""
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None
    
    async def get_ai_response(self, user_message: str) -> str:
        """Get response from Azure OpenAI"""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Build system prompt for interviewer behavior with context
            context_info = ""
            if self.interview_setup:
                context_info = f"""
Interview Context:
- Job Title: {self.interview_setup.get('jobTitle', 'Not specified')}
- Company: {self.interview_setup.get('company', 'Not specified')}
- Interview Format: {self.interview_setup.get('interviewFormat', 'Not specified')}
- Candidate Experience: {self.interview_setup.get('experience', 'Not specified')}
- Focus Areas: {', '.join(self.interview_setup.get('focusAreas', [])) if self.interview_setup.get('focusAreas') else 'General'}

"""
            
            system_prompt = f"""{context_info}You are a professional job interviewer conducting a realistic behavioral interview. 
Your role is to:
- Ask questions naturally and professionally
- Listen to candidate responses without excessive praise
- Ask follow-up questions when appropriate
- Keep questions relevant to job interview scenarios
- Be professional and neutral (not overly friendly or supportive)
- Do NOT provide feedback, encouragement, or validation during the interview
- Move smoothly between topics
- Maintain a formal, realistic interview atmosphere
- Respond with brief acknowledgments like "I see", "Understood", "Thank you" before next questions
- DO NOT ask about job title, company, or background already provided in context

Keep your responses concise, neutral, and professional, as if in a real corporate interview."""
            
            messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
            
            # Check if using API Management endpoint
            is_api_management = "azure-api.net" in self.endpoint
            
            if is_api_management:
                # API Management endpoint - use direct HTTP
                url = f"{self.endpoint}/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            else:
                # Standard Azure OpenAI endpoint
                url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            
            payload = {
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            logger.info(f"📤 Sending request to Azure OpenAI")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        assistant_message = result["choices"][0]["message"]["content"]
                        
                        # Add assistant response to history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                        
                        logger.info(f"✅ Got response from Azure OpenAI")
                        return assistant_message
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Azure OpenAI error {response.status}: {error_text}")
                        return "I apologize, I'm having trouble connecting. Could you please repeat that?"
                        
        except Exception as e:
            logger.error(f"❌ Error in get_ai_response: {str(e)}")
            return "I apologize for the technical difficulty. Could you please continue?"
    
    async def start_interview(self, websocket) -> str:
        """Send initial greeting and first question"""
        job_title = self.interview_setup.get('jobTitle', 'this position')
        company = self.interview_setup.get('company', '')
        
        greeting = f"Hello! Thank you for taking the time to interview with us today"
        if company:
            greeting += f" at {company}"
        greeting += f" for the {job_title} position. "
        
        first_question = self.get_next_question()
        
        full_message = greeting + first_question
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": full_message
        })
        
        # Store as Q&A pair
        self.qa_pairs.append({
            "question": first_question,
            "answer": None  # Will be filled when user responds
        })
        
        return full_message
    
    async def process_answer(self, user_answer: str) -> str:
        """Process user's answer and ask next question or follow-up"""
        # Store the answer to the current question
        if self.qa_pairs and self.qa_pairs[-1]["answer"] is None:
            self.qa_pairs[-1]["answer"] = user_answer
        
        # Decide: ask follow-up or move to next question
        # For simplicity, we'll alternate: 1 answer -> next question
        next_question = self.get_next_question()
        
        if next_question:
            # Acknowledge and ask next question
            response = await self.get_ai_response(user_answer)
            
            # If AI didn't naturally transition to next question, add it
            if "?" not in response:
                response += f" {next_question}"
            
            # Store new Q&A pair
            self.qa_pairs.append({
                "question": next_question,
                "answer": None
            })
            
            return response
        else:
            # Interview complete
            return "Thank you for sharing your thoughts. That concludes our interview today. I'll now prepare your feedback summary."
    
    async def generate_summary(self) -> Dict:
        """Generate comprehensive feedback summary using AI"""
        try:
            # Build summary prompt
            qa_text = "\n\n".join([
                f"Q: {qa['question']}\nA: {qa['answer']}"
                for qa in self.qa_pairs if qa['answer']
            ])
            
            summary_prompt = f"""You are an expert interview evaluator. Analyze this interview transcript and provide detailed feedback.

Interview Transcript:
{qa_text}

Provide a comprehensive evaluation in the following JSON format:
{{
    "overall_score": <number 0-100>,
    "language_use": {{
        "score": <number 0-100>,
        "feedback": "<detailed feedback on vocabulary, grammar, fluency, clarity>",
        "strengths": ["<strength1>", "<strength2>"],
        "improvements": ["<improvement1>", "<improvement2>"]
    }},
    "answer_quality": {{
        "score": <number 0-100>,
        "feedback": "<detailed feedback on relevance, completeness, depth, structure>",
        "strengths": ["<strength1>", "<strength2>"],
        "improvements": ["<improvement1>", "<improvement2>"]
    }},
    "detailed_feedback": "<overall comprehensive feedback paragraph>",
    "key_takeaways": ["<takeaway1>", "<takeaway2>", "<takeaway3>"]
}}

Be specific, constructive, and encouraging in your feedback."""

            # Check if using API Management endpoint
            is_api_management = "azure-api.net" in self.endpoint
            
            if is_api_management:
                url = f"{self.endpoint}/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
            else:
                url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an expert interview evaluator providing structured JSON feedback."},
                    {"role": "user", "content": summary_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            logger.info("📊 Generating interview summary...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        summary_text = result["choices"][0]["message"]["content"]
                        
                        # Try to parse JSON from response
                        try:
                            # Remove markdown code blocks if present
                            if "```json" in summary_text:
                                summary_text = summary_text.split("```json")[1].split("```")[0].strip()
                            elif "```" in summary_text:
                                summary_text = summary_text.split("```")[1].split("```")[0].strip()
                            
                            summary_data = json.loads(summary_text)
                            logger.info("✅ Summary generated successfully")
                            return summary_data
                        except json.JSONDecodeError:
                            logger.error("❌ Failed to parse JSON from AI response")
                            # Return a fallback structure
                            return {
                                "overall_score": 75,
                                "language_use": {
                                    "score": 75,
                                    "feedback": "Good communication overall.",
                                    "strengths": ["Clear expression"],
                                    "improvements": ["Continue practicing"]
                                },
                                "answer_quality": {
                                    "score": 75,
                                    "feedback": "Satisfactory answers provided.",
                                    "strengths": ["Relevant responses"],
                                    "improvements": ["More detail could help"]
                                },
                                "detailed_feedback": summary_text,
                                "key_takeaways": ["Keep practicing", "Good effort overall"]
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Summary generation error {response.status}: {error_text}")
                        raise Exception("Failed to generate summary")
                        
        except Exception as e:
            logger.error(f"❌ Error in generate_summary: {str(e)}")
            raise


async def run_interview_bot(websocket):
    """Main function to run the interview bot"""
    
    try:
        logger.info("🎤 Interview bot starting...")
        
        # Wait for interview setup data
        setup_data = await websocket.receive_json()
        interview_setup = {}
        
        if setup_data.get("type") == "setup":
            interview_setup = setup_data.get("data", {})
            logger.info(f"Received interview setup: {interview_setup}")
        
        # Initialize bot with setup data
        bot = InterviewBot(interview_setup)
        
        # Send initial greeting and first question
        initial_message = await bot.start_interview(websocket)
        await websocket.send_json({
            "type": "ai_message",
            "content": initial_message
        })
        
        # Main interview loop
        while True:
            # Receive user's answer
            data = await websocket.receive_json()
            
            if data.get("type") == "user_message":
                user_message = data.get("content", "").strip()
                
                if not user_message:
                    continue
                
                logger.info(f"👤 User: {user_message[:50]}...")
                
                # Process answer and get next question
                response = await bot.process_answer(user_message)
                
                # Send response
                await websocket.send_json({
                    "type": "ai_message",
                    "content": response
                })
                
                # Check if interview is complete
                if "concludes our interview" in response.lower():
                    logger.info("🏁 Interview completed, generating summary...")
                    
                    # Generate summary
                    summary = await bot.generate_summary()
                    
                    # Send summary
                    await websocket.send_json({
                        "type": "interview_complete",
                        "summary": summary
                    })
                    
                    logger.info("✅ Summary sent to client")
                    break
                    
            elif data.get("type") == "end_interview":
                logger.info("🛑 User ended interview early")
                
                # Generate summary with available data
                if any(qa['answer'] for qa in bot.qa_pairs):
                    summary = await bot.generate_summary()
                    await websocket.send_json({
                        "type": "interview_complete",
                        "summary": summary
                    })
                break
                
    except Exception as e:
        logger.error(f"❌ Error in interview bot: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "content": "An error occurred during the interview."
        })
