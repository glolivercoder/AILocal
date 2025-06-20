#!/usr/bin/env python3
"""
Widget de Controle de Áudio - Microfone e Saída de Som
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QDialog, QSlider,
                             QCheckBox, QGroupBox, QFrame, QSpinBox, QMessageBox)
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
        self.setFixedSize(800, 650)
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
        layout.setSpacing(15)
        
        # Cabeçalho com ícone maior
        header_layout = QHBoxLayout()
        
        # Ícone do microfone maior
        mic_label = QLabel()
        if os.path.exists('static/icons/microphone_active.png'):
            pixmap = QPixmap('static/icons/microphone_active.png')
            mic_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            mic_label.setText("🎤")
            mic_label.setStyleSheet("font-size: 48px;")
        
        title_label = QLabel("Configurações de Áudio")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00ff7f; margin-bottom: 10px;")
        
        header_layout.addWidget(mic_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Status das bibliotecas com melhor formatação
        status_group = QGroupBox("📊 Status das Dependências")
        status_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(8)
        
        # Criar labels com melhor formatação
        pyaudio_status = "✅ PyAudio: Disponível" if PYAUDIO_AVAILABLE else "❌ PyAudio: Não instalado (pip install pyaudio)"
        pyttsx3_status = "✅ pyttsx3: Disponível" if PYTTSX3_AVAILABLE else "❌ pyttsx3: Não instalado (pip install pyttsx3)"
        sr_status = "✅ SpeechRecognition: Disponível" if SPEECH_RECOGNITION_AVAILABLE else "❌ SpeechRecognition: Não instalado (pip install SpeechRecognition)"
        
        for status_text in [pyaudio_status, pyttsx3_status, sr_status]:
            status_label = QLabel(status_text)
            status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    padding: 5px;
                    margin: 2px;
                    background-color: #2d2d2d;
                    border-radius: 4px;
                }
            """)
            status_layout.addWidget(status_label)
        
        layout.addWidget(status_group)
        
        # Configurações de entrada (microfone) com melhor layout
        input_group = QGroupBox("🎤 Entrada de Áudio (Microfone)")
        input_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(12)
        
        # Habilitar microfone com checkbox maior
        self.mic_enabled_checkbox = QCheckBox("🎤 Habilitar comando de voz")
        self.mic_enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.mic_enabled_checkbox.stateChanged.connect(self.on_mic_enabled_changed)
        input_layout.addWidget(self.mic_enabled_checkbox)
        
        # Seleção de dispositivo de entrada com melhor layout
        input_device_frame = QFrame()
        input_device_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 6px; padding: 10px; }")
        input_device_layout = QVBoxLayout(input_device_frame)
        
        input_device_label = QLabel("🎙️ Dispositivo de entrada:")
        input_device_label.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 5px;")
        input_device_layout.addWidget(input_device_label)
        
        self.input_device_combo = QComboBox()
        self.input_device_combo.setStyleSheet("""
            QComboBox {
                font-size: 11px;
                padding: 8px;
                min-height: 25px;
            }
        """)
        self.input_device_combo.currentTextChanged.connect(self.on_input_device_changed)
        input_device_layout.addWidget(self.input_device_combo)
        
        input_layout.addWidget(input_device_frame)
        
        # Ativação por voz
        self.voice_activation_checkbox = QCheckBox("🔊 Ativação por palavra-chave")
        self.voice_activation_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        input_layout.addWidget(self.voice_activation_checkbox)
        
        layout.addWidget(input_group)
        
        # Configurações de saída (alto-falantes) com melhor layout
        output_group = QGroupBox("🔊 Saída de Áudio (Alto-falantes)")
        output_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(12)
        
        # Habilitar sons do sistema
        self.system_sounds_checkbox = QCheckBox("🔊 Habilitar sons do sistema")
        self.system_sounds_checkbox.setChecked(True)
        self.system_sounds_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        output_layout.addWidget(self.system_sounds_checkbox)
        
        # Seleção de dispositivo de saída com melhor layout
        output_device_frame = QFrame()
        output_device_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 6px; padding: 10px; }")
        output_device_layout = QVBoxLayout(output_device_frame)
        
        output_device_label = QLabel("🔊 Dispositivo de saída:")
        output_device_label.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 5px;")
        output_device_layout.addWidget(output_device_label)
        
        self.output_device_combo = QComboBox()
        self.output_device_combo.setStyleSheet("""
            QComboBox {
                font-size: 11px;
                padding: 8px;
                min-height: 25px;
            }
        """)
        self.output_device_combo.currentTextChanged.connect(self.on_output_device_changed)
        output_device_layout.addWidget(self.output_device_combo)
        
        output_layout.addWidget(output_device_frame)
        
        # Volume com slider maior e melhor formatação
        volume_frame = QFrame()
        volume_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 6px; padding: 10px; }")
        volume_layout = QVBoxLayout(volume_frame)
        
        volume_label = QLabel("🎚️ Volume:")
        volume_label.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 5px;")
        volume_layout.addWidget(volume_label)
        
        volume_control_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #1e1e1e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ff7f;
                border: 1px solid #00ff7f;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_label = QLabel("50%")
        self.volume_label.setStyleSheet("font-size: 12px; font-weight: bold; min-width: 40px;")
        
        volume_control_layout.addWidget(self.volume_slider)
        volume_control_layout.addWidget(self.volume_label)
        volume_layout.addLayout(volume_control_layout)
        
        output_layout.addWidget(volume_frame)
        
        layout.addWidget(output_group)
        
        # Botões de teste com melhor layout
        test_group = QGroupBox("🧪 Testes")
        test_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        test_layout = QHBoxLayout(test_group)
        test_layout.setSpacing(15)
        
        test_mic_button = QPushButton("🎤 Testar Microfone")
        test_mic_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 35px;
                background-color: #007acc;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        test_mic_button.clicked.connect(self.test_microphone)
        
        test_speaker_button = QPushButton("🔊 Testar Alto-falante")
        test_speaker_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 35px;
                background-color: #28a745;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        test_speaker_button.clicked.connect(self.test_speaker)
        
        test_layout.addWidget(test_mic_button)
        test_layout.addWidget(test_speaker_button)
        
        layout.addWidget(test_group)
        
        # Botões principais com melhor layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        install_button = QPushButton("📦 Instalar Dependências")
        install_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 35px;
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        install_button.clicked.connect(self.install_dependencies)
        
        save_button = QPushButton("💾 Salvar Configurações")
        save_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 35px;
                background-color: #28a745;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 12px 20px;
                min-height: 35px;
                background-color: #dc3545;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
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
        """Mostra mensagem em dialog visível"""
        # Determinar tipo de mensagem baseado no conteúdo
        if "✅" in message or "concluído" in message.lower():
            # Mensagem de sucesso
            msg_box = QMessageBox(QMessageBox.Information, "Áudio", message)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-size: 12px;
                }
                QMessageBox QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        elif "❌" in message or "erro" in message.lower():
            # Mensagem de erro
            msg_box = QMessageBox(QMessageBox.Critical, "Erro de Áudio", message)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-size: 12px;
                }
                QMessageBox QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        elif "📦" in message or "instalar" in message.lower():
            # Mensagem de instalação
            msg_box = QMessageBox(QMessageBox.Information, "Instalação", message)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-size: 12px;
                }
                QMessageBox QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            # Mensagem padrão
            msg_box = QMessageBox(QMessageBox.Information, "Áudio", message)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: white;
                    font-size: 12px;
                }
                QMessageBox QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        
        msg_box.exec_()

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