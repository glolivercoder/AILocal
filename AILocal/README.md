# AI Development Command Assistant

An AI-powered assistant that specializes in development commands for Flutter, Python, GitHub, Docker, Node.js, JavaScript, and Java. Interact via text or voice commands to get the right terminal commands for your development tasks.

## Features

- **Voice Recognition**: Speak your commands using browser-based speech recognition
- **AI Command Generation**: Powered by Ollama with support for multiple models:
  - Gemma 2 (7B)
  - CodeLlama (7B)
  - Llama 3 (8B)
- **Technology Detection**: Automatically recognizes which technology your request is related to
- **Command History**: Keeps track of your command history for easy reference
- **Command Execution**: Optional ability to execute commands directly (use with caution)
- **Dark Neon Interface**: Modern, developer-friendly UI

## Requirements

- Python 3.9+
- Node.js 16+ (if you want to build frontend from source)
- [Ollama](https://ollama.ai/) installed locally
- Microphone for voice input (optional)
- 8GB+ RAM recommended for running the models

## Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/ai-dev-command-assistant.git
cd ai-dev-command-assistant
```

2. Run the setup script:
```
python scripts/setup.py
```

This will:
- Install required Python packages
- Download the Vosk speech recognition model (if using offline speech recognition)
- Set up the directory structure
- Check for Ollama installation and required models

3. Start the application:
```
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Text Commands**: 
   - Type your request in natural language (e.g., "Create a new Flutter project named my_awesome_app")
   - Press Enter or click the Send button

2. **Voice Commands**:
   - Click the microphone button and speak your request
   - The assistant will automatically process your speech

3. **Filter by Technology**:
   - Click on a technology icon to focus only on commands for that specific technology

4. **Execute Commands**:
   - Enable "Execute commands" checkbox to allow the assistant to run commands directly
   - This is disabled by default for security reasons
   - Always review commands before execution

## Examples

Here are some example commands you can try:

### Flutter
- "Create a new Flutter project"
- "Add the http package to my Flutter project"
- "Run Flutter app on Chrome"

### Python
- "Create a new virtual environment"
- "Install requests and pandas packages"
- "Run my Python script with arguments"

### GitHub
- "Initialize a new Git repository"
- "Commit my changes with message 'Initial commit'"
- "Push my changes to the main branch"

### Docker
- "Build a Docker image from my Dockerfile"
- "Run a Nginx container on port 80"
- "List all running Docker containers"

### Node.js
- "Initialize a new Node.js project"
- "Install Express and MongoDB packages"
- "Run my Node.js application"

### JavaScript
- "Create a new React application"
- "Install development dependencies for my Vue project"
- "Build my Next.js application for production"

### Java
- "Compile my Java application"
- "Run my Spring Boot application"
- "Create a new Maven project"

## Advanced Configuration

### Environment Variables

Create a `.env` file in the root directory to configure optional settings:

```
# API Keys for alternative models (not required for basic functionality)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Optional configuration
DEBUG=true
PORT=5000
```

### Custom Models

To use a different Ollama model, edit the `SUPPORTED_MODELS` dictionary in `app.py`.

## Security Considerations

- The application runs commands locally on your machine
- Always review commands before execution
- The "Execute commands" option is disabled by default
- Unsafe commands (rm -rf /, format, etc.) are automatically blocked

## How It Works

1. **Command Input**: Your request is captured via text or speech
2. **Technology Detection**: The system identifies which technology your request relates to
3. **AI Processing**: The request is sent to the selected AI model with a specialized prompt
4. **Command Generation**: The AI returns the appropriate command(s)
5. **Execution (Optional)**: If enabled, the command can be executed directly
6. **History Storage**: All interactions are saved to the PROMPTS directory for future reference

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License 