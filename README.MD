# CodeLens: AI-Powered Source Code Documentation Generator

CodeLens is an intelligent documentation tool that uses AI to analyze codebases and generate comprehensive documentation. It helps developers understand complex projects quickly by automatically analyzing code structure, dependencies, business logic, and architecture.

![CodeLens Logo](docs/images/codelens-logo.png)

## Features

- **GitHub Integration**: Clone repositories directly from GitHub URLs
- **Multi-Language Support**: Analyzes code across various programming languages
- **AI-Powered Analysis**: Uses OpenAI or Ollama models for deep code understanding
- **Comprehensive Analysis**: Generates insights on code, dependencies, business logic, and architecture
- **Interactive Visualizations**: View dependency graphs, architecture diagrams, and more
- **Microservices Architecture**: Scalable and maintainable system design

## Architecture

CodeLens is built on a microservices architecture with the following components:

- **API Gateway Service**: Routes requests and handles API documentation
- **Source Code Service**: Manages code retrieval and analysis
- **Web UI**: Provides a user-friendly interface for interacting with the system

![Architecture Diagram](docs/images/architecture-diagram.png)

## Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for development)
- Python 3.11+ (for development)
- Either an OpenAI API key or Ollama running locally

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/codelens.git
   cd codelens
   ```

2. Configure environment variables:
   ```bash
   # For OpenAI integration
   export OPENAI_API_KEY=your-api-key
   
   # Or for Ollama (local models)
   # Ensure Ollama is running locally
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Web UI: http://localhost:3000
   - API: http://localhost:8080/api
   - API Documentation: http://localhost:8080/api-docs

### Manual Setup for Development

1. Start the API Gateway Service:
   ```bash
   cd services/api-gateway
   npm install
   npm run dev
   ```

2. Start the Source Code Service:
   ```bash
   cd services/source-code-service
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Start the Web UI:
   ```bash
   cd services/web-ui
   npm install
   npm run dev
   ```

## Using CodeLens

### Analyzing a GitHub Repository

1. Navigate to the web UI
2. Enter a GitHub repository URL in the Repository Cloning form
3. Click "Clone Repository"
4. Once cloning is complete, click "Analyze"
5. Select the types of analysis you want to perform
6. View the results in the analysis dashboard

### Uploading Code Files

1. Navigate to the Projects page
2. Click "Upload Files"
3. Select your source code files or upload a ZIP archive
4. Name your project and submit
5. Start an analysis on the uploaded files

## API Reference

CodeLens provides a RESTful API for programmatic access:

### GitHub Integration

- `POST /api/v1/source-code/github/repositories` - Clone a GitHub repository
- `GET /api/v1/source-code/github/repositories/{repository_id}` - Get repository information
- `GET /api/v1/source-code/github/repositories` - List all repositories

### File Management

- `POST /api/v1/source-code/files/upload` - Upload files for analysis
- `GET /api/v1/source-code/files/projects/{project_id}` - Get project information
- `GET /api/v1/source-code/files/projects/{project_id}/files` - List project files

### Analysis

- `POST /api/v1/source-code/analysis/projects/{project_id}/analyze` - Start analysis
- `GET /api/v1/source-code/analysis/analysis/{analysis_id}` - Get analysis status
- `GET /api/v1/source-code/analysis/analysis/{analysis_id}/results` - Get analysis results

For a complete API reference, see the [API Documentation](http://localhost:8080/api-docs) when the service is running.

## Configuration

Configuration is handled through environment variables:

### API Gateway

- `PORT` - Port number (default: 8080)
- `SOURCE_CODE_SERVICE_URL` - URL of the Source Code Service

### Source Code Service

- `LOG_LEVEL` - Logging level (default: INFO)
- `CLONE_BASE_PATH` - Path for cloned repositories
- `FILES_BASE_PATH` - Path for uploaded files
- `DB_PATH` - Path for database files
- `ANALYSIS_RESULTS_PATH` - Path for analysis results
- `OPENAI_API_KEY` - OpenAI API key
- `LLM_PROVIDER` - AI provider to use ("openai" or "ollama")
- `OLLAMA_API_BASE` - Ollama API base URL
- `OLLAMA_MODEL` - Ollama model to use

## Development

### Project Structure

```
codelens/
├── services/
│   ├── api-gateway/      # API Gateway service (Node.js/Express)
│   ├── source-code-service/ # Source Code service (Python/FastAPI)
│   └── web-ui/           # Web UI (React)
├── data/                 # Persistent data storage
├── docs/                 # Documentation
└── docker-compose.yml    # Docker Compose configuration
```

### Adding New Analysis Types

To add a new analysis type:

1. Define the analysis logic in `services/source-code-service/app/services/analysis_service.py`
2. Add the new analysis type to the models in `services/source-code-service/app/models/analysis.py`
3. Update the API endpoints in `services/source-code-service/app/routers/analysis.py`
4. Create visualization components in the web UI

### Running Tests

```bash
# API Gateway tests
cd services/api-gateway
npm test

# Source Code Service tests
cd services/source-code-service
pytest

# Web UI tests
cd services/web-ui
npm test
```

## Troubleshooting

### Common Issues

- **"Connection refused" errors**: Ensure all services are running and the Docker network is functioning correctly.
- **Analysis progress stuck at 0%**: Check the source-code-service logs for errors.
- **Repository cloning fails**: Verify the GitHub URL is correct and accessible.
- **"API key not defined" error**: Ensure the OPENAI_API_KEY environment variable is set if using OpenAI.

### Logs

To view logs for debugging:

```bash
# View all logs
docker-compose logs

# View logs for a specific service
docker-compose logs -f source-code-service
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for their powerful language models
- [Ollama](https://ollama.ai/) for local LLM support
- All contributors and supporters of the project