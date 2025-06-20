#!/usr/bin/env python3
"""
Interface Gráfica para Controle de Docker e N8N
Integração com MCPs para automação de workflows
"""

import sys
import os
import json
import subprocess
import requests
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# PyQt5 para interface gráfica
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
        QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
        QSpinBox, QCheckBox, QProgressBar, QMessageBox, QFileDialog,
        QSplitter, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread
    from PyQt5.QtGui import QFont, QIcon, QColor
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("⚠️ PyQt5 não disponível. Instale com: pip install PyQt5")

# Docker SDK
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    print("⚠️ Docker SDK não disponível. Instale com: pip install docker")

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerManager:
    """Gerenciador de containers Docker"""
    
    def __init__(self):
        self.client = None
        self.containers = {}
        self.images = {}
        
        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                logger.info("Docker client inicializado")
            except Exception as e:
                logger.error(f"Erro ao conectar com Docker: {e}")
    
    def get_containers(self) -> List[Dict[str, Any]]:
        """Lista todos os containers"""
        if not self.client:
            return []
        
        try:
            containers = []
            for container in self.client.containers.list(all=True):
                containers.append({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else container.image.id,
                    "ports": container.ports,
                    "created": container.attrs['Created'],
                    "state": container.attrs['State']
                })
            return containers
        except Exception as e:
            logger.error(f"Erro ao listar containers: {e}")
            return []
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Lista todas as imagens"""
        if not self.client:
            return []
        
        try:
            images = []
            for image in self.client.images.list():
                images.append({
                    "id": image.id,
                    "tags": image.tags,
                    "size": image.attrs['Size'],
                    "created": image.attrs['Created']
                })
            return images
        except Exception as e:
            logger.error(f"Erro ao listar imagens: {e}")
            return []
    
    def start_container(self, container_id: str) -> bool:
        """Inicia um container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Container {container_id} iniciado")
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar container {container_id}: {e}")
            return False
    
    def stop_container(self, container_id: str) -> bool:
        """Para um container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            logger.info(f"Container {container_id} parado")
            return True
        except Exception as e:
            logger.error(f"Erro ao parar container {container_id}: {e}")
            return False
    
    def remove_container(self, container_id: str) -> bool:
        """Remove um container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.remove()
            logger.info(f"Container {container_id} removido")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover container {container_id}: {e}")
            return False
    
    def run_container(self, image: str, name: str = None, ports: Dict = None, 
                     environment: Dict = None, volumes: Dict = None) -> str:
        """Executa um novo container"""
        if not self.client:
            return None
        
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=True
            )
            logger.info(f"Container {container.id} executado")
            return container.id
        except Exception as e:
            logger.error(f"Erro ao executar container: {e}")
            return None
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """Obtém logs de um container"""
        if not self.client:
            return ""
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            return logs
        except Exception as e:
            logger.error(f"Erro ao obter logs do container {container_id}: {e}")
            return ""

class N8NManager:
    """Gerenciador de N8N via API"""
    
    def __init__(self, base_url: str = "http://localhost:5678", api_token: str = None):
        self.base_url = base_url
        self.api_token = api_token
        self.session = requests.Session()
        
        if api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            })
    
    def test_connection(self) -> bool:
        """Testa conexão com N8N"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao conectar com N8N: {e}")
            return False
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """Lista todos os workflows"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter workflows: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro ao listar workflows: {e}")
            return []
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Obtém um workflow específico"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter workflow {workflow_id}: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao obter workflow {workflow_id}: {e}")
            return {}
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Cria um novo workflow"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows",
                json=workflow_data
            )
            if response.status_code == 201:
                return response.json()['id']
            else:
                logger.error(f"Erro ao criar workflow: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Erro ao criar workflow: {e}")
            return None
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Atualiza um workflow"""
        try:
            response = self.session.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                json=workflow_data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao atualizar workflow {workflow_id}: {e}")
            return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Remove um workflow"""
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/workflows/{workflow_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao remover workflow {workflow_id}: {e}")
            return False
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Ativa um workflow"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/workflows/{workflow_id}/activate")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao ativar workflow {workflow_id}: {e}")
            return False
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Desativa um workflow"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao desativar workflow {workflow_id}: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, data: Dict[str, Any] = None) -> str:
        """Executa um workflow"""
        try:
            payload = {"data": data} if data else {}
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                json=payload
            )
            if response.status_code == 200:
                return response.json().get('executionId')
            else:
                logger.error(f"Erro ao executar workflow {workflow_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar workflow {workflow_id}: {e}")
            return None
    
    def get_executions(self, workflow_id: str = None) -> List[Dict[str, Any]]:
        """Lista execuções de workflows"""
        try:
            url = f"{self.base_url}/api/v1/executions"
            if workflow_id:
                url += f"?workflowId={workflow_id}"
            
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter execuções: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro ao listar execuções: {e}")
            return []

