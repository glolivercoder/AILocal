import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import subprocess
import threading
from dotenv import load_dotenv

# Import our custom modules
from scripts.web_search import WebSearch, ExternalAPIClient
from scripts.docs_manager import DocsManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
VOSK_MODEL_PATH = os.path.join("models", "vosk_model")
SUPPORTED_MODELS = {
    "gemma": "gemma2:7b",
    "codellama": "codellama:7b",
    "llama3": "llama3:8b"
}
DEFAULT_MODEL = SUPPORTED_MODELS["gemma"]
PROMPTS_DIR = "PROMPTS"

# Initialize our components
web_search = WebSearch()
api_client = ExternalAPIClient()
docs_manager = DocsManager()

# Ensure PROMPTS directory exists
os.makedirs(PROMPTS_DIR, exist_ok=True)

# Helper functions
def save_prompt(user_input, ai_response):
    """Save conversation to the PROMPTS directory"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{PROMPTS_DIR}/prompt_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "user_input": user_input,
            "ai_response": ai_response
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Prompt saved to {filename}")
    return filename

def check_ollama_model(model_name):
    """Check if the specified Ollama model is available"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception as e:
        logger.error(f"Error checking Ollama model: {e}")
        return False

def generate_prompt_for_command(command_text, tech_type=None, use_docs=True, use_web=False):
    """Generate a prompt for the AI model based on the command and technology type"""
    
    # Base prompt
    if tech_type:
        prompt = f"""
        You are an expert in {tech_type} development commands. 
        
        Analyze the following user request and provide the appropriate terminal command(s):
        
        Request: "{command_text}"
        
        If this is a valid {tech_type} operation, provide ONLY the exact command(s) to execute.
        If this is not a valid operation, explain briefly why and suggest an alternative.
        Be precise, concise, and provide commands that work on Windows.
        """
    else:
        prompt = f"""
        You are an expert in development tools for Flutter, Python, GitHub, Docker, Node.js, JavaScript, and Java.
        
        Analyze the following user request and provide the appropriate terminal command(s):
        
        Request: "{command_text}"
        
        First, determine which technology this request relates to.
        Then provide ONLY the exact command(s) to execute for that technology.
        If this is not a valid operation, explain briefly why and suggest an alternative.
        Be precise, concise, and provide commands that work on Windows.
        """
    
    # If we want to use documentation, add it to the prompt
    if use_docs and tech_type:
        docs_results = docs_manager.search_docs(tech_type.lower(), command_text, max_results=2)
        if docs_results:
            prompt += "\n\nRelevant documentation information:\n"
            for i, result in enumerate(docs_results):
                prompt += f"\nFrom {result['title']}:\n{result['context']}\n"
    
    # If we want to use web search, add it to the prompt
    if use_web:
        search_term = f"{tech_type if tech_type else ''} {command_text} command line example"
        search_results = web_search.search(search_term, num_results=2)
        
        if search_results and search_results.get('results'):
            prompt += "\n\nRelevant web search information:\n"
            for i, result in enumerate(search_results['results']):
                prompt += f"\nFrom {result['title']} ({result['url']}):\n{result['summary']}\n"
    
    return prompt.strip()

def get_technology_from_command(command_text):
    """Detect which technology the command is related to"""
    command_lower = command_text.lower()
    
    if any(term in command_lower for term in ["flutter", "dart", "pub", "flutter pub"]):
        return "Flutter"
    elif any(term in command_lower for term in ["python", "pip", "venv", "django", "flask"]):
        return "Python"
    elif any(term in command_lower for term in ["git", "github", "commit", "push", "pull", "clone"]):
        return "GitHub"
    elif any(term in command_lower for term in ["docker", "container", "image", "compose"]):
        return "Docker"
    elif any(term in command_lower for term in ["node", "npm", "yarn", "package.json"]):
        return "Node.js"
    elif any(term in command_lower for term in ["javascript", "js", "react", "vue", "angular"]):
        return "JavaScript"
    elif any(term in command_lower for term in ["java", "maven", "gradle", "spring"]):
        return "Java"
    else:
        return None

def query_ollama(model_name, prompt):
    """Query the Ollama model with the given prompt"""
    try:
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],
            capture_output=True,
            text=True,
            timeout=30  # Set a timeout for the command
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "The model took too long to respond. Please try a simpler request."
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return f"Error: {str(e)}"

