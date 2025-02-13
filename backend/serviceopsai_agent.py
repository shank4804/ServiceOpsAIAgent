"""
ServiceOps AI Agent Module

This module implements an AI-powered agent for monitoring and managing Azure infrastructure.
It uses OpenAI's GPT-4 with llama_index's ReAct framework to analyze Azure Monitor metrics and provide actionable insights.
"""

import time
import threading
import requests
import os
from dotenv import load_dotenv
import logging
from azure_monitor import AzureMonitorAgent
from monitoring_tool import AzureMonitoringTool
import json
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent

# Initialize environment and logging
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)

class ServiceOpsAIAgent:
    """
    AI agent that monitors Azure infrastructure and provides recommendations.
    
    The agent uses llama_index's ReAct framework to analyze Azure Monitor metrics
    and maintains a conversation history for contextual responses.
    """

    def __init__(self):
        """Initialize the ServiceOps AI agent with configuration and dependencies."""
        # Configuration
        self.api_url = os.getenv('API_URL')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.polling_interval = int(os.getenv('POLLING_INTERVAL', 300))  # 5 minutes default
        
        # Initialize LLM
        self.llm = OpenAI(
            model="gpt-4",
            api_key=self.openai_api_key,
            temperature=0.1,
            max_retries=3
        )
        
        # Initialize tools
        self.monitoring_tool = AzureMonitoringTool()
        
        # Initialize ReAct agent
        self.agent = ReActAgent.from_tools(
            tools=[self.monitoring_tool],
            llm=self.llm,
            verbose=True,
            system_prompt=self.get_system_message()
        )
        
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
            logger.info("Starting metrics analysis...")
            metrics_response = self.monitoring_tool.run()
            if not metrics_response or metrics_response.get("status") != "success":
                logger.warning("No metrics data available.")
                return
                
            metrics = metrics_response["metrics"]
            logger.info(f"Retrieved metrics: {json.dumps(metrics, indent=2)}")
            
            # Use ReAct agent to analyze metrics
            prompt = f"""
            Analyze these Azure Monitor metrics and provide actionable recommendations:
            ####
            {metrics}
            ####
            Focus on:
            1. Performance bottlenecks
            2. Resource utilization
            3. Error rates and issues
            4. Optimization opportunities
            """
            
            logger.info("Sending prompt to ReAct agent for analysis...")
            response = self.agent.chat(prompt)
            logger.info(f"Agent's thought process:\n{response.response}")
            
            self.send_recommendation(response.response)
        except Exception as e:
            logger.error(f"Error fetching and analyzing metrics: {e}", exc_info=True)

    def chat_with_ai(self, prompt):
        """
        Process a user chat message with full context awareness.
        
        Args:
            prompt (str): User's message
            
        Returns:
            str: AI's response
        """
        try:
            logger.info(f"Processing chat prompt: {prompt}")
            
            # Use ReAct agent for chat
            response = self.agent.chat(prompt)
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": prompt})
            self.chat_history.append({"role": "assistant", "content": response.response})
            
            # Maintain history size
            if len(self.chat_history) > 20:
                logger.info("Trimming chat history to last 20 messages")
                self.chat_history = self.chat_history[-20:]
                
            return response.response
        except Exception as e:
            logger.error(f"Error in chat with AI: {e}", exc_info=True)
            return "I apologize, but I'm having trouble processing your request at the moment. Please try again or check the system metrics directly."

    def get_system_message(self):
        """Get the base system message that defines the AI's role and capabilities."""
        return """
        You are ServiceOps AI, a ReAct-based AI assistant designed to help engineers proactively manage, debug, and optimize their Azure Cloud infrastructure.
        Your role is critical during high-stress, on-call situations where engineers need actionable insights quickly. Analyze metrics, logs, and system state to 
        provide recommendations and step-by-step guidance for issue resolution.

        When analyzing infrastructure:
        1. Always check current metrics before making recommendations
        2. Prioritize critical issues and performance bottlenecks
        3. Provide specific, actionable steps for remediation
        4. Consider resource utilization and cost optimization
        5. Maintain context from previous interactions
        """

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
