#!/usr/bin/env python3
"""
Widget de Controle de Áudio - Microfone e Saída de Som
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QDialog, QSlider,
                             QCheckBox, QGroupBox, QFrame, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont
import json
import os
import sys

# Tentar importar bibliotecas de áudio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

class AudioControlDialog(QDialog):
    """Dialog para configuração de áudio"""
    
    audio_settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎤 Configurações de Áudio")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Configurações atuais
        self.current_settings = {
            "microphone_enabled": False,
            "system_sounds": True,
            "input_device": None,
            "output_device": None,
            "volume": 50,
            "voice_activation": False,
            "voice_engine": "pyttsx3"
        }
        
        self.init_ui()
        self.load_audio_devices()
        self.load_settings()
        
    def init_ui(self):
        """Inicializa interface"""
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Ícone do microfone
        mic_label = QLabel()
        if os.path.exists('static/icons/microphone_active.png'):
            pixmap = QPixmap('static/icons/microphone_active.png')
            mic_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            mic_label.setText("🎤")
            mic_label.setStyleSheet("font-size: 32px;")
        
        title_label = QLabel("Configurações de Áudio")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(mic_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Status das bibliotecas
        status_group = QGroupBox("Status das Dependências")
        status_layout = QVBoxLayout(status_group)
        
        pyaudio_status = "✅ Disponível" if PYAUDIO_AVAILABLE else "❌ Não instalado (pip install pyaudio)"
        pyttsx3_status = "✅ Disponível" if PYTTSX3_AVAILABLE else "❌ Não instalado (pip install pyttsx3)"
        sr_status = "✅ Disponível" if SPEECH_RECOGNITION_AVAILABLE else "❌ Não instalado (pip install SpeechRecognition)"
        
        status_layout.addWidget(QLabel(f"PyAudio: {pyaudio_status}"))
        status_layout.addWidget(QLabel(f"pyttsx3: {pyttsx3_status}"))
        status_layout.addWidget(QLabel(f"SpeechRecognition: {sr_status}"))
        
        layout.addWidget(status_group)
        
        # Configurações de entrada (microfone)
        input_group = QGroupBox("Entrada de Áudio (Microfone)")
        input_layout = QVBoxLayout(input_group)
        
        # Habilitar microfone
        self.mic_enabled_checkbox = QCheckBox("Habilitar comando de voz")
        self.mic_enabled_checkbox.stateChanged.connect(self.on_mic_enabled_changed)
        input_layout.addWidget(self.mic_enabled_checkbox)
        
        # Seleção de dispositivo de entrada
        input_device_layout = QHBoxLayout()
        input_device_layout.addWidget(QLabel("Dispositivo de entrada:"))
        self.input_device_combo = QComboBox()
        self.input_device_combo.currentTextChanged.connect(self.on_input_device_changed)
        input_device_layout.addWidget(self.input_device_combo)
        input_layout.addLayout(input_device_layout)
        
        # Ativação por voz
        self.voice_activation_checkbox = QCheckBox("Ativação por palavra-chave")
        input_layout.addWidget(self.voice_activation_checkbox)
        
        layout.addWidget(input_group)
        
        # Configurações de saída (alto-falantes)
        output_group = QGroupBox("Saída de Áudio (Alto-falantes)")
        output_layout = QVBoxLayout(output_group)
        
        # Habilitar sons do sistema
        self.system_sounds_checkbox = QCheckBox("Habilitar sons do sistema")
        self.system_sounds_checkbox.setChecked(True)
        output_layout.addWidget(self.system_sounds_checkbox)
        
        # Seleção de dispositivo de saída
        output_device_layout = QHBoxLayout()
        output_device_layout.addWidget(QLabel("Dispositivo de saída:"))
        self.output_device_combo = QComboBox()
        self.output_device_combo.currentTextChanged.connect(self.on_output_device_changed)
        output_device_layout.addWidget(self.output_device_combo)
        output_layout.addLayout(output_device_layout)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_label = QLabel("50%")
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        output_layout.addLayout(volume_layout)
        
        layout.addWidget(output_group)
        
        # Botões de teste
        test_group = QGroupBox("Testes")
        test_layout = QHBoxLayout(test_group)
        
        test_mic_button = QPushButton("🎤 Testar Microfone")
        test_mic_button.clicked.connect(self.test_microphone)
        
        test_speaker_button = QPushButton("🔊 Testar Alto-falante")
        test_speaker_button.clicked.connect(self.test_speaker)
        
        test_layout.addWidget(test_mic_button)
        test_layout.addWidget(test_speaker_button)
        
        layout.addWidget(test_group)
        
        # Botões principais
        buttons_layout = QHBoxLayout()
        
        install_button = QPushButton("📦 Instalar Dependências")
        install_button.clicked.connect(self.install_dependencies)
        
        save_button = QPushButton("💾 Salvar")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(install_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
    
    def load_audio_devices(self):
        """Carrega dispositivos de áudio disponíveis"""
        try:
            if PYAUDIO_AVAILABLE:
                p = pyaudio.PyAudio()
                
                # Dispositivos de entrada
                self.input_device_combo.clear()
                self.input_device_combo.addItem("Padrão do sistema")
                
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        self.input_device_combo.addItem(f"{info['name']} (ID: {i})")
                
                # Dispositivos de saída
                self.output_device_combo.clear()
                self.output_device_combo.addItem("Padrão do sistema")
                
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxOutputChannels'] > 0:
                        self.output_device_combo.addItem(f"{info['name']} (ID: {i})")
                
                p.terminate()
            else:
                self.input_device_combo.addItem("PyAudio não instalado")
                self.output_device_combo.addItem("PyAudio não instalado")
                
        except Exception as e:
            self.input_device_combo.addItem(f"Erro: {str(e)}")
            self.output_device_combo.addItem(f"Erro: {str(e)}")
    
    def on_mic_enabled_changed(self, state):
        """Manipula mudança no estado do microfone"""
        self.current_settings["microphone_enabled"] = state == Qt.Checked
    
    def on_input_device_changed(self, device):
        """Manipula mudança no dispositivo de entrada"""
        self.current_settings["input_device"] = device
    
    def on_output_device_changed(self, device):
        """Manipula mudança no dispositivo de saída"""
        self.current_settings["output_device"] = device
    
    def on_volume_changed(self, value):
        """Manipula mudança no volume"""
        self.current_settings["volume"] = value
        self.volume_label.setText(f"{value}%")
    
    def test_microphone(self):
        """Testa o microfone"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            self.show_message("❌ SpeechRecognition não instalado")
            return
        
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.show_message("🎤 Fale algo... (5 segundos)")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5)
                
            text = r.recognize_google(audio, language='pt-BR')
            self.show_message(f"✅ Microfone funcionando! Você disse: '{text}'")
            
        except sr.WaitTimeoutError:
            self.show_message("⏰ Tempo esgotado - nenhum áudio detectado")
        except sr.UnknownValueError:
            self.show_message("❓ Não foi possível entender o áudio")
        except sr.RequestError as e:
            self.show_message(f"❌ Erro no serviço de reconhecimento: {e}")
        except Exception as e:
            self.show_message(f"❌ Erro ao testar microfone: {e}")
    
    def test_speaker(self):
        """Testa o alto-falante"""
        if not PYTTSX3_AVAILABLE:
            self.show_message("❌ pyttsx3 não instalado")
            return
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', self.current_settings["volume"] / 100.0)
            
            # Tentar configurar voz em português
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brasil' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say("Teste de áudio. Se você está ouvindo isso, o alto-falante está funcionando corretamente.")
            engine.runAndWait()
            
            self.show_message("✅ Teste de áudio concluído!")
            
        except Exception as e:
            self.show_message(f"❌ Erro ao testar alto-falante: {e}")
    
    def install_dependencies(self):
        """Instala dependências de áudio"""
        self.show_message("📦 Instalando dependências de áudio...\n\nExecute no terminal:\npip install pyaudio pyttsx3 SpeechRecognition")
    
    def load_settings(self):
        """Carrega configurações salvas"""
        try:
            config_path = "config/audio_settings.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_settings.update(settings)
                    
                    # Aplicar configurações na interface
                    self.mic_enabled_checkbox.setChecked(self.current_settings["microphone_enabled"])
                    self.system_sounds_checkbox.setChecked(self.current_settings["system_sounds"])
                    self.volume_slider.setValue(self.current_settings["volume"])
                    self.voice_activation_checkbox.setChecked(self.current_settings["voice_activation"])
                    
        except Exception as e:
            print(f"Erro ao carregar configurações de áudio: {e}")
    
    def save_settings(self):
        """Salva configurações"""
        try:
            # Atualizar configurações
            self.current_settings["system_sounds"] = self.system_sounds_checkbox.isChecked()
            self.current_settings["voice_activation"] = self.voice_activation_checkbox.isChecked()
            
            # Salvar em arquivo
            config_path = "config/audio_settings.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            
            # Emitir sinal
            self.audio_settings_changed.emit(self.current_settings)
            self.accept()
            
        except Exception as e:
            self.show_message(f"❌ Erro ao salvar configurações: {e}")
    
    def show_message(self, message):
        """Mostra mensagem temporária"""
        # Por simplicidade, vamos usar print - em uma implementação real
        # seria melhor usar um QMessageBox ou notificação
        print(f"[Áudio] {message}")

