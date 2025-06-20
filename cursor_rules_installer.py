#!/usr/bin/env python3
"""
Cursor Rules Installer
Instala automaticamente rules relevantes do Cursor Directory baseado na análise do projeto.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiohttp
from playwright.async_api import async_playwright
import subprocess
import time

class CursorRulesInstaller:
    def __init__(self):
        self.cursor_directory_url = "https://cursor.directory"
        self.rules_cache_file = Path("cursor_rules_cache.json")
        self.installed_rules_file = Path("installed_rules.json")
        self.project_analysis = self.analyze_project()
        
        # Rules específicas para o projeto Sistema Integrado de Conhecimento
        self.project_specific_rules = [
            {
                "id": "deep-learning-python",
                "title": "Deep Learning Developer Python Cursor Rules",
                "url": "https://cursor.directory/rules/deep-learning-developer-python-cursor-rules",
                "tags": ["deep-learning", "tensorflow", "transformers", "diffusion-models"],
                "relevance": 95,
                "content": self.get_deep_learning_rule_content()
            },
            {
                "id": "fastapi-python",
                "title": "FastAPI Python Cursor Rules",
                "url": "https://cursor.directory/rules/fastapi-python-cursor-rules",
                "tags": ["fastapi", "python", "api", "microservices"],
                "relevance": 90,
                "content": self.get_fastapi_rule_content()
            },
            {
                "id": "jupyter-data-analyst",
                "title": "Jupyter Data Analyst Python Cursor Rules",
                "url": "https://cursor.directory/rules/jupyter-data-analyst-python-cursor-rules",
                "tags": ["data-analysis", "jupyter", "visualization", "pandas"],
                "relevance": 85,
                "content": self.get_jupyter_rule_content()
            },
            {
                "id": "python-test-generator",
                "title": "Python Test Case Generator",
                "url": "https://cursor.directory/rules/python-test-case-generator",
                "tags": ["testing", "test-cases", "quality"],
                "relevance": 85,
                "content": self.get_test_generator_rule_content()
            },
            {
                "id": "playwright-cursor",
                "title": "Playwright Cursor Rules",
                "url": "https://cursor.directory/rules/playwright-cursor-rules",
                "tags": ["playwright", "testing", "automation"],
                "relevance": 80,
                "content": self.get_playwright_rule_content()
            },
            {
                "id": "package-management-uv",
                "title": "Package Management with `uv`",
                "url": "https://cursor.directory/rules/package-management-with-uv",
                "tags": ["package-management", "uv", "dependencies"],
                "relevance": 80,
                "content": self.get_uv_rule_content()
            }
        ]
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analisa o projeto para determinar rules relevantes"""
        analysis = {
            "technologies": [],
            "complexity": "advanced",
            "type": "ai_system",
            "features": [],
            "files": []
        }
        
        # Detectar tecnologias baseado nos arquivos
        python_files = list(Path(".").rglob("*.py"))
        requirements_files = list(Path(".").rglob("requirements*.txt"))
        
        analysis["files"] = [str(f) for f in python_files[:10]]  # Primeiros 10 arquivos
        
        for file in python_files:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                
                if "langchain" in content.lower():
                    analysis["technologies"].append("langchain")
                if "tensorflow" in content.lower():
                    analysis["technologies"].append("tensorflow")
                if "fastapi" in content.lower():
                    analysis["technologies"].append("fastapi")
                if "docker" in content.lower():
                    analysis["technologies"].append("docker")
                if "pytest" in content.lower():
                    analysis["technologies"].append("testing")
                if "playwright" in content.lower():
                    analysis["technologies"].append("playwright")
                if "pandas" in content.lower():
                    analysis["technologies"].append("pandas")
                if "numpy" in content.lower():
                    analysis["technologies"].append("numpy")
                if "sklearn" in content.lower():
                    analysis["technologies"].append("scikit-learn")
                if "pyqt" in content.lower():
                    analysis["technologies"].append("pyqt")
                    
            except Exception as e:
                print(f"Erro ao ler arquivo {file}: {e}")
                
        # Detectar features
        if any("gui" in f.name.lower() for f in python_files):
            analysis["features"].append("gui")
        if any("api" in f.name.lower() for f in python_files):
            analysis["features"].append("api")
        if any("test" in f.name.lower() for f in python_files):
            analysis["features"].append("testing")
        if any("knowledge" in f.name.lower() for f in python_files):
            analysis["features"].append("ai_knowledge")
        if any("project" in f.name.lower() for f in python_files):
            analysis["features"].append("project_management")
            
        # Remover duplicatas
        analysis["technologies"] = list(set(analysis["technologies"]))
        analysis["features"] = list(set(analysis["features"]))
            
        return analysis
    
    def get_deep_learning_rule_content(self) -> str:
        """Conteúdo da rule de Deep Learning"""
        return """
# Deep Learning Developer Python Cursor Rules

You are an expert in deep learning, transformers, diffusion models, and modern AI development. You specialize in:

## Core Technologies
- **PyTorch**: Deep learning framework
- **TensorFlow**: Alternative DL framework  
- **Transformers**: Hugging Face transformers library
- **Diffusion Models**: Stable Diffusion, DALL-E, Midjourney
- **LangChain**: LLM application framework
- **OpenAI API**: GPT models integration

## Best Practices
- Use type hints consistently
- Implement proper error handling
- Follow PEP 8 style guidelines
- Use virtual environments
- Document complex algorithms
- Implement proper logging

## LangChain Integration
```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Initialize LLM
llm = OpenAI(temperature=0.7)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer this question: {question}"
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run chain
response = chain.run("What is machine learning?")
```

## TensorFlow Model
```python
import tensorflow as tf
from tensorflow.keras import layers, models

def create_model(input_shape, num_classes):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model
```
"""
    
    def get_fastapi_rule_content(self) -> str:
        """Conteúdo da rule de FastAPI"""
        return """
# FastAPI Python Cursor Rules

You are an expert in Python, FastAPI, and scalable API development. You specialize in:

## Core Technologies
- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework

## Basic FastAPI App
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Knowledge System API", version="1.0.0")

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

class DocumentResponse(BaseModel):
    id: str
    content: str
    processed: bool

@app.post("/documents/", response_model=DocumentResponse)
async def create_document(document: DocumentRequest):
    # Process document
    doc_id = process_document(document.content)
    return DocumentResponse(
        id=doc_id,
        content=document.content,
        processed=True
    )
```

## Best Practices
- Use dependency injection
- Implement proper error handling
- Add comprehensive logging
- Use environment variables
- Implement rate limiting
- Add authentication/authorization
- Write comprehensive tests
- Use async/await for I/O operations
"""
    
    def get_jupyter_rule_content(self) -> str:
        """Conteúdo da rule de Jupyter"""
        return """
# Jupyter Data Analyst Python Cursor Rules

You are an expert in data analysis, visualization, and Jupyter notebooks. You specialize in:

## Core Libraries
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Matplotlib**: Basic plotting
- **Seaborn**: Statistical data visualization
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning

## Notebook Structure
```python
# 1. Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# 2. Data Loading
df = pd.read_csv('data.csv')

# 3. Data Exploration
print(df.info())
print(df.describe())
print(df.isnull().sum())

# 4. Data Cleaning
df = df.dropna()
df = df.drop_duplicates()

# 5. Data Analysis
# Your analysis code here

# 6. Visualization
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='column_name')
plt.title('Distribution of Column Name')
plt.show()

# 7. Conclusions
# Document findings and insights
```

## Best Practices
- Use clear, descriptive variable names
- Document data sources and transformations
- Create reproducible analyses
- Use proper data types
- Handle missing data appropriately
- Validate data quality
"""
    
    def get_test_generator_rule_content(self) -> str:
        """Conteúdo da rule de Test Generator"""
        return """
# Python Test Case Generator

You are an AI coding assistant that can write comprehensive test cases for Python functions. You specialize in:

## Testing Frameworks
- **Pytest**: Primary testing framework
- **Unittest**: Standard library testing
- **Mock**: Mocking and patching
- **Coverage**: Code coverage analysis

## Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from your_module import your_function

class TestYourFunction:
    def test_success_case(self):
        # Arrange
        input_data = "test_input"
        expected_output = "expected_result"
        
        # Act
        result = your_function(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_error_case(self):
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            your_function(invalid_input)
    
    @patch('your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        # Arrange
        mock_dependency.return_value = "mocked_result"
        
        # Act
        result = your_function("test")
        
        # Assert
        assert result == "mocked_result"
        mock_dependency.assert_called_once()
```

## Best Practices
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Test edge cases and error conditions
- Use fixtures for common setup
- Mock external dependencies
- Maintain high test coverage
- Use parameterized tests for multiple scenarios
"""
    
    def get_playwright_rule_content(self) -> str:
        """Conteúdo da rule de Playwright"""
        return """
# Playwright Cursor Rules

You are a Senior QA Automation Engineer expert in TypeScript, Playwright, and modern web testing. You specialize in:

## Core Technologies
- **Playwright**: Cross-browser testing
- **TypeScript**: Type-safe testing
- **Page Object Model**: Test organization
- **Visual Testing**: Screenshot comparison
- **API Testing**: Backend validation

## Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';
import { KnowledgePage } from '../pages/KnowledgePage';

test.describe('Knowledge System', () => {
    let knowledgePage: KnowledgePage;

    test.beforeEach(async ({ page }) => {
        knowledgePage = new KnowledgePage(page);
        await knowledgePage.goto();
    });

    test('should process document successfully', async ({ page }) => {
        // Arrange
        const testDocument = 'test-document.pdf';
        
        // Act
        await knowledgePage.uploadDocument(testDocument);
        await knowledgePage.waitForProcessing();
        
        // Assert
        await expect(knowledgePage.getProcessingStatus()).toHaveText('Completed');
        await expect(knowledgePage.getDocumentCount()).toBeGreaterThan(0);
    });
});
```

## Page Object Model
```typescript
export class KnowledgePage {
    constructor(private page: Page) {}

    async goto() {
        await this.page.goto('/knowledge');
    }

    async uploadDocument(filePath: string) {
        await this.page.setInputFiles('input[type="file"]', filePath);
    }

    async waitForProcessing() {
        await this.page.waitForSelector('.processing-status', { state: 'visible' });
    }

    getProcessingStatus() {
        return this.page.locator('.processing-status');
    }
}
```

## Best Practices
- Use Page Object Model
- Implement proper waiting strategies
- Add visual regression tests
- Test across multiple browsers
- Use data-driven testing
- Implement parallel test execution
- Add comprehensive logging
- Use test fixtures for data setup
"""
    
    def get_uv_rule_content(self) -> str:
        """Conteúdo da rule de Package Management"""
        return """
# Package Management with `uv`

These rules define strict guidelines for Python package management using `uv`.

## Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new project
uv init my-project
cd my-project

# Add dependencies
uv add fastapi uvicorn
uv add --dev pytest black

# Install dependencies
uv sync
```

## Best Practices
- Use `uv` for all package management
- Lock dependencies with `uv lock`
- Use virtual environments
- Specify version constraints
- Use dev dependencies for tools
- Keep requirements files updated

## Project Structure
```
project/
├── pyproject.toml
├── uv.lock
├── src/
│   └── my_project/
└── tests/
```

## Commands
```bash
# Add package
uv add package-name

# Add dev package
uv add --dev package-name

# Remove package
uv remove package-name

# Update packages
uv update

# Run with uv
uv run python script.py
```
"""
    
    async def fetch_cursor_rules(self) -> List[Dict[str, Any]]:
        """Busca rules do Cursor Directory usando Playwright"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                print(f"🌐 Acessando {self.cursor_directory_url}...")
                await page.goto(self.cursor_directory_url)
                await page.wait_for_load_state("networkidle")
                
                # Extrair rules da página
                rules = await page.evaluate("""
                    () => {
                        const ruleElements = document.querySelectorAll('[data-rule], .rule-card, .rule-item');
                        return Array.from(ruleElements).map(el => ({
                            id: el.getAttribute('data-rule') || el.getAttribute('id') || Math.random().toString(36),
                            title: el.querySelector('h3, h4, .title')?.textContent?.trim() || '',
                            description: el.querySelector('p, .description')?.textContent?.trim() || '',
                            tags: Array.from(el.querySelectorAll('.tag, .badge')).map(t => t.textContent?.trim()).filter(Boolean),
                            url: el.querySelector('a')?.href || window.location.href,
                            relevance: 0
                        }));
                    }
                """)
                
                await browser.close()
                
                if not rules:
                    print("⚠️ Não foi possível extrair rules da página, usando rules padrão...")
                    return self.project_specific_rules
                
                return rules
                
        except Exception as e:
            print(f"❌ Erro ao buscar rules: {e}")
            print("📦 Usando rules específicas do projeto...")
            return self.project_specific_rules
    
    def calculate_relevance(self, rule: Dict[str, Any]) -> int:
        """Calcula relevância da rule para o projeto"""
        relevance = 0
        rule_text = f"{rule['title']} {rule['description']} {' '.join(rule.get('tags', []))}".lower()
        
        # Python rules são sempre relevantes
        if "python" in rule_text:
            relevance += 30
            
        # Tecnologias específicas do projeto
        for tech in self.project_analysis["technologies"]:
            if tech in rule_text:
                relevance += 20
                
        # Features do projeto
        for feature in self.project_analysis["features"]:
            if feature in rule_text:
                relevance += 15
                
        # Palavras-chave específicas
        keywords = ["ai", "machine learning", "deep learning", "api", "testing", "automation", "data", "fastapi", "tensorflow", "langchain"]
        for keyword in keywords:
            if keyword in rule_text:
                relevance += 10
                
        return min(relevance, 100)
    
    async def get_relevant_rules(self) -> List[Dict[str, Any]]:
        """Obtém rules relevantes para o projeto"""
        print("🔍 Buscando rules do Cursor Directory...")
        rules = await self.fetch_cursor_rules()
        
        # Adicionar rules específicas do projeto
        all_rules = rules + self.project_specific_rules
        
        # Calcular relevância
        for rule in all_rules:
            if rule.get("relevance", 0) == 0:
                rule["relevance"] = self.calculate_relevance(rule)
            
        # Ordenar por relevância
        all_rules.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Remover duplicatas baseado no título
        seen_titles = set()
        unique_rules = []
        for rule in all_rules:
            if rule["title"] not in seen_titles:
                seen_titles.add(rule["title"])
                unique_rules.append(rule)
        
        # Retornar top 10 mais relevantes
        return unique_rules[:10]
    
    async def install_rule_via_mcp(self, rule: Dict[str, Any]) -> bool:
        """Instala rule via MCP server"""
        try:
            print(f"📦 Instalando rule: {rule['title']}")
            
            # Criar arquivo da rule
            rule_filename = f"cursor_rules/{rule['id']}.md"
            rule_path = Path(rule_filename)
            rule_path.parent.mkdir(exist_ok=True)
            
            # Salvar conteúdo da rule
            content = rule.get("content", f"# {rule['title']}\n\n{rule.get('description', '')}")
            rule_path.write_text(content, encoding='utf-8')
            
            # Salvar rule instalada
            installed_rules = self.load_installed_rules()
            installed_rules.append({
                "id": rule["id"],
                "title": rule["title"],
                "url": rule["url"],
                "installed_at": str(Path.cwd()),
                "relevance": rule["relevance"],
                "file_path": str(rule_path)
            })
            self.save_installed_rules(installed_rules)
            
            print(f"✅ Rule instalada: {rule['title']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao instalar rule {rule['title']}: {e}")
            return False
    
    def load_installed_rules(self) -> List[Dict[str, Any]]:
        """Carrega rules já instaladas"""
        if self.installed_rules_file.exists():
            try:
                return json.loads(self.installed_rules_file.read_text())
            except:
                return []
        return []
    
    def save_installed_rules(self, rules: List[Dict[str, Any]]):
        """Salva lista de rules instaladas"""
        self.installed_rules_file.write_text(json.dumps(rules, indent=2, ensure_ascii=False))
    
    async def install_all_relevant_rules(self):
        """Instala todas as rules relevantes"""
        print("🔍 Analisando projeto...")
        print(f"📁 Arquivos Python encontrados: {len([f for f in Path('.').rglob('*.py')])}")
        print(f"🔧 Tecnologias detectadas: {', '.join(self.project_analysis['technologies'])}")
        print(f"🎯 Features detectadas: {', '.join(self.project_analysis['features'])}")
        
        print("\n📦 Buscando rules relevantes...")
        relevant_rules = await self.get_relevant_rules()
        
        print(f"\n🎯 Encontradas {len(relevant_rules)} rules relevantes:")
        for i, rule in enumerate(relevant_rules, 1):
            print(f"{i}. {rule['title']} (Relevância: {rule['relevance']}%)")
        
        print("\n🚀 Instalando rules...")
        installed_count = 0
        
        for rule in relevant_rules:
            if rule["relevance"] >= 70:  # Instalar apenas rules com alta relevância
                success = await self.install_rule_via_mcp(rule)
                if success:
                    installed_count += 1
                    
        print(f"\n✅ Instalação concluída! {installed_count} rules instaladas.")
        
        # Gerar relatório
        self.generate_installation_report(relevant_rules)
        
        # Criar arquivo de configuração para Cursor/VS Code
        self.create_editor_config()
    
    def generate_installation_report(self, rules: List[Dict[str, Any]]):
        """Gera relatório de instalação"""
        installed_rules = self.load_installed_rules()
        
        report = f"""# 📊 Relatório de Instalação de Rules

