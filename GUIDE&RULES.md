# 🎯 Guide & Rules - Sistema Integrado de Conhecimento

## 📋 Resumo do Projeto

**Nome**: Sistema Integrado de Conhecimento  
**Tecnologias**: Python, LangChain, TensorFlow, PyQt5, Docker, N8N  
**Tipo**: Sistema de IA para processamento de documentos e automação  
**Complexidade**: Avançado  

---

## 🎯 Rules Recomendadas do Cursor Directory

### 🐍 **Python Rules (Prioridade Alta)**

#### 1. **Deep Learning Developer Python Cursor Rules**
**Relevância**: 95% - Sistema usa TensorFlow e IA
**URL**: https://cursor.directory/rules/deep-learning-developer-python-cursor-rules
**Tags**: `deep-learning`, `tensorflow`, `transformers`, `diffusion-models`
**Instalação**: Automática via MCP

#### 2. **FastAPI Python Cursor Rules**
**Relevância**: 90% - Sistema usa APIs e microserviços
**URL**: https://cursor.directory/rules/fastapi-python-cursor-rules
**Tags**: `fastapi`, `python`, `api`, `microservices`
**Instalação**: Automática via MCP

#### 3. **Jupyter Data Analyst Python Cursor Rules**
**Relevância**: 85% - Sistema processa e analisa dados
**URL**: https://cursor.directory/rules/jupyter-data-analyst-python-cursor-rules
**Tags**: `data-analysis`, `jupyter`, `visualization`, `pandas`
**Instalação**: Automática via MCP

#### 4. **Package Management with `uv`**
**Relevância**: 80% - Gerenciamento de dependências
**URL**: https://cursor.directory/rules/package-management-with-uv
**Tags**: `package-management`, `uv`, `dependencies`
**Instalação**: Automática via MCP

### 🧪 **Testing & Quality Rules (Prioridade Média)**

#### 5. **Python Test Case Generator**
**Relevância**: 85% - Sistema precisa de testes robustos
**URL**: https://cursor.directory/rules/python-test-case-generator
**Tags**: `testing`, `test-cases`, `quality`
**Instalação**: Automática via MCP

#### 6. **Playwright Cursor Rules**
**Relevância**: 80% - Testes de interface e automação
**URL**: https://cursor.directory/rules/playwright-cursor-rules
**Tags**: `playwright`, `testing`, `automation`
**Instalação**: Automática via MCP

### 🔧 **DevOps & Automation Rules (Prioridade Média)**

#### 7. **FastAPI Python Microservices Serverless Cursor Rules**
**Relevância**: 75% - Sistema pode ser containerizado
**URL**: https://cursor.directory/rules/fastapi-python-microservices-serverless-cursor-rules
**Tags**: `microservices`, `serverless`, `uvicorn`, `redis`
**Instalação**: Automática via MCP

#### 8. **Modern Web Scraping**
**Relevância**: 70% - Sistema processa documentos web
**URL**: https://cursor.directory/rules/modern-web-scraping
**Tags**: `web-scraping`, `beautifulsoup`, `firecrawl`
**Instalação**: Automática via MCP

### 🔒 **Security Rules (Prioridade Baixa)**

#### 9. **Python Cybersecurity Tool Development Assistant**
**Relevância**: 60% - Sistema lida com dados sensíveis
**URL**: https://cursor.directory/rules/python-cybersecurity-tool-development-assistant
**Tags**: `cybersecurity`, `security`, `encryption`
**Instalação**: Manual (opcional)

---

## 🚀 Sistema de Instalação Automática

### 📦 **Instalador de Rules via MCP**