class AudioControlWidget(QWidget):
    """Widget compacto para controle de áudio"""
    
    audio_settings_changed = pyqtSignal(dict)
    voice_command_received = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_settings = {
            "microphone_enabled": False,
            "system_sounds": True,
            "volume": 50
        }
        self.is_listening = False
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa interface compacta"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Botão do microfone
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(32, 32)
        self.mic_button.setCheckable(True)
        self.mic_button.setToolTip("Clique para configurar áudio")
        self.mic_button.clicked.connect(self.show_audio_config)
        
        # Status do microfone
        self.status_label = QLabel("Áudio desabilitado")
        self.status_label.setStyleSheet("color: #666666; font-size: 11px;")
        
        layout.addWidget(self.mic_button)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.update_mic_icon()
    
    def update_mic_icon(self):
        """Atualiza ícone do microfone"""
        if self.audio_settings["microphone_enabled"]:
            # Microfone ativo
            if os.path.exists('static/icons/microphone_active.png'):
                icon = QIcon('static/icons/microphone_active.png')
                self.mic_button.setIcon(icon)
                self.mic_button.setIconSize(self.mic_button.size())
            else:
                self.mic_button.setText("🎤")
            
            self.status_label.setText("Microfone ativo")
            self.status_label.setStyleSheet("color: #28a745; font-size: 11px;")
        else:
            # Microfone mutado
            if os.path.exists('static/icons/microphone_muted.png'):
                icon = QIcon('static/icons/microphone_muted.png')
                self.mic_button.setIcon(icon)
                self.mic_button.setIconSize(self.mic_button.size())
            else:
                self.mic_button.setText("🔇")
            
            self.status_label.setText("Microfone desabilitado")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 11px;")
    
    def show_audio_config(self):
        """Mostra dialog de configuração de áudio"""
        dialog = AudioControlDialog(self)
        dialog.audio_settings_changed.connect(self.on_audio_settings_changed)
        dialog.exec_()
    
    def on_audio_settings_changed(self, settings):
        """Manipula mudança nas configurações de áudio"""
        self.audio_settings = settings
        self.update_mic_icon()
        self.audio_settings_changed.emit(settings)
    
    def load_settings(self):
        """Carrega configurações de áudio"""
        try:
            config_path = "config/audio_settings.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.audio_settings = json.load(f)
                    self.update_mic_icon()
        except Exception as e:
            print(f"Erro ao carregar configurações de áudio: {e}")
    
    def get_current_settings(self):
        """Retorna configurações atuais"""
        return self.audio_settings 