## 🎯 Análise do Projeto
- **Tecnologias**: {', '.join(self.project_analysis['technologies'])}
- **Features**: {', '.join(self.project_analysis['features'])}
- **Complexidade**: {self.project_analysis['complexity']}
- **Tipo**: {self.project_analysis['type']}

## 📦 Rules Analisadas
Total de rules encontradas: {len(rules)}

## 🏆 Top 5 Rules Mais Relevantes

"""
        
        for i, rule in enumerate(rules[:5], 1):
            report += f"""### {i}. {rule['title']}
- **Relevância**: {rule['relevance']}%
- **Tags**: {', '.join(rule.get('tags', []))}
- **URL**: {rule['url']}
- **Descrição**: {rule.get('description', '')[:100]}...

"""
        
        report += f"""## 📋 Rules Instaladas
{len(installed_rules)} rules foram instaladas com sucesso:

"""
        
        for rule in installed_rules:
            report += f"- ✅ {rule['title']} (Relevância: {rule['relevance']}%)\n"
        
        report += f"""
## 🎯 Próximos Passos
1. Reiniciar Cursor/VS Code para aplicar as rules
2. Verificar se as rules estão funcionando
3. Personalizar rules conforme necessário
4. Usar as rules para melhorar o desenvolvimento

## 📁 Arquivos Criados
- `cursor_rules/` - Pasta com as rules instaladas
- `installed_rules.json` - Lista de rules instaladas
- `.vscode/settings.json` - Configuração do editor

---
*Relatório gerado em: {Path.cwd()}*
"""
        
        report_file = Path("cursor_rules_report.md")
        report_file.write_text(report, encoding='utf-8')
        print(f"📄 Relatório salvo em: {report_file}")
    
    def create_editor_config(self):
        """Cria configuração para Cursor/VS Code"""
        config_dir = Path(".vscode")
        config_dir.mkdir(exist_ok=True)
        
        settings = {
            "files.associations": {
                "*.md": "markdown"
            },
            "markdown.preview.breaks": True,
            "markdown.preview.fontSize": 14,
            "python.defaultInterpreterPath": "python",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            }
        }
        
        settings_file = config_dir / "settings.json"
        settings_file.write_text(json.dumps(settings, indent=2))
        print(f"⚙️ Configuração do editor salva em: {settings_file}")

# Função principal
async def main():
    print("🚀 Cursor Rules Installer")
    print("=" * 50)
    
    installer = CursorRulesInstaller()
    await installer.install_all_relevant_rules()
    
    print("\n🎉 Instalação concluída!")
    print("📝 Verifique o arquivo 'cursor_rules_report.md' para mais detalhes.")

if __name__ == "__main__":
    asyncio.run(main()) 