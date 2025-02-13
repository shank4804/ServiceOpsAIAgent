# ServiceOps AI Agent

An AI-powered monitoring and management system for Azure cloud infrastructure. This system uses OpenAI's GPT-4 to analyze metrics, provide insights, and assist in infrastructure management through natural language interaction.

## Features

- Real-time monitoring of Azure infrastructure metrics
- AI-powered analysis and recommendations
- Interactive chat interface for infrastructure management
- Beautiful dashboard with metric visualizations
- Proactive issue detection and alerting

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-4
- **Monitoring**: Azure Monitor
- **UI Framework**: Bootstrap 5

## Setup

1. Clone the repository:
```bash
git clone https://github.com/shank4804/ServiceOpsAIAgent.git
cd ServiceOpsAIAgent
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with:
```
API_URL=http://localhost:3000
OPENAI_API_KEY=your_openai_api_key
POLLING_INTERVAL=300
```

4. Start the backend server:
```bash
python api.py
```

5. Start the frontend server:
```bash
cd ../frontend
python -m http.server 8000
```

You can now access the application at:
- Frontend: http://localhost:8000
- Backend API: http://localhost:3000

## Usage

1. The dashboard shows real-time metrics and system health
2. Use the chat interface to:
   - Query system status
   - Get performance insights
   - Request recommendations
   - Investigate potential issues

## Development

- The backend runs on Flask and serves the API endpoints
- The frontend is a static web application that communicates with the backend API
- CORS is enabled to allow frontend-backend communication
- The application uses OpenAI's GPT-4 for intelligent analysis and recommendations
- Azure Monitor integration provides real-time infrastructure metrics

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
