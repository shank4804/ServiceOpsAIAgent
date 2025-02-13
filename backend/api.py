from flask import Flask, request, jsonify
from flask_cors import CORS
from azure_monitor import AzureMonitorAgent
from serviceopsai_agent import ServiceOpsAIAgent
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

azure_monitor_agent = AzureMonitorAgent()
ai_agent = ServiceOpsAIAgent()
logger = logging.getLogger(__name__)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        metrics = azure_monitor_agent.get_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendation', methods=['GET'])
def get_recommendation():
    try:
        # Use the agent's chat_with_ai method to analyze metrics
        metrics = azure_monitor_agent.get_metrics()
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
        recommendation = ai_agent.chat_with_ai(prompt)
        return jsonify({'recommendation': recommendation})
    except Exception as e:
        logger.error(f"Error analyzing metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        response = ai_agent.chat_with_ai(message)
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
