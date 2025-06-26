# 🎥 Transcrição de Vídeo - Guia Completo e Checklist

## 📋 Índice
- [🎯 Visão Geral](#-visão-geral)
- [🏆 Melhores Opções](#-melhores-opções)
- [🔧 Implementação](#-implementação)
- [📊 Comparação de Custos](#-comparação-de-custos)
- [✅ Checklist de Desenvolvimento](#-checklist-de-desenvolvimento)
- [🚀 Código Completo](#-código-completo)
- [📦 Dependências](#-dependências)
- [🎯 Casos de Uso](#-casos-de-uso)

---

## 🎯 Visão Geral

Sistema de transcrição de vídeos com foco em **baixo custo** e **alta qualidade**, suportando:
- 🎥 **Vídeos Locais** (MP4, AVI, MOV, MKV, WebM)
- 🌐 **YouTube** (download automático + transcrição)
- 🎙️ **Podcasts** (extração de áudio + transcrição)
- 📱 **APIs Externas** (AssemblyAI, Deepgram)

---

## 🏆 Melhores Opções

### 🥇 **1. Whisper (OpenAI) - Open Source**
```bash
pip install openai-whisper
```

**✅ Vantagens:**
- 💰 **100% Gratuito** - Modelo open source
- ⭐ **Alta Qualidade** - Mesmo modelo da OpenAI
- 🌍 **99 Idiomas** - Suporte completo
- 🔌 **Offline** - Funciona sem internet
- 📏 **5 Tamanhos** - tiny, base, small, medium, large

**📊 Modelos Disponíveis:**
| Modelo | Tamanho | Velocidade | Precisão | Uso Recomendado |
|--------|---------|------------|----------|-----------------|
| **tiny** | 39MB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Testes rápidos |
| **base** | 74MB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Recomendado** |
| **small** | 244MB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Produção |
| **medium** | 769MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Alta precisão |
| **large** | 1550MB | ⚡ | ⭐⭐⭐⭐⭐ | Máxima precisão |

### 🥈 **2. AssemblyAI - API Econômica**
```python
# Custo: $0.00025/segundo (~$0.90/hora)
# Qualidade: Profissional
# Recursos: Timestamps, speaker diarization
```

### 🥉 **3. Deepgram - Alternativa**
```python
# Custo: $0.0004/segundo (~$1.44/hora)
# Qualidade: Muito boa
# Recursos: Múltiplos idiomas
```

---

## 🔧 Implementação

### 📁 **Estrutura do Projeto**
```
video_transcriber/
├── 📂 models/
│   ├── whisper_models/
│   └── custom_models/
├── 📂 audio/
│   ├── input/
│   └── output/
├── 📂 transcripts/
├── 📄 requirements.txt
├── ⚙️ config.py
├── 🎥 transcriber.py
├── 📥 youtube_downloader.py
└── 🌐 api_client.py
```

### 🚀 **Instalação Rápida**
```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install openai-whisper yt-dlp requests torch transformers

# 3. Instalar FFmpeg (necessário para Whisper)
# Windows: https://ffmpeg.org/download.html
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

---

## 📊 Comparação de Custos

| Serviço | Custo/Hora | Qualidade | Offline | Recursos |
|---------|------------|-----------|---------|----------|
| 🥇 **Whisper Local** | **$0** | ⭐⭐⭐⭐⭐ | ✅ | Completo |
| 🥈 **AssemblyAI** | **$0.90** | ⭐⭐⭐⭐⭐ | ❌ | Profissional |
| 🥉 **Deepgram** | **$1.44** | ⭐⭐⭐⭐ | ❌ | Múltiplos idiomas |
| OpenAI Whisper API | **$6.00** | ⭐⭐⭐⭐⭐ | ❌ | Premium |

**🎯 Recomendação**: Comece com **Whisper local** (modelo "base")!

---

## ✅ Checklist de Desenvolvimento

### 🔧 **Setup Inicial**
- [ ] **Criar estrutura de pastas**
  - [ ] `models/` para modelos Whisper
  - [ ] `audio/input/` para vídeos de entrada
  - [ ] `audio/output/` para áudios processados
  - [ ] `transcripts/` para transcrições

- [ ] **Instalar dependências**
  - [ ] `openai-whisper`
  - [ ] `yt-dlp`
  - [ ] `requests`
  - [ ] `torch`
  - [ ] `transformers`

- [ ] **Configurar FFmpeg**
  - [ ] Windows: Download e adicionar ao PATH
  - [ ] Linux: `sudo apt install ffmpeg`
  - [ ] Mac: `brew install ffmpeg`

### 🎥 **Funcionalidades Básicas**
- [ ] **Transcrição local**
  - [ ] Carregar modelo Whisper
  - [ ] Processar vídeo local
  - [ ] Salvar transcrição em JSON
  - [ ] Suporte a múltiplos formatos

- [ ] **Download YouTube**
  - [ ] Configurar yt-dlp
  - [ ] Extrair áudio em MP3
  - [ ] Integrar com transcrição
  - [ ] Limpar arquivos temporários

- [ ] **Sistema de timestamps**
  - [ ] Ativar word_timestamps
  - [ ] Salvar segmentos com tempo
  - [ ] Formato legível (HH:MM:SS)

### 🌐 **APIs Externas**
- [ ] **AssemblyAI**
  - [ ] Configurar API key
  - [ ] Upload de arquivos
  - [ ] Polling de status
  - [ ] Download de resultados

- [ ] **Deepgram**
  - [ ] Configurar cliente
  - [ ] Processamento assíncrono
  - [ ] Tratamento de erros

### 📊 **Recursos Avançados**
- [ ] **Transcrição em lote**
  - [ ] Processar pasta inteira
  - [ ] Barra de progresso
  - [ ] Relatório de resultados
  - [ ] Tratamento de erros

- [ ] **Múltiplos idiomas**
  - [ ] Detecção automática
  - [ ] Seleção manual
  - [ ] Suporte a 99 idiomas

- [ ] **Otimizações**
  - [ ] Cache de modelos
  - [ ] Processamento paralelo
  - [ ] Compressão de áudio

### 🎨 **Interface**
- [ ] **CLI (Command Line)**
  - [ ] Argumentos de linha de comando
  - [ ] Help e documentação
  - [ ] Barra de progresso
  - [ ] Logs detalhados

- [ ] **GUI (Opcional)**
  - [ ] Interface gráfica simples
  - [ ] Drag & drop de arquivos
  - [ ] Configurações visuais
  - [ ] Preview de resultados

### 🧪 **Testes**
- [ ] **Testes unitários**
  - [ ] Testar carregamento de modelo
  - [ ] Testar transcrição local
  - [ ] Testar download YouTube
  - [ ] Testar APIs externas

- [ ] **Testes de integração**
  - [ ] Fluxo completo local
  - [ ] Fluxo completo YouTube
  - [ ] Fluxo completo API
  - [ ] Tratamento de erros

- [ ] **Testes de performance**
  - [ ] Tempo de transcrição
  - [ ] Uso de memória
  - [ ] Qualidade dos resultados
  - [ ] Comparação entre modelos

### 📚 **Documentação**
- [ ] **README.md**
  - [ ] Instalação passo a passo
  - [ ] Exemplos de uso
  - [ ] Troubleshooting
  - [ ] FAQ

- [ ] **Documentação técnica**
  - [ ] Arquitetura do sistema
  - [ ] API reference
  - [ ] Configurações
  - [ ] Otimizações

### 🚀 **Deploy**
- [ ] **Empacotamento**
  - [ ] Requirements.txt
  - [ ] Setup.py
  - [ ] Dockerfile (opcional)
  - [ ] Executável (pyinstaller)

- [ ] **Distribuição**
  - [ ] GitHub repository
  - [ ] Releases
  - [ ] Documentação online
  - [ ] Exemplos de uso

---

## 🚀 Código Completo

### 🎥 **transcriber.py**
```python
#!/usr/bin/env python3
"""
Video Transcriber - Sistema de Transcrição com Baixo Custo
Suporte para vídeos locais, YouTube e podcasts
"""

import os
import whisper
import yt_dlp
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime
import time

class VideoTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Inicializa o transcriber
        
        Args:
            model_size: Tamanho do modelo Whisper (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.output_dir = Path("transcripts")
        self.output_dir.mkdir(exist_ok=True)
        
        # Carregar modelo
        self.load_model()
    
    def load_model(self):
        """Carrega o modelo Whisper"""
        try:
            print(f"🔄 Carregando modelo Whisper {self.model_size}...")
            self.model = whisper.load_model(self.model_size)
            print(f"✅ Modelo {self.model_size} carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            raise
    
    def transcribe_local_video(self, video_path: str, language: str = "pt") -> Dict[str, Any]:
        """
        Transcreve vídeo local
        
        Args:
            video_path: Caminho para o vídeo
            language: Idioma do vídeo (pt, en, es, etc.)
        
        Returns:
            Dicionário com transcrição e metadados
        """
        try:
            print(f"🎥 Transcrevendo vídeo: {video_path}")
            
            # Verificar se arquivo existe
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {video_path}")
            
            # Transcrição
            result = self.model.transcribe(
                video_path,
                language=language,
                verbose=True
            )
            
            # Salvar resultado
            output_file = self.output_dir / f"{Path(video_path).stem}_transcript.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Transcrição salva em: {output_file}")
            return result
            
        except Exception as e:
            print(f"❌ Erro na transcrição: {e}")
            raise
    
    def download_youtube_video(self, url: str, output_path: str = "audio") -> str:
        """
        Download de vídeo do YouTube
        
        Args:
            url: URL do vídeo do YouTube
            output_path: Pasta para salvar o áudio
        
        Returns:
            Caminho do arquivo de áudio
        """
        try:
            print(f"📥 Baixando vídeo do YouTube: {url}")
            
            # Configurações do yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
                'no_warnings': False,
            }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_file = f"{output_path}/{info['title']}.mp3"
            
            print(f"✅ Áudio salvo em: {audio_file}")
            return audio_file
            
        except Exception as e:
            print(f"❌ Erro no download: {e}")
            raise
    
    def transcribe_youtube(self, url: str, language: str = "pt") -> Dict[str, Any]:
        """
        Transcreve vídeo do YouTube
        
        Args:
            url: URL do vídeo
            language: Idioma do vídeo
        
        Returns:
            Dicionário com transcrição e metadados
        """
        try:
            # Download do vídeo
            audio_file = self.download_youtube_video(url)
            
            # Transcrição
            result = self.transcribe_local_video(audio_file, language)
            
            # Limpar arquivo temporário
            os.remove(audio_file)
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na transcrição do YouTube: {e}")
            raise
    
    def transcribe_with_timestamps(self, video_path: str, language: str = "pt") -> Dict[str, Any]:
        """
        Transcreve com timestamps
        
        Args:
            video_path: Caminho para o vídeo
            language: Idioma do vídeo
        
        Returns:
            Dicionário com transcrição segmentada
        """
        try:
            print(f"⏰ Transcrevendo com timestamps: {video_path}")
            
            result = self.model.transcribe(
                video_path,
                language=language,
                verbose=True,
                word_timestamps=True
            )
            
            # Salvar com timestamps
            output_file = self.output_dir / f"{Path(video_path).stem}_timestamps.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Transcrição com timestamps salva em: {output_file}")
            return result
            
        except Exception as e:
            print(f"❌ Erro na transcrição com timestamps: {e}")
            raise
    
    def batch_transcribe(self, folder_path: str, language: str = "pt") -> Dict[str, Any]:
        """
        Transcreve múltiplos vídeos
        
        Args:
            folder_path: Pasta com vídeos
            language: Idioma dos vídeos
        
        Returns:
            Dicionário com resultados de todos os vídeos
        """
        try:
            print(f"📁 Transcrevendo pasta: {folder_path}")
            
            results = {}
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
            
            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    file_path = os.path.join(folder_path, file)
                    print(f"🎥 Processando: {file}")
                    
                    try:
                        result = self.transcribe_local_video(file_path, language)
                        results[file] = result
                    except Exception as e:
                        print(f"❌ Erro ao processar {file}: {e}")
                        results[file] = {"error": str(e)}
            
            # Salvar resultados em lote
            batch_file = self.output_dir / f"batch_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Transcrições em lote salvas em: {batch_file}")
            return results
            
        except Exception as e:
            print(f"❌ Erro na transcrição em lote: {e}")
            raise

# Cliente para APIs externas
class APITranscriber:
    def __init__(self, api_key: str, service: str = "assemblyai"):
        """
        Inicializa cliente de API
        
        Args:
            api_key: Chave da API
            service: Serviço (assemblyai, deepgram, etc.)
        """
        self.api_key = api_key
        self.service = service
        
        if service == "assemblyai":
            self.base_url = "https://api.assemblyai.com/v2"
        elif service == "deepgram":
            self.base_url = "https://api.deepgram.com/v1"
    
    def transcribe_with_api(self, audio_path: str, language: str = "pt") -> Dict[str, Any]:
        """
        Transcreve usando API externa
        
        Args:
            audio_path: Caminho para o áudio
            language: Idioma do áudio
        
        Returns:
            Dicionário com transcrição
        """
        try:
            if self.service == "assemblyai":
                return self._transcribe_assemblyai(audio_path, language)
            elif self.service == "deepgram":
                return self._transcribe_deepgram(audio_path, language)
            else:
                raise ValueError(f"Serviço não suportado: {self.service}")
                
        except Exception as e:
            print(f"❌ Erro na API: {e}")
            raise
    
    def _transcribe_assemblyai(self, audio_path: str, language: str) -> Dict[str, Any]:
        """Transcreve usando AssemblyAI"""
        # Upload
        with open(audio_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/upload",
                data=f,
                headers={"authorization": self.api_key}
            )
            upload_url = response.json()["upload_url"]
        
        # Transcrição
        data = {
            "audio_url": upload_url,
            "language_code": language
        }
        
        response = requests.post(
            f"{self.base_url}/transcript",
            json=data,
            headers={"authorization": self.api_key}
        )
        
        transcript_id = response.json()["id"]
        
        # Aguardar conclusão
        while True:
            response = requests.get(
                f"{self.base_url}/transcript/{transcript_id}",
                headers={"authorization": self.api_key}
            )
            
            status = response.json()["status"]
            if status == "completed":
                return response.json()
            elif status == "error":
                raise Exception("Erro na transcrição")
            
            time.sleep(3)

# Interface de linha de comando
def main():
    """Interface principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Transcriber - Baixo Custo")
    parser.add_argument("--input", "-i", required=True, help="Arquivo de vídeo ou URL do YouTube")
    parser.add_argument("--model", "-m", default="base", choices=["tiny", "base", "small", "medium", "large"], help="Tamanho do modelo Whisper")
    parser.add_argument("--language", "-l", default="pt", help="Idioma do vídeo")
    parser.add_argument("--timestamps", "-t", action="store_true", help="Incluir timestamps")
    parser.add_argument("--api", "-a", help="Usar API externa (assemblyai, deepgram)")
    parser.add_argument("--api-key", "-k", help="Chave da API")
    
    args = parser.parse_args()
    
    try:
        if args.api and args.api_key:
            # Usar API externa
            transcriber = APITranscriber(args.api_key, args.api)
            result = transcriber.transcribe_with_api(args.input, args.language)
        else:
            # Usar Whisper local
            transcriber = VideoTranscriber(args.model)
            
            if args.input.startswith("http"):
                # YouTube
                result = transcriber.transcribe_youtube(args.input, args.language)
            else:
                # Arquivo local
                if args.timestamps:
                    result = transcriber.transcribe_with_timestamps(args.input, args.language)
                else:
                    result = transcriber.transcribe_local_video(args.input, args.language)
        
        # Mostrar resultado
        print("\n📝 Transcrição:")
        print("=" * 50)
        print(result.get("text", "Nenhum texto encontrado"))
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
```

### 📥 **youtube_downloader.py**
```python
#!/usr/bin/env python3
"""
YouTube Downloader - Download de vídeos do YouTube
"""

import yt_dlp
import os
from pathlib import Path

class YouTubeDownloader:
    def __init__(self, output_path: str = "audio"):
        """
        Inicializa o downloader
        
        Args:
            output_path: Pasta para salvar os arquivos
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
    
    def download_audio(self, url: str, quality: str = "192") -> str:
        """
        Download de áudio do YouTube
        
        Args:
            url: URL do vídeo
            quality: Qualidade do áudio (128, 192, 320)
        
        Returns:
            Caminho do arquivo de áudio
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = self.output_path / f"{info['title']}.mp3"
            
        return str(audio_file)
    
    def download_video(self, url: str, quality: str = "720") -> str:
        """
        Download de vídeo do YouTube
        
        Args:
            url: URL do vídeo
            quality: Qualidade do vídeo (480, 720, 1080)
        
        Returns:
            Caminho do arquivo de vídeo
        """
        ydl_opts = {
            'format': f'best[height<={quality}]',
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = self.output_path / f"{info['title']}.{info['ext']}"
            
        return str(video_file)
```

---

## 📦 Dependências

### 📄 **requirements.txt**
```txt
# Transcrição
openai-whisper>=20231117
torch>=2.0.0
transformers>=4.35.0

# Download YouTube
yt-dlp>=2023.12.30

# Requisições HTTP
requests>=2.31.0

# Processamento de áudio
ffmpeg-python>=0.2.0

# Utilitários
tqdm>=4.66.0
colorama>=0.4.6
```

### 🔧 **Instalação**
```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar FFmpeg
# Windows: Download de https://ffmpeg.org/download.html
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

---

## 🎯 Casos de Uso

### 🎥 **Vídeo Local**
```bash
# Transcrição básica
python transcriber.py -i video.mp4 -m base -l pt

# Com timestamps
python transcriber.py -i video.mp4 -m small -l pt -t

# Múltiplos arquivos
python transcriber.py -i pasta_videos/ -m base -l pt
```

### 🌐 **YouTube**
```bash
# Download + transcrição
python transcriber.py -i "https://youtube.com/watch?v=VIDEO_ID" -m base -l pt

# Com timestamps
python transcriber.py -i "https://youtube.com/watch?v=VIDEO_ID" -m small -l pt -t
```

### 🌐 **API Externa**
```bash
# AssemblyAI
python transcriber.py -i audio.mp3 -a assemblyai -k YOUR_API_KEY

# Deepgram
python transcriber.py -i audio.mp3 -a deepgram -k YOUR_API_KEY
```

### 🎙️ **Podcast**
```python
# Código Python
transcriber = VideoTranscriber("base")
result = transcriber.transcribe_local_video("podcast.mp3", "pt")
print(result["text"])
```

---

## 🚀 Próximos Passos

### 🔄 **Melhorias Futuras**
- [ ] **Interface gráfica** com PyQt6
- [ ] **Processamento em lote** com barra de progresso
- [ ] **Speaker diarization** (identificar falantes)
- [ ] **Tradução automática** para múltiplos idiomas
- [ ] **Sincronização de legendas** (SRT, VTT)
- [ ] **Análise de sentimento** do conteúdo
- [ ] **Resumo automático** do vídeo
- [ ] **Detecção de tópicos** principais

### 📱 **Integração com Apps**
- [ ] **Bot Telegram** para transcrição
- [ ] **Webhook** para processamento automático
- [ ] **API REST** para integração
- [ ] **Plugin para editores** (VS Code, Cursor)
- [ ] **Extensão de navegador** para YouTube

### 🎯 **Otimizações**
- [ ] **Cache de modelos** para reutilização
- [ ] **Processamento paralelo** para múltiplos vídeos
- [ ] **Compressão inteligente** de áudio
- [ ] **GPU acceleration** com CUDA
- [ ] **Streaming** para vídeos longos

---

## 📚 Recursos Adicionais

### 🔗 **Links Úteis**
- [Whisper GitHub](https://github.com/openai/whisper)
- [AssemblyAI Docs](https://www.assemblyai.com/docs)
- [Deepgram Docs](https://developers.deepgram.com/)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg Docs](https://ffmpeg.org/documentation.html)

### 📖 **Tutoriais**
- [Instalação Whisper](https://github.com/openai/whisper#setup)
- [Configuração FFmpeg](https://ffmpeg.org/download.html)
- [Uso yt-dlp](https://github.com/yt-dlp/yt-dlp#usage)

### 🐛 **Troubleshooting**
- **Erro FFmpeg**: Instalar FFmpeg e adicionar ao PATH
- **Erro CUDA**: Usar CPU se GPU não disponível
- **Erro YouTube**: Atualizar yt-dlp: `pip install -U yt-dlp`
- **Erro API**: Verificar chave e limites de uso

---

**🎯 Status**: ✅ Documentação Completa  
**📅 Última Atualização**: 20/06/2025  
**🚀 Próximo Passo**: Implementar checklist de desenvolvimento
