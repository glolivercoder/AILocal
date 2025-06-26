#!/usr/bin/env python3
"""
Prompt Manager GUI - Interface gráfica para gerenciamento de prompts
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QComboBox, QPushButton, QTextEdit, QLineEdit, QLabel, QTabWidget,
        QListWidget, QListWidgetItem, QDialog, QFormLayout, QMessageBox,
        QScrollArea, QFrame, QSplitter, QGroupBox, QGridLayout, QSpinBox,
        QDoubleSpinBox, QCheckBox, QFileDialog, QProgressBar
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QIcon, QPixmap
except ImportError:
    print("PyQt5 não encontrado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

from prompt_manager import PromptManager, Prompt, PromptCategory

class AddCategoryDialog(QDialog):
    """Dialog para adicionar nova categoria"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Nova Categoria")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        self.icon_edit = QLineEdit()
        self.docs_url_edit = QLineEdit()
        
        form_layout.addRow("Nome:", self.name_edit)
        form_layout.addRow("Descrição:", self.description_edit)
        form_layout.addRow("Ícone (emoji):", self.icon_edit)
        form_layout.addRow("URL da Documentação:", self.docs_url_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Adicionar")
        self.cancel_button = QPushButton("Cancelar")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Valores padrão
        self.icon_edit.setText("📁")
    
    def get_category_data(self):
        """Retorna dados da categoria"""
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.text(),
            "icon": self.icon_edit.text(),
            "docs_url": self.docs_url_edit.text()
        }

