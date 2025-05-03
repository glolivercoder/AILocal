# NeoVoice AI Assistant - Extensão para Python

Esta extensão do NeoVoice AI Assistant adiciona suporte especializado para criação de scripts Python, com opção de alternar entre modelos locais e APIs externas para maior poder computacional.

## Índice

- [Integração com CodeLlama](#integração-com-codellama)
- [Seleção de Modelos](#seleção-de-modelos)
- [Template para Python](#template-para-python)
- [Integração com APIs Externas](#integração-com-apis-externas)
- [Configuração](#configuração)

## Integração com CodeLlama

O CodeLlama é um modelo especializado em código, treinado especificamente para entender e gerar código de programação de alta qualidade. A integração com Ollama permite executá-lo localmente.

```python
# Adicionar ao app.py
CODELLAMA_MODEL_NAME = "codellama:7b-q4_K_M"

def check_codellama():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return CODELLAMA_MODEL_NAME in result.stdout
    except Exception as e:
        logger.error(f"Erro ao verificar CodeLlama: {e}")
        return False
```

## Seleção de Modelos

Adicione um dropdown para selecionar entre diferentes modelos de IA:

```html
<!-- Adicionar ao index.html na seção de status -->
<div class="mb-8 p-4 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20">
    <h2 class="text-xl font-semibold mb-3 text-blue-400">Modelo de IA</h2>
    <select id="model-selector" class="w-full p-2 bg-gray-700 text-blue-100 rounded-lg border border-blue-500 focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50">
        <option value="gemma2:7b">Gemma 2 (7B) - Uso geral</option>
        <option value="codellama:7b-q4_K_M">CodeLlama (7B) - Especialista em código</option>
        <option value="llama3:8b">Llama 3 (8B) - Balanceado</option>
        <option value="openrouter">OpenRouter API (Externo)</option>
        <option value="deepseek">DeepSeek API (Externo)</option>
        <option value="gemini">Gemini API (Externo)</option>
        <option value="grok">Grok API (Externo)</option>
    </select>
</div>
```

```javascript
// Adicionar ao main.js
const modelSelector = document.getElementById('model-selector');

modelSelector.addEventListener('change', function() {
    localStorage.setItem('selectedModel', this.value);
    updateModelStatus();
});

// Carregar modelo salvo
if (localStorage.getItem('selectedModel')) {
    modelSelector.value = localStorage.getItem('selectedModel');
}

function updateModelStatus() {
    const selectedModel = modelSelector.value;
    
    // Atualizar interface baseado no modelo selecionado
    if (selectedModel.includes('openrouter') || 
        selectedModel.includes('deepseek') || 
        selectedModel.includes('gemini') || 
        selectedModel.includes('grok')) {
        document.getElementById('api-key-section').classList.remove('hidden');
    } else {
        document.getElementById('api-key-section').classList.add('hidden');
    }
}
```

## Template para Python

Crie um template especializado para Python usando o Modelfile:

```bash
# Criar arquivo Modelfile
cat > Modelfile << 'EOF'
FROM codellama:7b-q4_K_M
SYSTEM """
Você é um assistente especializado em criar scripts Python eficientes e bem documentados.
Sempre inclua:
1. Comentários explicativos
2. Tratamento de erros
3. Boas práticas PEP8
4. Docstrings para funções
"""
EOF

# Criar modelo personalizado
ollama create python-helper -f Modelfile
```

## Integração com APIs Externas

Adicione suporte para APIs externas quando precisar de mais poder computacional:

```python
# Adicionar ao app.py
import requests
from dotenv import load_dotenv
load_dotenv()  # Carregar API keys do arquivo .env

# Configurações de APIs
API_KEYS = {
    'openrouter': os.getenv('OPENROUTER_API_KEY'),
    'deepseek': os.getenv('DEEPSEEK_API_KEY'),
    'gemini': os.getenv('GEMINI_API_KEY'),
    'grok': os.getenv('GROK_API_KEY')
}

API_ENDPOINTS = {
    'openrouter': 'https://openrouter.ai/api/v1/chat/completions',
    'deepseek': 'https://api.deepseek.com/v1/chat/completions',
    'gemini': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
    'grok': 'https://api.grok.ai/v1/chat/completions'
}

# Nova rota para processar comandos com modelo selecionado
@app.route('/api/process_command_with_model', methods=['POST'])
def process_command_with_model():
    data = request.json
    command_text = data.get('command', '')
    selected_model = data.get('model', 'gemma2:7b')
    
    if not command_text:
        return jsonify({'error': 'Comando vazio'}), 400
    
    # Prompt para Python
    python_prompt = f"""
    Crie um script Python para a seguinte tarefa:
    {command_text}
    
    Inclua comentários explicativos, tratamento de erros, e siga as boas práticas PEP8.
    """
    
    try:
        # Verificar se é um modelo local ou API externa
        if selected_model in API_KEYS and API_KEYS[selected_model]:
            # Usar API externa
            response = call_external_api(selected_model, python_prompt)
        else:
            # Usar modelo local com Ollama
            model_name = "python-helper" if selected_model == "codellama:7b-q4_K_M" else selected_model
            response = call_local_model(model_name, python_prompt)
            
        return jsonify({
            'original_command': command_text,
            'ai_response': response,
            'model_used': selected_model
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar comando: {e}")
        return jsonify({'error': str(e)}), 500

def call_external_api(api_name, prompt):
    """Chamar API externa com o prompt"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEYS[api_name]}'
    }
    
    # Adaptar o formato do payload para cada API
    if api_name == 'gemini':
        payload = {
            'contents': [{'parts': [{'text': prompt}]}]
        }
    else:
        payload = {
            'model': 'claude-3-opus-20240229' if api_name == 'openrouter' else 'deepseek-coder' if api_name == 'deepseek' else 'grok-1',
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3
        }
    
    response = requests.post(API_ENDPOINTS[api_name], headers=headers, json=payload)
    response.raise_for_status()
    
    # Extrair resposta de acordo com o formato de cada API
    if api_name == 'gemini':
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return response.json()['choices'][0]['message']['content']

def call_local_model(model_name, prompt):
    """Chamar modelo local via Ollama"""
    result = subprocess.run(
        ["ollama", "run", model_name, prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto para armazenar suas chaves de API:

```
OPENROUTER_API_KEY=sua_chave_aqui
DEEPSEEK_API_KEY=sua_chave_aqui
GEMINI_API_KEY=sua_chave_aqui
GROK_API_KEY=sua_chave_aqui
```

2. Adicione a seção de configuração de API à interface:

```html
<!-- Adicionar ao index.html -->
<div id="api-key-section" class="mb-8 p-4 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20 hidden">
    <h2 class="text-xl font-semibold mb-3 text-blue-400">Configuração de API</h2>
    <div class="space-y-3">
        <div>
            <label class="block text-blue-300 mb-1">Chave de API</label>
            <input type="password" id="api-key-input" class="w-full p-2 bg-gray-700 text-blue-100 rounded-lg border border-blue-500">
        </div>
        <button id="save-api-key" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-all duration-300">
            Salvar Chave
        </button>
    </div>
</div>
```

Esta configuração permite alternar facilmente entre modelos locais para tarefas mais simples e APIs externas mais poderosas quando necessário para scripts Python mais complexos.
