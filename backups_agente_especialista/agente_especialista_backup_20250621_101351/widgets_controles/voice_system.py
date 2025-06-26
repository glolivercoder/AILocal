#!/usr/bin/env python3
"""
Sistema de Reconhecimento de Voz e TTS Natural
Integração com SpeechRecognition e pyttsx3
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import logging
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import queue

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceSystem:
    """Sistema completo de voz com reconhecimento e TTS"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback_function = None
        self.voice_settings = self.load_voice_settings()
        
        # Inicializar componentes
        self.init_microphone()
        self.init_tts()
    
    def load_voice_settings(self) -> Dict[str, Any]:
        """Carrega configurações de voz"""
        config_file = Path("config/voice_settings.json")
        default_settings = {
            "voice_rate": 150,
            "voice_volume": 0.9,
            "voice_id": None,
            "language": "pt-BR",
            "energy_threshold": 4000,
            "pause_threshold": 0.8,
            "dynamic_energy_threshold": True,
            "ambient_noise_adjustment": True
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar configurações de voz: {e}")
        
        return default_settings
    
    def save_voice_settings(self):
        """Salva configurações de voz"""
        config_file = Path("config/voice_settings.json")
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar configurações de voz: {e}")
    
    def init_microphone(self):
        """Inicializa o microfone"""
        try:
            self.microphone = sr.Microphone()
            
            # Ajustar para ruído ambiente
            if self.voice_settings.get("ambient_noise_adjustment", True):
                logger.info("Ajustando para ruído ambiente...")
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Configurar parâmetros
            self.recognizer.energy_threshold = self.voice_settings.get("energy_threshold", 4000)
            self.recognizer.pause_threshold = self.voice_settings.get("pause_threshold", 0.8)
            self.recognizer.dynamic_energy_threshold = self.voice_settings.get("dynamic_energy_threshold", True)
            
            logger.info("Microfone inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar microfone: {e}")
            self.microphone = None
    
    def init_tts(self):
        """Inicializa o sistema TTS"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configurar voz
            voices = self.tts_engine.getProperty('voices')
            
            # Tentar encontrar voz em português
            voice_id = self.voice_settings.get("voice_id")
            if voice_id:
                self.tts_engine.setProperty('voice', voice_id)
            else:
                # Procurar por voz em português
                for voice in voices:
                    if 'portuguese' in voice.name.lower() or 'portugues' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        self.voice_settings["voice_id"] = voice.id
                        break
            
            # Configurar propriedades
            self.tts_engine.setProperty('rate', self.voice_settings.get("voice_rate", 150))
            self.tts_engine.setProperty('volume', self.voice_settings.get("voice_volume", 0.9))
            
            logger.info("Sistema TTS inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar TTS: {e}")
            self.tts_engine = None
    
    def get_available_voices(self) -> list:
        """Retorna lista de vozes disponíveis"""
        if not self.tts_engine:
            return []
        
        voices = self.tts_engine.getProperty('voices')
        voice_list = []
        
        for voice in voices:
            voice_info = {
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages,
                "gender": voice.gender,
                "age": voice.age
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def set_voice(self, voice_id: str):
        """Define a voz do TTS"""
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.setProperty('voice', voice_id)
            self.voice_settings["voice_id"] = voice_id
            self.save_voice_settings()
            return True
        except Exception as e:
            logger.error(f"Erro ao definir voz: {e}")
            return False
    
    def set_voice_rate(self, rate: int):
        """Define a velocidade da voz"""
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.setProperty('rate', rate)
            self.voice_settings["voice_rate"] = rate
            self.save_voice_settings()
            return True
        except Exception as e:
            logger.error(f"Erro ao definir velocidade: {e}")
            return False
    
    def set_voice_volume(self, volume: float):
        """Define o volume da voz"""
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.setProperty('volume', volume)
            self.voice_settings["voice_volume"] = volume
            self.save_voice_settings()
            return True
        except Exception as e:
            logger.error(f"Erro ao definir volume: {e}")
            return False
    
    def speak(self, text: str, block: bool = True):
        """Fala o texto fornecido"""
        if not self.tts_engine:
            logger.error("TTS não inicializado")
            return False
        
        try:
            if block:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # Executar em thread separada
                def speak_thread():
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                
                thread = threading.Thread(target=speak_thread)
                thread.daemon = True
                thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao falar: {e}")
            return False
    
    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Escuta uma vez e retorna o texto reconhecido"""
        if not self.microphone:
            logger.error("Microfone não inicializado")
            return None
        
        try:
            with self.microphone as source:
                logger.info("Escutando...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Reconhecer usando Google Speech Recognition
            text = self.recognizer.recognize_google(
                audio, 
                language=self.voice_settings.get("language", "pt-BR")
            )
            
            logger.info(f"Reconhecido: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.info("Timeout - nenhum áudio detectado")
            return None
        except sr.UnknownValueError:
            logger.info("Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            logger.error(f"Erro na requisição de reconhecimento: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro no reconhecimento: {e}")
            return None
    
    def start_listening(self, callback: Callable[[str], None]):
        """Inicia escuta contínua com callback"""
        if self.is_listening:
            logger.warning("Já está escutando")
            return False
        
        self.callback_function = callback
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                try:
                    text = self.listen_once(timeout=1)
                    if text and self.callback_function:
                        self.callback_function(text)
                except Exception as e:
                    logger.error(f"Erro no loop de escuta: {e}")
                    time.sleep(0.1)
        
        # Iniciar thread de escuta
        self.listen_thread = threading.Thread(target=listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        logger.info("Escuta contínua iniciada")
        return True
    
    def stop_listening(self):
        """Para a escuta contínua"""
        self.is_listening = False
        logger.info("Escuta contínua parada")
    
    def test_microphone(self) -> bool:
        """Testa o microfone"""
        if not self.microphone:
            return False
        
        try:
            self.speak("Teste do microfone. Fale algo em 3 segundos.")
            text = self.listen_once(timeout=3)
            
            if text:
                self.speak(f"Você disse: {text}")
                return True
            else:
                self.speak("Não consegui entender. Teste falhado.")
                return False
                
        except Exception as e:
            logger.error(f"Erro no teste do microfone: {e}")
            return False
    
    def get_audio_devices(self) -> Dict[str, list]:
        """Retorna dispositivos de áudio disponíveis"""
        devices = {
            "microphones": [],
            "speakers": []
        }
        
        try:
            # Listar microfones
            mic_list = sr.Microphone.list_microphone_names()
            for i, name in enumerate(mic_list):
                devices["microphones"].append({
                    "index": i,
                    "name": name
                })
            
            # Listar alto-falantes (se disponível)
            if self.tts_engine:
                # pyttsx3 não tem método direto para listar dispositivos
                # Mas podemos verificar se está funcionando
                devices["speakers"].append({
                    "name": "Sistema Padrão",
                    "status": "Ativo" if self.tts_engine else "Inativo"
                })
            
        except Exception as e:
            logger.error(f"Erro ao listar dispositivos: {e}")
        
        return devices
    
    def set_microphone(self, device_index: int):
        """Define o microfone a ser usado"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            
            # Reajustar para ruído ambiente
            if self.voice_settings.get("ambient_noise_adjustment", True):
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info(f"Microfone alterado para índice {device_index}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar microfone: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de voz"""
        return {
            "microphone_available": self.microphone is not None,
            "tts_available": self.tts_engine is not None,
            "is_listening": self.is_listening,
            "voice_settings": self.voice_settings,
            "available_voices": len(self.get_available_voices()),
            "audio_devices": self.get_audio_devices()
        }

# Função de teste
def test_voice_system():
    """Testa o sistema de voz"""
    print("🎤 Testando Sistema de Voz")
    print("=" * 40)
    
    voice_system = VoiceSystem()
    
    # Verificar status
    status = voice_system.get_status()
    print(f"Microfone disponível: {status['microphone_available']}")
    print(f"TTS disponível: {status['tts_available']}")
    print(f"Vozes disponíveis: {status['available_voices']}")
    
    # Listar vozes
    voices = voice_system.get_available_voices()
    print(f"\nVozes disponíveis:")
    for voice in voices[:5]:  # Mostrar apenas as primeiras 5
        print(f"- {voice['name']} ({voice['id']})")
    
    # Testar TTS
    if voice_system.tts_engine:
        print("\n🔊 Testando TTS...")
        voice_system.speak("Olá! Este é um teste do sistema de voz.")
    
    # Testar microfone
    if voice_system.microphone:
        print("\n🎤 Testando microfone...")
        success = voice_system.test_microphone()
        print(f"Teste do microfone: {'✅ Sucesso' if success else '❌ Falha'}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_voice_system() 