class AddPromptDialog(QDialog):
    """Dialog para adicionar novo prompt"""
    def __init__(self, categories: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Novo Prompt")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItems(categories)
        self.tags_edit = QLineEdit()
        self.content_edit = QTextEdit()
        
        form_layout.addRow("Título:", self.title_edit)
        form_layout.addRow("Categoria:", self.category_combo)
        form_layout.addRow("Tags (separadas por vírgula):", self.tags_edit)
        form_layout.addRow("Conteúdo:", self.content_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Adicionar")
        self.cancel_button = QPushButton("Cancelar")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_prompt_data(self):
        """Retorna dados do prompt"""
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        return {
            "title": self.title_edit.text(),
            "category": self.category_combo.currentText(),
            "tags": tags,
            "content": self.content_edit.toPlainText()
        }

class PromptImprovementDialog(QDialog):
    """Dialog para mostrar melhorias de prompt"""
    def __init__(self, original_prompt: str, improved_prompt: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Melhorias de Prompt")
        self.setModal(True)
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Splitter para comparar
        splitter = QSplitter(Qt.Horizontal)
        
        # Prompt original
        original_group = QGroupBox("Prompt Original")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setPlainText(original_prompt)
        self.original_text.setReadOnly(True)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        
        # Prompt melhorado
        improved_group = QGroupBox("Prompt Melhorado")
        improved_layout = QVBoxLayout()
        self.improved_text = QTextEdit()
        self.improved_text.setPlainText(improved_prompt)
        improved_layout.addWidget(self.improved_text)
        improved_group.setLayout(improved_layout)
        
        splitter.addWidget(original_group)
        splitter.addWidget(improved_group)
        
        layout.addWidget(splitter)
        
        # Botões
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Aplicar Melhorias")
        self.cancel_button = QPushButton("Cancelar")
        
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_improved_content(self):
        """Retorna o conteúdo melhorado"""
        return self.improved_text.toPlainText()

class PromptManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prompt_manager = PromptManager()
        self.current_category = None
        self.current_prompt = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Prompt Manager - Sistema de Gerenciamento de Prompts")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Header com dropdown e botão +
        header_layout = QHBoxLayout()
        
        # Dropdown de categorias
        self.category_label = QLabel("Categoria:")
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        
        # Botão + para adicionar categoria
        self.add_category_btn = QPushButton("+")
        self.add_category_btn.setFixedSize(30, 30)
        self.add_category_btn.clicked.connect(self.add_category)
        
        # Botão de busca automática de docs
        self.search_docs_btn = QPushButton("🔍 Buscar Docs")
        self.search_docs_btn.clicked.connect(self.search_documentation)
        
        header_layout.addWidget(self.category_label)
        header_layout.addWidget(self.category_combo)
        header_layout.addWidget(self.add_category_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.search_docs_btn)
        
        main_layout.addLayout(header_layout)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo - Lista de prompts
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_prompt_btn = QPushButton("+ Adicionar Prompt")
        self.edit_prompt_btn = QPushButton("✏️ Editar")
        self.delete_prompt_btn = QPushButton("🗑️ Excluir")
        self.improve_prompt_btn = QPushButton("🚀 Melhorar")
        
        self.add_prompt_btn.clicked.connect(self.add_prompt)
        self.edit_prompt_btn.clicked.connect(self.edit_prompt)
        self.delete_prompt_btn.clicked.connect(self.delete_prompt)
        self.improve_prompt_btn.clicked.connect(self.improve_prompt)
        
        action_layout.addWidget(self.add_prompt_btn)
        action_layout.addWidget(self.edit_prompt_btn)
        action_layout.addWidget(self.delete_prompt_btn)
        action_layout.addWidget(self.improve_prompt_btn)
        
        left_layout.addLayout(action_layout)
        
        # Lista de prompts
        self.prompts_list = QListWidget()
        self.prompts_list.itemClicked.connect(self.on_prompt_selected)
        left_layout.addWidget(self.prompts_list)
        
        left_panel.setLayout(left_layout)
        
        # Painel direito - Detalhes do prompt
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Informações do prompt
        info_group = QGroupBox("Informações do Prompt")
        info_layout = QFormLayout()
        
        self.prompt_title_label = QLabel("")
        self.prompt_category_label = QLabel("")
        self.prompt_tags_label = QLabel("")
        self.prompt_usage_label = QLabel("")
        self.prompt_rating_label = QLabel("")
        
        info_layout.addRow("Título:", self.prompt_title_label)
        info_layout.addRow("Categoria:", self.prompt_category_label)
        info_layout.addRow("Tags:", self.prompt_tags_label)
        info_layout.addRow("Uso:", self.prompt_usage_label)
        info_layout.addRow("Avaliação:", self.prompt_rating_label)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Conteúdo do prompt
        content_group = QGroupBox("Conteúdo")
        content_layout = QVBoxLayout()
        
        self.prompt_content_edit = QTextEdit()
        self.prompt_content_edit.textChanged.connect(self.on_content_changed)
        content_layout.addWidget(self.prompt_content_edit)
        
        content_group.setLayout(content_layout)
        right_layout.addWidget(content_group)
        
        # Botões de ação do prompt
        prompt_action_layout = QHBoxLayout()
        self.copy_prompt_btn = QPushButton("📋 Copiar")
        self.export_prompt_btn = QPushButton("📤 Exportar")
        self.rate_prompt_btn = QPushButton("⭐ Avaliar")
        
        self.copy_prompt_btn.clicked.connect(self.copy_prompt)
        self.export_prompt_btn.clicked.connect(self.export_prompt)
        self.rate_prompt_btn.clicked.connect(self.rate_prompt)
        
        prompt_action_layout.addWidget(self.copy_prompt_btn)
        prompt_action_layout.addWidget(self.export_prompt_btn)
        prompt_action_layout.addWidget(self.rate_prompt_btn)
        
        right_layout.addLayout(prompt_action_layout)
        
        right_panel.setLayout(right_layout)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Sistema de Prompts carregado")
        
        central_widget.setLayout(main_layout)
    
    def load_data(self):
        """Carrega dados iniciais"""
        # Carregar categorias no dropdown
        self.category_combo.clear()
        for name, category in self.prompt_manager.categories.items():
            self.category_combo.addItem(f"{category.icon} {name}")
        
        if self.category_combo.count() > 0:
            self.category_combo.setCurrentIndex(0)
            self.on_category_changed(self.category_combo.currentText())
    
    def on_category_changed(self, category_text):
        """Quando categoria é alterada"""
        if category_text:
            # Extrair nome da categoria (remover ícone)
            category_name = category_text.split(" ", 1)[1] if " " in category_text else category_text
            self.current_category = category_name
            
            # Carregar prompts da categoria
            self.load_prompts_for_category(category_name)
    
    def load_prompts_for_category(self, category_name):
        """Carrega prompts de uma categoria"""
        self.prompts_list.clear()
        prompts = self.prompt_manager.get_prompts_by_category(category_name)
        
        for prompt in prompts:
            item = QListWidgetItem(f"{prompt.title}")
            item.setData(Qt.UserRole, prompt)
            self.prompts_list.addItem(item)
    
    def on_prompt_selected(self, item):
        """Quando um prompt é selecionado"""
        prompt = item.data(Qt.UserRole)
        self.current_prompt = prompt
        
        # Atualizar informações
        self.prompt_title_label.setText(prompt.title)
        self.prompt_category_label.setText(prompt.category)
        self.prompt_tags_label.setText(", ".join(prompt.tags))
        self.prompt_usage_label.setText(str(prompt.usage_count))
        self.prompt_rating_label.setText(f"{prompt.rating:.1f}/5.0")
        
        # Carregar conteúdo
        self.prompt_content_edit.setPlainText(prompt.content)
        
        # Atualizar contador de uso
        self.prompt_manager.update_prompt_usage(prompt.title)
    
    def add_category(self):
        """Adiciona nova categoria"""
        dialog = AddCategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_category_data()
            
            if data["name"]:
                success = self.prompt_manager.add_category(
                    data["name"], data["description"], data["icon"], data["docs_url"]
                )
                
                if success:
                    # Recarregar categorias
                    self.load_data()
                    QMessageBox.information(self, "Sucesso", f"Categoria '{data['name']}' adicionada!")
                else:
                    QMessageBox.warning(self, "Erro", "Categoria já existe!")
            else:
                QMessageBox.warning(self, "Erro", "Nome da categoria é obrigatório!")
    
    def add_prompt(self):
        """Adiciona novo prompt"""
        if not self.current_category:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria primeiro!")
            return
        
        categories = list(self.prompt_manager.categories.keys())
        dialog = AddPromptDialog(categories, self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_prompt_data()
            
            if data["title"] and data["content"]:
                success = self.prompt_manager.add_prompt(
                    data["title"], data["content"], data["category"], data["tags"]
                )
                
                if success:
                    # Recarregar prompts
                    self.load_prompts_for_category(self.current_category)
                    QMessageBox.information(self, "Sucesso", f"Prompt '{data['title']}' adicionado!")
                else:
                    QMessageBox.warning(self, "Erro", "Erro ao adicionar prompt!")
            else:
                QMessageBox.warning(self, "Erro", "Título e conteúdo são obrigatórios!")
    
    def edit_prompt(self):
        """Edita prompt selecionado"""
        if not self.current_prompt:
            QMessageBox.warning(self, "Erro", "Selecione um prompt primeiro!")
            return
        
        # Atualizar conteúdo
        new_content = self.prompt_content_edit.toPlainText()
        if new_content != self.current_prompt.content:
            self.current_prompt.content = new_content
            self.current_prompt.updated_at = datetime.now().isoformat()
            self.prompt_manager.save_prompts()
            QMessageBox.information(self, "Sucesso", "Prompt atualizado!")
    
    def delete_prompt(self):
        """Exclui prompt selecionado"""
        if not self.current_prompt:
            QMessageBox.warning(self, "Erro", "Selecione um prompt primeiro!")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"Deseja excluir o prompt '{self.current_prompt.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.prompt_manager.prompts.remove(self.current_prompt)
            self.prompt_manager.save_prompts()
            self.load_prompts_for_category(self.current_category)
            self.current_prompt = None
            self.prompt_content_edit.clear()
            QMessageBox.information(self, "Sucesso", "Prompt excluído!")
    
    async def improve_prompt(self):
        """Melhora prompt usando documentação"""
        if not self.current_prompt:
            QMessageBox.warning(self, "Erro", "Selecione um prompt primeiro!")
            return
        
        # Buscar documentação
        docs = await self.prompt_manager.find_docs_automatically(self.current_prompt.category)
        
        if docs:
            # Gerar melhorias
            improvements = await self.prompt_manager.improve_prompt_with_docs(
                self.current_prompt, docs
            )
            
            # Mostrar dialog de melhorias
            dialog = PromptImprovementDialog(
                self.current_prompt.content, improvements, self
            )
            
            if dialog.exec_() == QDialog.Accepted:
                improved_content = dialog.get_improved_content()
                self.current_prompt.content = improved_content
                self.current_prompt.updated_at = datetime.now().isoformat()
                self.prompt_manager.save_prompts()
                self.prompt_content_edit.setPlainText(improved_content)
                QMessageBox.information(self, "Sucesso", "Prompt melhorado!")
        else:
            QMessageBox.warning(self, "Erro", "Não foi possível encontrar documentação para melhorar o prompt!")
    
    def copy_prompt(self):
        """Copia prompt para clipboard"""
        if self.current_prompt:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_prompt.content)
            QMessageBox.information(self, "Sucesso", "Prompt copiado para clipboard!")
    
    def export_prompt(self):
        """Exporta prompt"""
        if not self.current_prompt:
            QMessageBox.warning(self, "Erro", "Selecione um prompt primeiro!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar Prompt", 
            f"{self.current_prompt.title}.md", 
            "Markdown (*.md);;Texto (*.txt)"
        )
        
        if filename:
            export_content = self.prompt_manager.export_prompts(self.current_prompt.category)
            Path(filename).write_text(export_content, encoding='utf-8')
            QMessageBox.information(self, "Sucesso", f"Prompt exportado para {filename}!")
    
    def rate_prompt(self):
        """Avalia prompt"""
        if not self.current_prompt:
            QMessageBox.warning(self, "Erro", "Selecione um prompt primeiro!")
            return
        
        rating, ok = QInputDialog.getDouble(
            self, "Avaliar Prompt", 
            "Digite uma avaliação (0.0 - 5.0):",
            self.current_prompt.rating, 0.0, 5.0, 1
        )
        
        if ok:
            self.prompt_manager.rate_prompt(self.current_prompt.title, rating)
            self.current_prompt.rating = rating
            self.prompt_rating_label.setText(f"{rating:.1f}/5.0")
            QMessageBox.information(self, "Sucesso", "Avaliação salva!")
    
    async def search_documentation(self):
        """Busca documentação para categoria atual"""
        if not self.current_category:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria primeiro!")
            return
        
        # Mostrar progresso
        progress = QProgressDialog("Buscando documentação...", "Cancelar", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            docs = await self.prompt_manager.find_docs_automatically(self.current_category)
            progress.close()
            
            if docs:
                # Mostrar documentação encontrada
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Documentação - {self.current_category}")
                dialog.setModal(True)
                dialog.setFixedSize(800, 600)
                
                layout = QVBoxLayout()
                
                text_edit = QTextEdit()
                text_edit.setPlainText(docs)
                text_edit.setReadOnly(True)
                
                layout.addWidget(text_edit)
                
                close_btn = QPushButton("Fechar")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível encontrar documentação!")
                
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Erro", f"Erro ao buscar documentação: {e}")
    
    def on_content_changed(self):
        """Quando conteúdo é alterado"""
        # Aqui você pode implementar auto-save ou outras funcionalidades
        pass

def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Criar e mostrar janela principal
    window = PromptManagerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 