def process_with_external_api(command_text, technology, api_name, openrouter_model=None):
    """Process the command using an external API"""
    system_message = f"You are an expert in {technology if technology else 'software development'} commands for Windows systems. Provide clear, concise commands."
    prompt = generate_prompt_for_command(command_text, technology, use_docs=True, use_web=True)
    
    return api_client.call_external_api(api_name, prompt, system_message, openrouter_model)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    vosk_available = os.path.exists(VOSK_MODEL_PATH)
    
    # Check Ollama models
    model_status = {}
    for key, model in SUPPORTED_MODELS.items():
        model_status[key] = check_ollama_model(model)
    
    # Check documentation status
    docs_status = docs_manager.get_docs_status()
    
    # Check API status
    api_status = {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'gemini': bool(os.getenv('GEMINI_API_KEY')),
        'openrouter': bool(os.getenv('OPENROUTER_API_KEY')),
        'deepseek': bool(os.getenv('DEEPSEEK_API_KEY')),
        'grok': bool(os.getenv('GROK_API_KEY'))
    }
    
    return jsonify({
        'vosk_available': vosk_available,
        'models': model_status,
        'docs': {k: v['downloaded'] for k, v in docs_status.items()},
        'apis': api_status
    })

@app.route('/api/process_command', methods=['POST'])
def process_command():
    data = request.json
    command_text = data.get('command', '')
    model_name = data.get('model', DEFAULT_MODEL)
    use_web = data.get('use_web', False)
    use_docs = data.get('use_docs', True)
    openrouter_model = data.get('openrouter_model')
    
    if not command_text:
        return jsonify({'error': 'Empty command'}), 400
    
    # Detect technology 
    technology = data.get('technology') or get_technology_from_command(command_text)
    
    # Check if this is a request to use an external API
    external_apis = ['openai', 'gemini', 'openrouter', 'deepseek', 'grok']
    if model_name in external_apis:
        ai_response = process_with_external_api(command_text, technology, model_name, openrouter_model)
    else:
        # Generate prompt with optional documentation and web search
        prompt = generate_prompt_for_command(command_text, technology, use_docs, use_web)
        
        # Query the AI model
        ai_response = query_ollama(model_name, prompt)
    
    # Save the conversation
    save_prompt(command_text, ai_response)
    
    return jsonify({
        'technology': technology,
        'original_command': command_text,
        'ai_response': ai_response,
        'model_used': model_name
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    prompts = []
    for filename in os.listdir(PROMPTS_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(PROMPTS_DIR, filename), 'r', encoding='utf-8') as f:
                    prompts.append(json.load(f))
            except Exception as e:
                logger.error(f"Error loading prompt file {filename}: {e}")
    
    # Sort by timestamp
    prompts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify(prompts)

@app.route('/api/web_search', methods=['POST'])
def web_search_route():
    data = request.json
    query = data.get('query', '')
    num_results = int(data.get('num_results', 5))
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    results = web_search.search(query, num_results=num_results)
    return jsonify(results)

@app.route('/api/docs/status', methods=['GET'])
def docs_status():
    status = docs_manager.get_docs_status()
    return jsonify(status)

@app.route('/api/docs/download', methods=['POST'])
def download_docs():
    data = request.json
    technology = data.get('technology')
    
    if not technology:
        # Download all if no specific technology is specified
        def download_all_background():
            docs_manager.download_all_docs()
        
        thread = threading.Thread(target=download_all_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Started downloading all documentation in the background'})
    else:
        # Download specific technology
        success = docs_manager.download_docs(technology.lower())
        return jsonify({'success': success})

@app.route('/api/docs/search', methods=['POST'])
def search_docs():
    data = request.json
    technology = data.get('technology')
    query = data.get('query', '')
    max_results = int(data.get('max_results', 5))
    
    if not technology or not query:
        return jsonify({'error': 'Technology and query are required'}), 400
    
    results = docs_manager.search_docs(technology.lower(), query, max_results=max_results)
    return jsonify(results)

if __name__ == '__main__':
    # Check if Ollama is installed
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        logger.info("Ollama available, checking models...")
        
        # Check if required models are available
        for model_name in SUPPORTED_MODELS.values():
            if model_name not in result.stdout:
                logger.warning(f"Model {model_name} not found. You may need to run: ollama pull {model_name}")
    except Exception as e:
        logger.error(f"Ollama not available: {e}")
        logger.info("Please install Ollama from https://ollama.ai/")
    
    # Start the server
    app.run(debug=True) 