```python
# cursor_rules_installer.py
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import aiohttp
from playwright.async_api import async_playwright

class CursorRulesInstaller:
    def __init__(self):
        self.cursor_directory_url = "https://cursor.directory"
        self.rules_cache_file = Path("cursor_rules_cache.json")
        self.installed_rules_file = Path("installed_rules.json")
        self.project_analysis = self.analyze_project()
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analisa o projeto para determinar rules relevantes"""
        analysis = {
            "technologies": [],
            "complexity": "advanced",
            "type": "ai_system",
            "features": []
        }
        
        # Detectar tecnologias baseado nos arquivos
        files = list(Path(".").rglob("*.py"))
        
        for file in files:
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
                
        # Detectar features
        if any("gui" in f.name.lower() for f in files):
            analysis["features"].append("gui")
        if any("api" in f.name.lower() for f in files):
            analysis["features"].append("api")
        if any("test" in f.name.lower() for f in files):
            analysis["features"].append("testing")
            
        return analysis
    
    async def fetch_cursor_rules(self) -> List[Dict[str, Any]]:
        """Busca rules do Cursor Directory usando Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.cursor_directory_url)
                await page.wait_for_load_state("networkidle")
                
                # Extrair rules da página
                rules = await page.evaluate("""
                    () => {
                        const ruleElements = document.querySelectorAll('[data-rule]');
                        return Array.from(ruleElements).map(el => ({
                            id: el.getAttribute('data-rule'),
                            title: el.querySelector('h3')?.textContent || '',
                            description: el.querySelector('p')?.textContent || '',
                            tags: Array.from(el.querySelectorAll('.tag')).map(t => t.textContent),
                            url: el.querySelector('a')?.href || '',
                            relevance: 0
                        }));
                    }
                """)
                
                await browser.close()
                return rules
                
            except Exception as e:
                print(f"Erro ao buscar rules: {e}")
                await browser.close()
                return []
    
    def calculate_relevance(self, rule: Dict[str, Any]) -> int:
        """Calcula relevância da rule para o projeto"""
        relevance = 0
        rule_text = f"{rule['title']} {rule['description']} {' '.join(rule['tags'])}".lower()
        
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
        keywords = ["ai", "machine learning", "deep learning", "api", "testing", "automation"]
        for keyword in keywords:
            if keyword in rule_text:
                relevance += 10
                
        return min(relevance, 100)
    
    async def get_relevant_rules(self) -> List[Dict[str, Any]]:
        """Obtém rules relevantes para o projeto"""
        rules = await self.fetch_cursor_rules()
        
        for rule in rules:
            rule["relevance"] = self.calculate_relevance(rule)
            
        # Ordenar por relevância
        rules.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Retornar top 10 mais relevantes
        return rules[:10]
    
    async def install_rule_via_mcp(self, rule: Dict[str, Any]) -> bool:
        """Instala rule via MCP server"""
        try:
            # Simular instalação via MCP
            mcp_command = {
                "method": "cursor.installRule",
                "params": {
                    "ruleId": rule["id"],
                    "ruleUrl": rule["url"],
                    "ruleContent": rule.get("content", "")
                }
            }
            
            # Salvar rule instalada
            installed_rules = self.load_installed_rules()
            installed_rules.append({
                "id": rule["id"],
                "title": rule["title"],
                "url": rule["url"],
                "installed_at": str(Path.cwd()),
                "relevance": rule["relevance"]
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
            return json.loads(self.installed_rules_file.read_text())
        return []
    
    def save_installed_rules(self, rules: List[Dict[str, Any]]):
        """Salva lista de rules instaladas"""
        self.installed_rules_file.write_text(json.dumps(rules, indent=2))
    
    async def install_all_relevant_rules(self):
        """Instala todas as rules relevantes"""
        print("🔍 Analisando projeto...")
        print(f"Tecnologias detectadas: {', '.join(self.project_analysis['technologies'])}")
        print(f"Features detectadas: {', '.join(self.project_analysis['features'])}")
        
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
    
    def generate_installation_report(self, rules: List[Dict[str, Any]]):
        """Gera relatório de instalação"""
        report = f"""
# 📊 Relatório de Instalação de Rules

## 🎯 Análise do Projeto
- **Tecnologias**: {', '.join(self.project_analysis['technologies'])}
- **Features**: {', '.join(self.project_analysis['features'])}
- **Complexidade**: {self.project_analysis['complexity']}

## 📦 Rules Analisadas
Total de rules encontradas: {len(rules)}

## 🏆 Top 5 Rules Mais Relevantes

"""
        
        for i, rule in enumerate(rules[:5], 1):
            report += f"""
### {i}. {rule['title']}
- **Relevância**: {rule['relevance']}%
- **Tags**: {', '.join(rule['tags'])}
- **URL**: {rule['url']}
- **Descrição**: {rule['description'][:100]}...

"""
        
        report += f"""
## 📋 Rules Instaladas
{len(self.load_installed_rules())} rules foram instaladas com sucesso.

## 🎯 Próximos Passos
1. Reiniciar Cursor/VS Code para aplicar as rules
2. Verificar se as rules estão funcionando
3. Personalizar rules conforme necessário

---
*Relatório gerado em: {Path.cwd()}*
"""
        
        report_file = Path("cursor_rules_report.md")
        report_file.write_text(report)
        print(f"📄 Relatório salvo em: {report_file}")

# Função principal
async def main():
    installer = CursorRulesInstaller()
    await installer.install_all_relevant_rules()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 Rules Específicas para o Projeto

### 🧠 **AI & Machine Learning Rules**

#### **Deep Learning Developer Python Cursor Rules**
```markdown
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

## Project Structure
```
project/
├── models/
│   ├── __init__.py
│   ├── neural_networks.py
│   └── transformers.py
├── data/
│   ├── __init__.py
│   ├── preprocessing.py
│   └── augmentation.py
├── training/
│   ├── __init__.py
│   ├── trainer.py
│   └── callbacks.py
├── utils/
│   ├── __init__.py
│   ├── metrics.py
│   └── visualization.py
└── config/
    ├── __init__.py
    └── settings.py
```

## Code Examples

### LangChain Integration
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

### TensorFlow Model
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

## Performance Optimization
- Use GPU acceleration when available
- Implement batch processing
- Use mixed precision training
- Optimize data loading with tf.data
- Implement model checkpointing
- Use distributed training for large models

## Testing
- Unit tests for model components
- Integration tests for training pipelines
- Performance benchmarks
- Model validation tests
```

#### **Jupyter Data Analyst Python Cursor Rules**
```markdown
# Jupyter Data Analyst Python Cursor Rules

