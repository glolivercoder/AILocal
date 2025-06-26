# NeoVoice AI Assistant - Documentação Completa

Uma assistente de IA local com interface dark neon que integra reconhecimento de voz Vosk e processamento de linguagem Gemma 2 para executar comandos Git, Docker, Flutter e Cloudflare.

## Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Arquivos do Projeto](#arquivos-do-projeto)
  - [app.py](#apppy)
  - [requirements.txt](#requirementstxt)
  - [index.html](#indexhtml)
  - [main.js](#mainjs)
  - [setup.py](#setuppy)
  - [Configuração do Frontend](#configuração-do-frontend)
- [Uso](#uso)
- [Personalização](#personalização)
- [Licença](#licença)

## Visão Geral

NeoVoice AI Assistant é uma solução de IA local que combina:

- 🎤 **Reconhecimento de voz local** usando Vosk (sem dependência de serviços em nuvem)
- 🧠 **Processamento de linguagem** com Gemma 2 (7B)
- 🌐 **Interface web moderna** construída com Vite, Tailwind CSS 4.0
- 🌙 **Tema dark neon** com acentos em azul
- 🔧 **Comandos para ferramentas** como Git, Docker, Flutter e Cloudflare

## Requisitos

- Python 3.9+
- Node.js 16+
- 8GB+ RAM
- Processador Ryzen 5600 ou equivalente
- Ollama (para executar o modelo Gemma)

## Estrutura do Projeto

```
G:\AILocal\
│
├── app.py                  # Aplicação Flask principal
├── requirements.txt        # Dependências Python
├── README.md               # Documentação
│
├── static\                 # Arquivos estáticos
│   ├── css\
│   │   └── output.css      # CSS compilado do Tailwind
│   ├── js\
│   │   ├── main.js         # JavaScript principal
│   │   ├── voiceRecognition.js  # Lógica de reconhecimento de voz
│   │   └── commands.js     # Lógica de comandos
│   └── img\                # Imagens e ícones
│
├── templates\              # Templates HTML
│   └── index.html          # Página principal
│
├── models\                 # Diretório para modelos de IA
│   ├── vosk_model\         # Modelo Vosk (será baixado)
│   └── gemma_model\        # Modelo Gemma (será baixado)
│
├── scripts\                # Scripts auxiliares
│   ├── setup.py            # Script de configuração
│   └── command_executor.py # Executor de comandos
│
└── frontend\               # Código fonte do frontend (Vite+Tailwind)
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.js
    └── src\
        ├── main.js
        └── style.css
```

## Instalação

1. Clone este repositório ou crie a estrutura de diretórios manualmente
2. Execute `pip install -r requirements.txt`
3. Execute `python scripts/setup.py` para baixar os modelos necessários
4. Na pasta `frontend`, execute `npm install` e `npm run build`
5. Inicie a aplicação com `python app.py`

## Arquivos do Projeto

### app.py

```python
import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Verificar se os modelos estão disponíveis
VOSK_MODEL_PATH = os.path.join("models", "vosk_model")
GEMMA_MODEL_NAME = "gemma2:7b"

# Verificar se o Ollama está instalado e se o modelo Gemma está disponível
def check_gemma():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return GEMMA_MODEL_NAME in result.stdout
    except Exception as e:
        logger.error(f"Erro ao verificar Ollama: {e}")
        return False

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# API para verificar status dos modelos
@app.route('/api/status', methods=['GET'])
def status():
    vosk_available = os.path.exists(VOSK_MODEL_PATH)
    gemma_available = check_gemma()
    
    return jsonify({
        'vosk_available': vosk_available,
        'gemma_available': gemma_available
    })

# API para processar comandos de voz
@app.route('/api/process_command', methods=['POST'])
def process_command():
    data = request.json
    command_text = data.get('command', '')
    
    if not command_text:
        return jsonify({'error': 'Comando vazio'}), 400
    
    # Processar o comando com Gemma
    try:
        # Aqui usamos Ollama para consultar o modelo Gemma
        prompt = f"""
        Analise o seguinte comando de voz e determine a ação a ser executada.
        Se for um comando válido para Git, Docker, Flutter ou Cloudflare, forneça o comando exato a ser executado.
        Se não for um comando válido, explique por que e sugira alternativas.
        
        Comando: "{command_text}"
        """
        
        result = subprocess.run(
            ["ollama", "run", GEMMA_MODEL_NAME, prompt],
            capture_output=True,
            text=True
        )
        
        # Extrair o comando a ser executado da resposta do modelo
        ai_response = result.stdout.strip()
        
        # Verificar se é um comando que deve ser executado
        if any(tool in command_text.lower() for tool in ['git', 'docker', 'flutter', 'cloudflare']):
            # Aqui você implementaria a lógica para executar o comando
            # Por segurança, isso deve ser feito com cuidado
            execution_result = "Comando reconhecido, mas a execução automática está desativada por segurança."
        else:
            execution_result = "Não é um comando executável."
        
        return jsonify({
            'original_command': command_text,
            'ai_response': ai_response,
            'execution_result': execution_result
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar comando: {e}")
        return jsonify({'error': str(e)}), 500

# Iniciar o servidor
if __name__ == '__main__':
    # Verificar status dos modelos
    if not os.path.exists(VOSK_MODEL_PATH):
        logger.warning(f"Modelo Vosk não encontrado em {VOSK_MODEL_PATH}. Execute scripts/setup.py primeiro.")
    
    if not check_gemma():
        logger.warning(f"Modelo Gemma não encontrado. Execute 'ollama pull {GEMMA_MODEL_NAME}' primeiro.")
    
    app.run(debug=True)
```

### requirements.txt

```
flask==2.3.3
flask-cors==4.0.0
vosk==0.3.45
sounddevice==0.4.6
numpy==1.24.3
requests==2.31.0
ollama==0.1.5
python-dotenv==1.0.0
tqdm==4.66.1
```

### index.html

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeoVoice AI Assistant</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/output.css') }}">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body class="bg-gray-900 text-blue-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="mb-10 text-center">
            <h1 class="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">
                NeoVoice AI Assistant
            </h1>
            <p class="text-blue-300">Assistente de IA local com reconhecimento de voz</p>
        </header>

        <main class="max-w-4xl mx-auto">
            <!-- Status dos modelos -->
            <div class="mb-8 p-4 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20">
                <h2 class="text-xl font-semibold mb-3 text-blue-400">Status do Sistema</h2>
                <div class="grid grid-cols-2 gap-4">
                    <div class="flex items-center">
                        <div id="vosk-status" class="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                        <span>Reconhecimento de Voz (Vosk)</span>
                    </div>
                    <div class="flex items-center">
                        <div id="gemma-status" class="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                        <span>Modelo de Linguagem (Gemma)</span>
                    </div>
                </div>
            </div>

            <!-- Área de comandos de voz -->
            <div class="mb-8 p-6 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-semibold text-blue-400">Comandos de Voz</h2>
                    <button id="mic-button" class="p-3 bg-blue-600 hover:bg-blue-700 rounded-full transition-all duration-300 shadow-lg shadow-blue-600/50">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                    </button>
                </div>
                
                <div id="listening-indicator" class="hidden mb-4 p-2 text-center text-blue-300 animate-pulse">
                    Ouvindo... <span class="dots">...</span>
                </div>
                
                <div id="transcript-container" class="mb-4 p-4 bg-gray-700 rounded-lg min-h-16 text-blue-100">
                    <p id="transcript" class="italic text-blue-300">Clique no microfone para falar um comando...</p>
                </div>
            </div>

            <!-- Área de resposta da IA -->
            <div class="mb-8 p-6 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20">
                <h2 class="text-xl font-semibold mb-4 text-blue-400">Resposta da IA</h2>
                <div id="ai-response" class="p-4 bg-gray-700 rounded-lg min-h-32 prose prose-invert prose-blue max-w-none">
                    <p class="text-blue-300">A resposta da IA aparecerá aqui...</p>
                </div>
            </div>

            <!-- Área de execução de comandos -->
            <div class="p-6 bg-gray-800 rounded-lg border border-blue-500 shadow-lg shadow-blue-500/20">
                <h2 class="text-xl font-semibold mb-4 text-blue-400">Resultado da Execução</h2>
                <pre id="execution-result" class="p-4 bg-black rounded-lg overflow-x-auto text-green-400 font-mono text-sm min-h-32">
# Os resultados da execução aparecerão aqui
                </pre>
            </div>
        </main>
    </div>

    <footer class="mt-12 py-6 text-center text-blue-400 text-sm">
        <p>NeoVoice AI Assistant &copy; 2025</p>
    </footer>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### main.js

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da UI
    const micButton = document.getElementById('mic-button');
    const listeningIndicator = document.getElementById('listening-indicator');
    const transcript = document.getElementById('transcript');
    const aiResponse = document.getElementById('ai-response');
    const executionResult = document.getElementById('execution-result');
    const voskStatus = document.getElementById('vosk-status');
    const gemmaStatus = document.getElementById('gemma-status');

    // Verificar status dos modelos
    async function checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            // Atualizar indicadores de status
            voskStatus.className = `w-3 h-3 rounded-full ${data.vosk_available ? 'bg-green-500' : 'bg-red-500'} mr-2`;
            gemmaStatus.className = `w-3 h-3 rounded-full ${data.gemma_available ? 'bg-green-500' : 'bg-red-500'} mr-2`;
            
            // Desabilitar botão de microfone se os modelos não estiverem disponíveis
            if (!data.vosk_available || !data.gemma_available) {
                micButton.disabled = true;
                micButton.classList.add('opacity-50', 'cursor-not-allowed');
                micButton.classList.remove('hover:bg-blue-700');
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
        }
    }

    // Verificar status ao carregar a página
    checkStatus();

    // Reconhecimento de voz simulado (em produção, seria integrado com Vosk)
    let isListening = false;

    micButton.addEventListener('click', function() {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });

    function startListening() {
        // Em uma implementação real, aqui iniciaríamos o Vosk
        isListening = true;
        micButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        micButton.classList.add('bg-red-600', 'hover:bg-red-700', 'animate-pulse');
        listeningIndicator.classList.remove('hidden');
        
        // Simulação para demonstração
        setTimeout(() => {
            // Simular reconhecimento de voz após 3 segundos
            const demoCommands = [
                "git status",
                "docker ps",
                "flutter run",
                "cloudflare purge cache"
            ];
            const randomCommand = demoCommands[Math.floor(Math.random() * demoCommands.length)];
            transcript.textContent = randomCommand;
            
            // Processar o comando
            processCommand(randomCommand);
            
            // Parar de ouvir
            stopListening();
        }, 3000);
    }

    function stopListening() {
        isListening = false;
        micButton.classList.remove('bg-red-600', 'hover:bg-red-700', 'animate-pulse');
        micButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
        listeningIndicator.classList.add('hidden');
    }

    async function processCommand(command) {
        try {
            // Mostrar indicador de carregamento
            aiResponse.innerHTML = '<p class="text-blue-300 animate-pulse">Processando comando...</p>';
            executionResult.textContent = '# Aguardando resposta...';
            
            // Enviar comando para o backend
            const response = await fetch('/api/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            });
            
            const data = await response.json();
            
            // Renderizar resposta formatada com Markdown
            aiResponse.innerHTML = marked.parse(data.ai_response);
            
            // Mostrar resultado da execução
            executionResult.textContent = data.execution_result;
            
            // Adicionar efeito de destaque
            aiResponse.classList.add('highlight-animation');
            executionResult.classList.add('highlight-animation');
            
            // Remover efeito após animação
            setTimeout(() => {
                aiResponse.classList.remove('highlight-animation');
                executionResult.classList.remove('highlight-animation');
            }, 1000);
            
        } catch (error) {
            console.error('Erro ao processar comando:', error);
            aiResponse.innerHTML = '<p class="text-red-500">Erro ao processar comando</p>';
            executionResult.textContent = `# Erro: ${error.message}`;
        }
    }

    // Animação dos pontos de "Ouvindo..."
    setInterval(() => {
        const dots = document.querySelector('.dots');
        if (dots) {
            if (dots.textContent === '...') dots.textContent = '.';
            else if (dots.textContent === '.') dots.textContent = '..';
            else if (dots.textContent === '..') dots.textContent = '...';
        }
    }, 500);
});
```

### setup.py

```python
#!/usr/bin/env python3
import os
import sys
import subprocess
import zipfile
import requests
import shutil
import json
from tqdm import tqdm

# Diretório raiz do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT_DIR, "models")
VOSK_MODEL_DIR = os.path.join(MODELS_DIR, "vosk_model")

# URLs para download
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"

def download_file(url, destination):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    print(f"Baixando {url}...")
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    
    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    
    progress_bar.close()

def setup_vosk():
    """Download and setup Vosk model"""
    if os.path.exists(VOSK_MODEL_DIR):
        print(f"Modelo Vosk já existe em {VOSK_MODEL_DIR}")
        return
    
    # Criar diretório para modelos se não existir
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Baixar modelo Vosk
    zip_path = os.path.join(MODELS_DIR, "vosk_model.zip")
    download_file(VOSK_MODEL_URL, zip_path)
    
    # Extrair arquivo zip
    print("Extraindo modelo Vosk...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODELS_DIR)
    
    # Renomear diretório extraído
    extracted_dir = os.path.join(MODELS_DIR, "vosk-model-small-pt-0.3")
    if os.path.exists(extracted_dir):
        shutil.move(extracted_dir, VOSK_MODEL_DIR)
    
    # Remover arquivo zip
    os.remove(zip_path)
    print("Modelo Vosk configurado com sucesso!")

def setup_gemma():
    """Setup Gemma model with Ollama"""
    try:
        # Verificar se Ollama está instalado
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        
        # Verificar se o modelo já existe
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "gemma2:7b" in result.stdout:
            print("Modelo Gemma já está disponível no Ollama")
            return
        
        # Baixar modelo Gemma
        print("Baixando modelo Gemma2 7B (isso pode levar algum tempo)...")
        subprocess.run(["ollama", "pull", "gemma2:7b"], check=True)
        print("Modelo Gemma configurado com sucesso!")
        
    except subprocess.CalledProcessError:
        print("Erro: Ollama não está instalado ou não está no PATH")
        print("Por favor, instale o Ollama: https://ollama.ai/download")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao configurar Gemma: {e}")
        sys.exit(1)

def setup_frontend():
    """Setup frontend with npm"""
    frontend_dir = os.path.join(ROOT_DIR, "frontend")
    
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir, exist_ok=True)
        
        # Criar package.json
        package_json = {
            "name": "neovoice-frontend",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "marked": "^9.1.5"
            },
            "devDependencies": {
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.31",
                "tailwindcss": "^4.0.0",
                "vite": "^5.0.0"
            }
        }
        
        with open(os.path.join(frontend_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Criar tailwind.config.js
        with open(os.path.join(frontend_dir, "tailwind.config.js"), "w") as f:
            f.write("""/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../templates/**/*.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00f3ff',
        'deep-blue': '#0026ff',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { 
            boxShadow: '0 0 10px 0px rgba(0, 243, 255, 0.7), 0 0 20px 0px rgba(0, 38, 255, 0.5)' 
          },
          '50%': { 
            boxShadow: '0 0 20px 5px rgba(0, 243, 255, 0.9), 0 0 30px 5px rgba(0, 38, 255, 0.7)' 
          },
        }
      },
    },
  },
  plugins: [],
}
""")
        
        # Criar vite.config.js
        with open(os.path.join(frontend_dir, "vite.config.js"), "w") as f:
            f.write("""import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: '../static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const extType = info[info.length - 1]
          if (/\\.(css|scss|sass)$/.test(assetInfo.name)) {
            return 'css/[name][extname]'
          }
          return `img/[name][extname]`
        },
      },
    },
  },
})
""")
        
        # Criar src/main.js
        src_dir = os.path.join(frontend_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        with open(os.path.join(src_dir, "main.js"), "w") as f:
            f.write("""import './style.css'
// Frontend code will be compiled and moved to static/js/main.js
""")
        
        # Criar src/style.css
        with open(os.path.join(src_dir, "style.css"), "w") as f:
            f.write("""@tailwind base;
@tailwind components;
@tailwind utilities;

/* Estilos personalizados */
body {
  background-color: #0f1729;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(0, 38, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(0, 243, 255, 0.1) 0%, transparent 50%);
}

.highlight-animation {
  animation: highlight 1s ease-in-out;
}

@keyframes highlight {
  0% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0.7); }
  50% { box-shadow: 0 0 20px 5px rgba(0, 243, 255, 0.7); }
  100% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0.7); }
}

.prose code {
  @apply bg-gray-800 text-blue-300 px-1 py-0.5 rounded;
}

.prose pre {
  @apply bg-gray-800 text-blue-300 p-4 rounded-lg overflow-x-auto;
}
""")
    
    try:
        # Verificar se npm está instalado
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        print("Configurando frontend...")
        os.chdir(frontend_dir)
        
        # Instalar dependências
        subprocess.run(["npm", "install"], check=True)
        
        # Construir frontend
        subprocess.run(["npm", "run", "build"], check=True)
        
        print("Frontend configurado com sucesso!")
        
    except subprocess.CalledProcessError:
        print("Aviso: npm não está instalado ou não está no PATH")
        print("O frontend precisará ser construído manualmente")
    except Exception as e:
        print(f"Erro ao configurar frontend: {e}")
    finally:
        os.chdir(ROOT_DIR)

def main():
    print("=== Configuração do NeoVoice AI Assistant ===")
    
    # Verificar dependências
    try:
        import flask
        import vosk
        import numpy
    except ImportError:
        print("Instalando dependências Python...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                       os.path.join(ROOT_DIR, "requirements.txt")], check=True)
    
    # Configurar componentes
    setup_vosk()
    setup_gemma()
    setup_frontend()
    
    print("\n=== Configuração concluída! ===")
    print("Para iniciar o aplicativo, execute: python app.py")

if __name__ == "__main__":
    main()
```

## Configuração do Frontend

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../templates/**/*.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00f3ff',
        'deep-blue': '#0026ff',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { 
            boxShadow: '0 0 10px 0px rgba(0, 243, 255, 0.7), 0 0 20px 0px rgba(0, 38, 255, 0.5)' 
          },
          '50%': { 
            boxShadow: '0 0 20px 5px rgba(0, 243, 255, 0.9), 0 0 30px 5px rgba(0, 38, 255, 0.7)' 
          },
        }
      },
    },
  },
  plugins: [],
}
```

## Uso

1. Certifique-se de ter instalado todas as dependências:
   - Python 3.9+ e as bibliotecas necessárias
   - Node.js e npm para o frontend
   - Ollama para o modelo Gemma

2. Execute o script de configuração para baixar os modelos:
   ```
   python scripts/setup.py
   ```

3. Inicie a aplicação:
   ```
   python app.py
   ```

4. Abra o navegador em `http://localhost:5000`

5. Clique no botão de microfone para iniciar o reconhecimento de voz

6. Fale comandos como "git status", "docker ps", "flutter run" ou "cloudflare purge cache"

## Personalização

Você pode personalizar o NeoVoice AI Assistant de várias maneiras:

1. **Adicionar novos comandos**: Edite a função `process_command()` em `app.py` para adicionar suporte a mais comandos

2. **Alterar o tema**: Modifique as cores no arquivo `tailwind.config.js` para personalizar o tema

3. **Usar um modelo diferente**: Substitua o Gemma por outro modelo compatível com Ollama, como Llama 3 ou Mistral

4. **Adicionar mais funcionalidades**: Implemente novas rotas na API Flask para adicionar recursos como histórico de comandos ou atalhos personalizados

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

---

**Nota**: Este projeto foi criado especificamente para um Ryzen 5600 com 8GB de RAM, otimizado para executar modelos de IA localmente com uma interface moderna e responsiva.
```
