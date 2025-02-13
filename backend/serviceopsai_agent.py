"""
ServiceOps AI Agent Module

This module implements an AI-powered agent for monitoring and managing Azure infrastructure.
It uses OpenAI's GPT-4 to analyze Azure Monitor metrics and provide actionable insights.
"""

import time
import threading
import requests
import os
from dotenv import load_dotenv
import logging
from azure_monitor import AzureMonitorAgent

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceOpsAIAgent:
    """
    AI agent that monitors Azure infrastructure and provides recommendations.
    
    The agent continuously monitors Azure Monitor metrics, analyzes them using GPT-4,
    and maintains a conversation history for contextual responses.
    """

    def __init__(self):
        """Initialize the ServiceOps AI agent with configuration and dependencies."""
        # Configuration
        self.api_url = os.getenv('API_URL')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.polling_interval = int(os.getenv('POLLING_INTERVAL', 300))  # 5 minutes default
        
        # State management
        self.chat_history = []
        self.azure_monitor_agent = AzureMonitorAgent()

    # Core monitoring functionality
    def start(self):
        """Start the continuous monitoring loop."""
        while True:
            self.fetch_and_analyze_metrics()
            time.sleep(self.polling_interval)

    def fetch_and_analyze_metrics(self):
        """Fetch current metrics and generate AI recommendations."""
        try:
            metrics = self.azure_monitor_agent.get_metrics()
            if not metrics:
                logger.warning("No metrics data available.")
                return
            recommendation = self.get_openai_recommendation(metrics)
            self.send_recommendation(recommendation)
        except Exception as e:
            logger.error(f"Error fetching and analyzing metrics: {e}")

    # AI interaction methods
    def get_system_message(self):
        """Get the base system message that defines the AI's role and capabilities."""
        return """
        You are ServiceOps AI, a ReAct-based AI assistant designed to help engineers proactively manage, debug, and optimize their Azure Cloud infrastructure.
        Your role is critical during high-stress, on-call situations where engineers need actionable insights quickly. Analyze metrics, logs, and system state to 
        provide recommendations and step-by-step guidance for issue resolution.
        """

    def get_openai_recommendation(self, metrics):
        """
        Generate recommendations based on current metrics.
        
        Args:
            metrics (dict): Current system metrics from Azure Monitor
            
        Returns:
            str: AI-generated recommendation
        """
        prompt = f"""
        Given the following Azure Monitor metrics, provide actionable recommendations for optimizing system performance or resolving potential issues:
        ####
        {metrics}
        ####
        - Think in depth and provide a detailed analysis of the metrics. Focus on highlighting potential risks, resource bottlenecks, and any areas requiring immediate attention.
        - Provide prioritized action steps where applicable.
        - Keep it short and concise.
        """
        try:
            response = self._make_openai_request(
                messages=[
                    {"role": "system", "content": self.get_system_message()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return response
        except Exception as e:
            logger.error(f"Error fetching recommendation from OpenAI: {e}")
            return "Error fetching recommendation from OpenAI."

    def chat_with_ai(self, prompt):
        """
        Process a user chat message with full context awareness.
        
        Args:
            prompt (str): User's message
            
        Returns:
            str: AI's response
        """
        # Build context
        current_metrics = self.azure_monitor_agent.get_metrics()
        system_context = f"""
        Current System State:
        - Total Metrics Being Monitored: {len(current_metrics)}
        - System Overview: {self.get_current_metrics_context()}
        """
        # Construct messages with context and history
        messages = [
            {
                "role": "system", 
                "content": f"""
                {self.get_system_message()}
                You have access to real-time system metrics and historical chat context. Use this information to provide accurate, 
                contextual responses. When analyzing issues:
                1. Consider the current system state and metrics
                2. Reference relevant historical context from previous conversations
                3. Provide specific, actionable recommendations
                4. If metrics indicate issues, highlight them in your response
                5. Use technical details from the metrics when relevant
                {system_context}
                """
            }
        ]
        
        # Add chat history and current message
        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": prompt})

        try:
            ai_response = self._make_openai_request(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": prompt})
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Maintain history size
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
                
            return ai_response
        except Exception as e:
            logger.error(f"Error in chat with AI: {e}")
            return "I apologize, but I'm having trouble processing your request at the moment. Please try again or check the system metrics directly."

    # Helper methods
    def _make_openai_request(self, messages, max_tokens=300, temperature=None):
        """
        Make a request to OpenAI API with error handling.
        
        Args:
            messages (list): List of message dictionaries
            max_tokens (int): Maximum tokens in response
            temperature (float, optional): Response randomness
            
        Returns:
            str: AI response content
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}'
        }
        
        data = {
            'model': 'gpt-4o',
            'messages': messages,
            'max_tokens': max_tokens
        }
        if temperature is not None:
            data['temperature'] = temperature

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()

    def get_current_metrics_context(self):
        """Get current metrics in a formatted string."""
        try:
            metrics = self.azure_monitor_agent.get_metrics()
            if not metrics:
                return "No metrics data available."
            
            # Format metrics for better readability
            context = []
            for metric in metrics:
                services = metric['services']
                for service_name, service_data in services.items():
                    main_metric = next(
                        (key for key, value in service_data.items() 
                         if isinstance(value, (int, float)) and key != 'status'),
                        None
                    )
                    if main_metric:
                        value = service_data[main_metric]
                        context.append(f"{service_name} - {main_metric}: {value}")
            
            return "\n".join(context)
        except Exception as e:
            logger.error(f"Error formatting metrics context: {e}")
            return "Metrics context not available."

    def send_recommendation(self, recommendation):
        """Send an AI recommendation to the API."""
        try:
            response = requests.post(
                f'{self.api_url}/api/recommendation',
                json={'recommendation': recommendation}
            )
            if response.status_code == 200:
                logger.info('Recommendation sent successfully.')
            else:
                logger.error(f'Failed to send recommendation: {response.status_code}')
        except Exception as e:
            logger.error(f'Error sending recommendation: {e}')

if __name__ == "__main__":
    agent = ServiceOpsAIAgent()
    agent_thread = threading.Thread(target=agent.start)
    agent_thread.start()