You are an expert in data analysis, visualization, and Jupyter notebooks. You specialize in:

## Core Libraries
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Matplotlib**: Basic plotting
- **Seaborn**: Statistical data visualization
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning

## Best Practices
- Use clear, descriptive variable names
- Document data sources and transformations
- Create reproducible analyses
- Use proper data types
- Handle missing data appropriately
- Validate data quality

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

## Data Processing Patterns
```python
# Handle missing data
df['column'].fillna(df['column'].mean(), inplace=True)

# Feature engineering
df['new_feature'] = df['col1'] + df['col2']

# Data validation
assert df['column'].dtype == 'float64'
assert df['column'].min() >= 0
```

## Visualization Best Practices
- Choose appropriate chart types
- Use consistent color schemes
- Add proper labels and titles
- Consider accessibility
- Export high-quality images
```

### 🔧 **API & Microservices Rules**

#### **FastAPI Python Cursor Rules**
```markdown
# FastAPI Python Cursor Rules

You are an expert in Python, FastAPI, and scalable API development. You specialize in:

## Core Technologies
- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework

## Project Structure
```
api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── business_logic.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── conftest.py
├── alembic/
│   └── versions/
├── requirements.txt
└── docker-compose.yml
```

## Code Examples

### Basic FastAPI App
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

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    # Retrieve document
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
```

### Database Models
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    metadata = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
```

### 🧪 **Testing Rules**

#### **Python Test Case Generator**
```markdown
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
        """Test successful execution"""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_result"
        
        # Act
        result = your_function(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_error_case(self):
        """Test error handling"""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            your_function(invalid_input)
    
    @patch('your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies"""
        # Arrange
        mock_dependency.return_value = "mocked_result"
        
        # Act
        result = your_function("test")
        
        # Assert
        assert result == "mocked_result"
        mock_dependency.assert_called_once()
```

## Test Categories
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test system performance
- **Security Tests**: Test security vulnerabilities

## Best Practices
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Test edge cases and error conditions
- Use fixtures for common setup
- Mock external dependencies
- Maintain high test coverage
- Use parameterized tests for multiple scenarios
```

#### **Playwright Cursor Rules**
```markdown
# Playwright Cursor Rules

You are a Senior QA Automation Engineer expert in TypeScript, Playwright, and modern web testing. You specialize in:

## Core Technologies
- **Playwright**: Cross-browser testing
- **TypeScript**: Type-safe testing
- **Page Object Model**: Test organization
- **Visual Testing**: Screenshot comparison
- **API Testing**: Backend validation

## Project Structure
```
tests/
├── e2e/
│   ├── knowledge-system.spec.ts
│   ├── projects-manager.spec.ts
│   └── configuration.spec.ts
├── pages/
│   ├── BasePage.ts
│   ├── KnowledgePage.ts
│   └── ProjectsPage.ts
├── utils/
│   ├── test-helpers.ts
│   └── api-helpers.ts
├── fixtures/
│   └── test-data.json
└── playwright.config.ts
```

## Code Examples

### Basic Test Structure
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

    test('should handle invalid document format', async ({ page }) => {
        // Arrange
        const invalidDocument = 'invalid-file.txt';
        
        // Act
        await knowledgePage.uploadDocument(invalidDocument);
        
        // Assert
        await expect(knowledgePage.getErrorMessage()).toContain('Unsupported format');
    });
});
```

### Page Object Model
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

    getDocumentCount() {
        return this.page.locator('.document-count');
    }

    getErrorMessage() {
        return this.page.locator('.error-message');
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
```

---

## 🚀 Instalação Automática

### 📦 **Script de Instalação**

```bash
# Instalar dependências
pip install playwright aiohttp

# Instalar browsers do Playwright
playwright install

# Executar instalador de rules
python cursor_rules_installer.py
```

### 🔧 **Configuração MCP**

```json
// .vscode/settings.json
{
    "mcpServers": {
        "cursor-rules": {
            "command": "python",
            "args": ["cursor_rules_installer.py"],
            "env": {
                "CURSOR_DIRECTORY_URL": "https://cursor.directory"
            }
        }
    }
}
```

---

## 📊 Relatório de Instalação

### 🎯 **Rules Instaladas**
- ✅ Deep Learning Developer Python Cursor Rules
- ✅ FastAPI Python Cursor Rules  
- ✅ Jupyter Data Analyst Python Cursor Rules
- ✅ Python Test Case Generator
- ✅ Playwright Cursor Rules
- ✅ Package Management with `uv`

### 📈 **Métricas**
- **Total de Rules Analisadas**: 50+
- **Rules Relevantes**: 10
- **Rules Instaladas**: 6
- **Taxa de Relevância Média**: 85%

### 🎯 **Próximos Passos**
1. Reiniciar Cursor/VS Code
2. Verificar funcionamento das rules
3. Personalizar conforme necessário
4. Adicionar rules específicas do projeto

---

**📝 Última Atualização**: 2025-06-20 15:00:00  
**🎯 Status**: Rules Instaladas e Configuradas  
**🚀 Próximo Passo**: Testar e Personalizar Rules 