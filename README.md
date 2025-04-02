# GenAI Application

A modern, containerized GenAI application that combines Ollama, FastAPI, and Chainlit to create an intelligent chat interface with document retrieval capabilities.

## Architecture

The application is built with a three-tier architecture:

1. **Backend (Ollama)**
   - Runs the Mistral model
   - Handles LLM inference
   - Exposed on port 11434

2. **Middleware (FastAPI)**
   - Acts as a proxy between frontend and backend
   - Handles request/response formatting
   - Exposed on port 8001

3. **Frontend (Chainlit)**
   - Provides a modern chat interface
   - Integrates with ChromaDB for document retrieval
   - Exposed on port 8000

## Features

- 🤖 Powered by Mistral model
- 📚 Document retrieval using ChromaDB
- 💬 Modern chat interface with Chainlit
- 🔄 Real-time streaming responses
- 🐳 Fully containerized with Docker
- 🔍 Semantic search capabilities
- 📊 Health checks and automatic recovery

## Prerequisites

- Docker and Docker Compose
- At least 8GB of RAM (16GB recommended)
- 2GB of free disk space

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd GenAI
```

2. Start the application:
```bash
docker-compose up -d
```

3. Access the application:
- Chainlit: http://localhost:8000
- Middleware API: http://localhost:8001
- Ollama API: http://localhost:11434

## Project Structure

```
GenAI/
├── backend/
│   ├── Dockerfile
│   └── start.sh
├── frontend/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── chroma_db/
├── middleware/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── docker-compose.yaml
```

## Components

### Backend (Ollama)

- Uses the official Ollama image
- Runs Mistral model
- Handles LLM inference requests
- Persists model data using Docker volumes

### Middleware (FastAPI)

- Proxies requests between frontend and backend
- Handles message formatting
- Provides error handling and logging
- Implements health checks

### Frontend (Chainlit)

- Modern chat interface
- Integrates with ChromaDB for document retrieval
- Uses sentence-transformers for embeddings
- Implements streaming responses

## Development

### Building from Source

1. Build individual components:
```bash
docker-compose build
```

2. Start in development mode:
```bash
docker-compose up
```

### Adding Documents to ChromaDB

1. Place your text documents in the `frontend/data` directory
2. Run the ChromaDB creation notebook:
```bash
jupyter notebook frontend/create_chroma.ipynb
```

## API Endpoints

### Middleware API

- `GET /`: Health check endpoint
- `POST /api/chat`: Chat completion endpoint

### Ollama API

- `POST /api/chat`: Direct access to Ollama chat completions

## Environment Variables

- `BACKEND_URL`: URL of the Ollama backend (default: http://backend:11434)
- `OLLAMA_HOST`: Ollama host URL for frontend (default: http://backend:11434)

## Monitoring

The application includes health checks for all services:
- Backend: Checks Ollama API availability
- Middleware: Monitors FastAPI endpoints
- Frontend: Verifies Chainlit server status

## Troubleshooting

1. Check service logs:
```bash
docker-compose logs -f [service_name]
```

2. Verify service health:
```bash
docker-compose ps
```

3. Restart services:
```bash
docker-compose restart [service_name]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- [Ollama](https://ollama.ai/) for the LLM backend
- [Chainlit](https://chainlit.io/) for the chat interface
- [ChromaDB](https://www.chromadb.com/) for vector storage
- [FastAPI](https://fastapi.tiangolo.com/) for the API middleware 