class MCPIntegration:
    """Integração com MCPs para automação"""
    
    def __init__(self, mcp_manager=None):
        self.mcp_manager = mcp_manager
        self.available_mcps = {
            "filesystem": "Sistema de arquivos",
            "github": "Controle de versão",
            "postgres": "Banco de dados",
            "browser-tools": "Automação web",
            "ollama": "Modelos locais"
        }
    
    def create_webhook_workflow(self, webhook_url: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria workflow de webhook usando MCPs"""
        workflow = {
            "name": f"Webhook Workflow - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "nodes": [
                {
                    "id": "webhook_trigger",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "webhook",
                        "responseMode": "responseNode",
                        "options": {}
                    }
                },
                {
                    "id": "mcp_processor",
                    "type": "n8n-nodes-base.function",
                    "position": [460, 300],
                    "parameters": {
                        "functionCode": f"""
                        // Processar dados do webhook com MCPs
                        const data = $input.first().json;
                        
                        // Aqui você pode integrar com MCPs
                        // Por exemplo, salvar em arquivo, banco de dados, etc.
                        
                        return {{
                            json: {{
                                processed: true,
                                timestamp: new Date().toISOString(),
                                data: data
                            }}
                        }};
                        """
                    }
                }
            ],
            "connections": {
                "webhook_trigger": {
                    "main": [
                        [
                            {
                                "node": "mcp_processor",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }
        
        return workflow
    
    def create_data_architecture_workflow(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """Cria workflow de arquitetura de dados"""
        workflow = {
            "name": f"Data Architecture - {source_type} to {target_type}",
            "nodes": [
                {
                    "id": "source_node",
                    "type": f"n8n-nodes-base.{source_type}",
                    "position": [240, 300],
                    "parameters": {}
                },
                {
                    "id": "transform_node",
                    "type": "n8n-nodes-base.function",
                    "position": [460, 300],
                    "parameters": {
                        "functionCode": """
                        // Transformação de dados
                        const data = $input.all();
                        return data.map(item => ({
                            json: {
                                ...item.json,
                                transformed: true,
                                timestamp: new Date().toISOString()
                            }
                        }));
                        """
                    }
                },
                {
                    "id": "target_node",
                    "type": f"n8n-nodes-base.{target_type}",
                    "position": [680, 300],
                    "parameters": {}
                }
            ],
            "connections": {
                "source_node": {
                    "main": [
                        [
                            {
                                "node": "transform_node",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "transform_node": {
                    "main": [
                        [
                            {
                                "node": "target_node",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }
        
        return workflow

class DockerN8NInterface(QMainWindow):
    """Interface gráfica principal"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar gerenciadores
        self.docker_manager = DockerManager()
        self.n8n_manager = N8NManager()
        self.mcp_integration = MCPIntegration()
        
        # Configurar interface
        self.init_ui()
        self.setup_timers()
        
        # Carregar dados iniciais
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa a interface gráfica"""
        self.setWindowTitle("Docker & N8N Manager - Interface MCP")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Criar abas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Aba Docker
        self.create_docker_tab()
        
        # Aba N8N
        self.create_n8n_tab()
        
        # Aba MCP Integration
        self.create_mcp_tab()
        
        # Aba Workflows
        self.create_workflows_tab()
        
        # Status bar
        self.statusBar().showMessage("Pronto")
    
    def create_docker_tab(self):
        """Cria aba de gerenciamento Docker"""
        docker_widget = QWidget()
        layout = QVBoxLayout(docker_widget)
        
        # Splitter para dividir a interface
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Painel esquerdo - Containers
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de containers
        containers_group = QGroupBox("Containers Docker")
        containers_layout = QVBoxLayout(containers_group)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.refresh_containers_btn = QPushButton("Atualizar")
        self.refresh_containers_btn.clicked.connect(self.refresh_containers)
        buttons_layout.addWidget(self.refresh_containers_btn)
        
        self.start_container_btn = QPushButton("Iniciar")
        self.start_container_btn.clicked.connect(self.start_selected_container)
        buttons_layout.addWidget(self.start_container_btn)
        
        self.stop_container_btn = QPushButton("Parar")
        self.stop_container_btn.clicked.connect(self.stop_selected_container)
        buttons_layout.addWidget(self.stop_container_btn)
        
        self.remove_container_btn = QPushButton("Remover")
        self.remove_container_btn.clicked.connect(self.remove_selected_container)
        buttons_layout.addWidget(self.remove_container_btn)
        
        containers_layout.addLayout(buttons_layout)
        
        # Tabela de containers
        self.containers_table = QTableWidget()
        self.containers_table.setColumnCount(5)
        self.containers_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Status", "Imagem", "Portas"
        ])
        containers_layout.addWidget(self.containers_table)
        
        left_layout.addWidget(containers_group)
        
        # Painel direito - Imagens
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Grupo de imagens
        images_group = QGroupBox("Imagens Docker")
        images_layout = QVBoxLayout(images_group)
        
        # Botões de imagens
        images_buttons_layout = QHBoxLayout()
        
        self.refresh_images_btn = QPushButton("Atualizar")
        self.refresh_images_btn.clicked.connect(self.refresh_images)
        images_buttons_layout.addWidget(self.refresh_images_btn)
        
        self.run_image_btn = QPushButton("Executar")
        self.run_image_btn.clicked.connect(self.run_selected_image)
        images_buttons_layout.addWidget(self.run_image_btn)
        
        images_layout.addLayout(images_buttons_layout)
        
        # Tabela de imagens
        self.images_table = QTableWidget()
        self.images_table.setColumnCount(4)
        self.images_table.setHorizontalHeaderLabels([
            "ID", "Tags", "Tamanho", "Criado"
        ])
        images_layout.addWidget(self.images_table)
        
        right_layout.addWidget(images_group)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 700])
        
        # Adicionar aba
        self.tab_widget.addTab(docker_widget, "Docker")
    
    def create_n8n_tab(self):
        """Cria aba de gerenciamento N8N"""
        n8n_widget = QWidget()
        layout = QVBoxLayout(n8n_widget)
        
        # Configuração N8N
        config_group = QGroupBox("Configuração N8N")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("URL:"))
        self.n8n_url_input = QLineEdit("http://localhost:5678")
        config_layout.addWidget(self.n8n_url_input)
        
        config_layout.addWidget(QLabel("Token:"))
        self.n8n_token_input = QLineEdit()
        self.n8n_token_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.n8n_token_input)
        
        self.connect_n8n_btn = QPushButton("Conectar")
        self.connect_n8n_btn.clicked.connect(self.connect_n8n)
        config_layout.addWidget(self.connect_n8n_btn)
        
        layout.addWidget(config_group)
        
        # Workflows
        workflows_group = QGroupBox("Workflows")
        workflows_layout = QVBoxLayout(workflows_group)
        
        # Botões de workflows
        workflows_buttons_layout = QHBoxLayout()
        
        self.refresh_workflows_btn = QPushButton("Atualizar")
        self.refresh_workflows_btn.clicked.connect(self.refresh_workflows)
        workflows_buttons_layout.addWidget(self.refresh_workflows_btn)
        
        self.create_workflow_btn = QPushButton("Criar")
        self.create_workflow_btn.clicked.connect(self.create_workflow)
        workflows_buttons_layout.addWidget(self.create_workflow_btn)
        
        self.activate_workflow_btn = QPushButton("Ativar")
        self.activate_workflow_btn.clicked.connect(self.activate_selected_workflow)
        workflows_buttons_layout.addWidget(self.activate_workflow_btn)
        
        self.deactivate_workflow_btn = QPushButton("Desativar")
        self.deactivate_workflow_btn.clicked.connect(self.deactivate_selected_workflow)
        workflows_buttons_layout.addWidget(self.deactivate_workflow_btn)
        
        workflows_layout.addLayout(workflows_buttons_layout)
        
        # Lista de workflows
        self.workflows_list = QListWidget()
        workflows_layout.addWidget(self.workflows_list)
        
        layout.addWidget(workflows_group)
        
        # Adicionar aba
        self.tab_widget.addTab(n8n_widget, "N8N")
    
    def create_mcp_tab(self):
        """Cria aba de integração MCP"""
        mcp_widget = QWidget()
        layout = QVBoxLayout(mcp_widget)
        
        # MCPs disponíveis
        mcps_group = QGroupBox("MCPs Disponíveis")
        mcps_layout = QVBoxLayout(mcps_group)
        
        self.mcps_tree = QTreeWidget()
        self.mcps_tree.setHeaderLabel("MCPs")
        mcps_layout.addWidget(self.mcps_tree)
        
        layout.addWidget(mcps_group)
        
        # Criação de workflows
        workflow_creation_group = QGroupBox("Criação de Workflows")
        workflow_creation_layout = QVBoxLayout(workflow_creation_group)
        
        # Tipo de workflow
        workflow_type_layout = QHBoxLayout()
        workflow_type_layout.addWidget(QLabel("Tipo:"))
        self.workflow_type_combo = QComboBox()
        self.workflow_type_combo.addItems([
            "Webhook",
            "Data Architecture",
            "Custom"
        ])
        workflow_type_layout.addWidget(self.workflow_type_combo)
        
        self.create_mcp_workflow_btn = QPushButton("Criar Workflow MCP")
        self.create_mcp_workflow_btn.clicked.connect(self.create_mcp_workflow)
        workflow_type_layout.addWidget(self.create_mcp_workflow_btn)
        
        workflow_creation_layout.addLayout(workflow_type_layout)
        
        layout.addWidget(workflow_creation_group)
        
        # Adicionar aba
        self.tab_widget.addTab(mcp_widget, "MCP Integration")
    
    def create_workflows_tab(self):
        """Cria aba de workflows personalizados"""
        workflows_widget = QWidget()
        layout = QVBoxLayout(workflows_widget)
        
        # Editor de workflow
        editor_group = QGroupBox("Editor de Workflow")
        editor_layout = QVBoxLayout(editor_group)
        
        self.workflow_editor = QTextEdit()
        self.workflow_editor.setPlaceholderText("Cole aqui o JSON do workflow...")
        editor_layout.addWidget(self.workflow_editor)
        
        # Botões do editor
        editor_buttons_layout = QHBoxLayout()
        
        self.load_workflow_btn = QPushButton("Carregar")
        self.load_workflow_btn.clicked.connect(self.load_workflow)
        editor_buttons_layout.addWidget(self.load_workflow_btn)
        
        self.save_workflow_btn = QPushButton("Salvar")
        self.save_workflow_btn.clicked.connect(self.save_workflow)
        editor_buttons_layout.addWidget(self.save_workflow_btn)
        
        self.deploy_workflow_btn = QPushButton("Deploy")
        self.deploy_workflow_btn.clicked.connect(self.deploy_workflow)
        editor_buttons_layout.addWidget(self.deploy_workflow_btn)
        
        editor_layout.addLayout(editor_buttons_layout)
        
        layout.addWidget(editor_group)
        
        # Adicionar aba
        self.tab_widget.addTab(workflows_widget, "Workflows")
    
    def setup_timers(self):
        """Configura timers para atualização automática"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Atualizar a cada 30 segundos
    
    def refresh_data(self):
        """Atualiza todos os dados"""
        self.refresh_containers()
        self.refresh_images()
        self.refresh_workflows()
        self.refresh_mcps()
    
    def refresh_containers(self):
        """Atualiza lista de containers"""
        containers = self.docker_manager.get_containers()
        
        self.containers_table.setRowCount(len(containers))
        for i, container in enumerate(containers):
            self.containers_table.setItem(i, 0, QTableWidgetItem(container['id'][:12]))
            self.containers_table.setItem(i, 1, QTableWidgetItem(container['name']))
            self.containers_table.setItem(i, 2, QTableWidgetItem(container['status']))
            self.containers_table.setItem(i, 3, QTableWidgetItem(container['image']))
            self.containers_table.setItem(i, 4, QTableWidgetItem(str(container['ports'])))
    
    def refresh_images(self):
        """Atualiza lista de imagens"""
        images = self.docker_manager.get_images()
        
        self.images_table.setRowCount(len(images))
        for i, image in enumerate(images):
            self.images_table.setItem(i, 0, QTableWidgetItem(image['id'][:12]))
            self.images_table.setItem(i, 1, QTableWidgetItem(', '.join(image['tags'])))
            self.images_table.setItem(i, 2, QTableWidgetItem(f"{image['size'] / 1024 / 1024:.1f} MB"))
            self.images_table.setItem(i, 3, QTableWidgetItem(image['created'][:10]))
    
    def refresh_workflows(self):
        """Atualiza lista de workflows"""
        if not self.n8n_manager.test_connection():
            return
        
        workflows = self.n8n_manager.get_workflows()
        
        self.workflows_list.clear()
        for workflow in workflows:
            item = QListWidgetItem(f"{workflow.get('name', 'Unnamed')} ({workflow.get('id', 'N/A')})")
            item.setData(Qt.UserRole, workflow)
            self.workflows_list.addItem(item)
    
    def refresh_mcps(self):
        """Atualiza lista de MCPs"""
        self.mcps_tree.clear()
        
        for mcp_id, mcp_name in self.mcp_integration.available_mcps.items():
            item = QTreeWidgetItem(self.mcps_tree)
            item.setText(0, f"{mcp_name} ({mcp_id})")
            item.setData(0, Qt.UserRole, mcp_id)
    
    def start_selected_container(self):
        """Inicia container selecionado"""
        current_row = self.containers_table.currentRow()
        if current_row >= 0:
            container_id = self.containers_table.item(current_row, 0).text()
            if self.docker_manager.start_container(container_id):
                QMessageBox.information(self, "Sucesso", "Container iniciado")
                self.refresh_containers()
    
    def stop_selected_container(self):
        """Para container selecionado"""
        current_row = self.containers_table.currentRow()
        if current_row >= 0:
            container_id = self.containers_table.item(current_row, 0).text()
            if self.docker_manager.stop_container(container_id):
                QMessageBox.information(self, "Sucesso", "Container parado")
                self.refresh_containers()
    
    def remove_selected_container(self):
        """Remove container selecionado"""
        current_row = self.containers_table.currentRow()
        if current_row >= 0:
            container_id = self.containers_table.item(current_row, 0).text()
            if self.docker_manager.remove_container(container_id):
                QMessageBox.information(self, "Sucesso", "Container removido")
                self.refresh_containers()
    
    def run_selected_image(self):
        """Executa imagem selecionada"""
        current_row = self.images_table.currentRow()
        if current_row >= 0:
            image_tags = self.images_table.item(current_row, 1).text()
            if image_tags:
                image_name = image_tags.split(',')[0]
                container_id = self.docker_manager.run_container(image_name)
                if container_id:
                    QMessageBox.information(self, "Sucesso", f"Container executado: {container_id}")
                    self.refresh_containers()
    
    def connect_n8n(self):
        """Conecta ao N8N"""
        url = self.n8n_url_input.text()
        token = self.n8n_token_input.text()
        
        self.n8n_manager = N8NManager(url, token)
        
        if self.n8n_manager.test_connection():
            QMessageBox.information(self, "Sucesso", "Conectado ao N8N")
            self.refresh_workflows()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao conectar com N8N")
    
    def create_workflow(self):
        """Cria novo workflow"""
        # Implementar criação de workflow
        QMessageBox.information(self, "Info", "Funcionalidade em desenvolvimento")
    
    def activate_selected_workflow(self):
        """Ativa workflow selecionado"""
        current_item = self.workflows_list.currentItem()
        if current_item:
            workflow = current_item.data(Qt.UserRole)
            if self.n8n_manager.activate_workflow(workflow['id']):
                QMessageBox.information(self, "Sucesso", "Workflow ativado")
                self.refresh_workflows()
    
    def deactivate_selected_workflow(self):
        """Desativa workflow selecionado"""
        current_item = self.workflows_list.currentItem()
        if current_item:
            workflow = current_item.data(Qt.UserRole)
            if self.n8n_manager.deactivate_workflow(workflow['id']):
                QMessageBox.information(self, "Sucesso", "Workflow desativado")
                self.refresh_workflows()
    
    def create_mcp_workflow(self):
        """Cria workflow com integração MCP"""
        workflow_type = self.workflow_type_combo.currentText()
        
        if workflow_type == "Webhook":
            workflow = self.mcp_integration.create_webhook_workflow(
                "http://localhost:5678/webhook",
                {"test": "data"}
            )
        elif workflow_type == "Data Architecture":
            workflow = self.mcp_integration.create_data_architecture_workflow(
                "postgres", "filesystem"
            )
        else:
            workflow = {"name": "Custom Workflow", "nodes": []}
        
        # Salvar workflow
        workflow_json = json.dumps(workflow, indent=2)
        self.workflow_editor.setPlainText(workflow_json)
        
        QMessageBox.information(self, "Sucesso", "Workflow MCP criado")
    
    def load_workflow(self):
        """Carrega workflow de arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Workflow", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    workflow = json.load(f)
                self.workflow_editor.setPlainText(json.dumps(workflow, indent=2))
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao carregar workflow: {e}")
    
    def save_workflow(self):
        """Salva workflow em arquivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Workflow", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                workflow_text = self.workflow_editor.toPlainText()
                workflow = json.loads(workflow_text)
                
                with open(file_path, 'w') as f:
                    json.dump(workflow, f, indent=2)
                
                QMessageBox.information(self, "Sucesso", "Workflow salvo")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao salvar workflow: {e}")
    
    def deploy_workflow(self):
        """Deploy do workflow no N8N"""
        try:
            workflow_text = self.workflow_editor.toPlainText()
            workflow = json.loads(workflow_text)
            
            workflow_id = self.n8n_manager.create_workflow(workflow)
            if workflow_id:
                QMessageBox.information(self, "Sucesso", f"Workflow deployado: {workflow_id}")
                self.refresh_workflows()
            else:
                QMessageBox.warning(self, "Erro", "Falha ao deployar workflow")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao deployar workflow: {e}")

def main():
    """Função principal"""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 não disponível. Instale com: pip install PyQt5")
        return
    
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Criar e mostrar interface
    interface = DockerN8NInterface()
    interface.show()
    
    # Executar aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 