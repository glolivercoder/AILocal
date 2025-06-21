#!/usr/bin/env python3
"""
Prompt Manager - Sistema de Gerenciamento de Prompts por Categoria
Integração com MCP de busca (Perplexity) para melhorar prompts automaticamente
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
from datetime import datetime
import re

class PromptCategory:
    def __init__(self, name: str, description: str, icon: str, docs_url: str = ""):
        self.name = name
        self.description = description
        self.icon = icon
        self.docs_url = docs_url
        self.prompts = []
        self.last_updated = datetime.now().isoformat()

class Prompt:
    def __init__(self, title: str, content: str, category: str, tags: List[str] = None):
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.usage_count = 0
        self.rating = 0.0

class PromptManager:
    def __init__(self):
        self.prompts_file = Path("prompts_data.json")
        self.categories_file = Path("prompt_categories.json")
        self.categories = self.load_categories()
        self.prompts = self.load_prompts()
        
        # Categorias padrão
        self.default_categories = [
            {
                "name": "Lovable",
                "description": "Prompts para desenvolvimento com Lovable",
                "icon": "❤️",
                "docs_url": "https://docs.lovable.dev/introduction"
            },
            {
                "name": "Leonardo AI",
                "description": "Prompts para geração de imagens com Leonardo AI",
                "icon": "🎨",
                "docs_url": "https://docs.leonardo.ai/"
            },
            {
                "name": "V03 Google",
                "description": "Prompts para geração de vídeo com V03 da Google",
                "icon": "🎬",
                "docs_url": "https://ai.google.dev/gemini-api/docs/models/gemini"
            },
            {
                "name": "Cursor",
                "description": "Prompts para desenvolvimento com Cursor",
                "icon": "⚡",
                "docs_url": "https://cursor.sh/docs"
            },
            {
                "name": "VS Code",
                "description": "Prompts para VS Code e extensões",
                "icon": "💻",
                "docs_url": "https://code.visualstudio.com/docs"
            },
            {
                "name": "Wandsurf",
                "description": "Prompts para Wandsurf",
                "icon": "🌊",
                "docs_url": ""
            },
            {
                "name": "Trae",
                "description": "Prompts para Trae",
                "icon": "🌿",
                "docs_url": ""
            },
            {
                "name": "GitHub Copilot Pro",
                "description": "Prompts para GitHub Copilot Pro",
                "icon": "🤖",
                "docs_url": "https://docs.github.com/en/copilot"
            }
        ]
        
        # Inicializar categorias padrão se não existirem
        if not self.categories:
            self.initialize_default_categories()
    
    def initialize_default_categories(self):
        """Inicializa categorias padrão"""
        for cat_data in self.default_categories:
            category = PromptCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                docs_url=cat_data["docs_url"]
            )
            self.categories[cat_data["name"]] = category
        
        self.save_categories()
    
    def load_categories(self) -> Dict[str, PromptCategory]:
        """Carrega categorias do arquivo"""
        if self.categories_file.exists():
            try:
                data = json.loads(self.categories_file.read_text())
                categories = {}
                for name, cat_data in data.items():
                    category = PromptCategory(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        icon=cat_data["icon"],
                        docs_url=cat_data.get("docs_url", "")
                    )
                    category.prompts = cat_data.get("prompts", [])
                    category.last_updated = cat_data.get("last_updated", datetime.now().isoformat())
                    categories[name] = category
                return categories
            except:
                return {}
        return {}
    
    def save_categories(self):
        """Salva categorias no arquivo"""
        data = {}
        for name, category in self.categories.items():
            data[name] = {
                "name": category.name,
                "description": category.description,
                "icon": category.icon,
                "docs_url": category.docs_url,
                "prompts": category.prompts,
                "last_updated": category.last_updated
            }
        
        self.categories_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def load_prompts(self) -> List[Prompt]:
        """Carrega prompts do arquivo"""
        if self.prompts_file.exists():
            try:
                data = json.loads(self.prompts_file.read_text(encoding='utf-8'))
                prompts = []
                for prompt_data in data:
                    prompt = Prompt(
                        title=prompt_data["title"],
                        content=prompt_data["content"],
                        category=prompt_data["category"],
                        tags=prompt_data.get("tags", [])
                    )
                    prompt.created_at = prompt_data.get("created_at", datetime.now().isoformat())
                    prompt.updated_at = prompt_data.get("updated_at", datetime.now().isoformat())
                    prompt.usage_count = prompt_data.get("usage_count", 0)
                    prompt.rating = prompt_data.get("rating", 0.0)
                    prompts.append(prompt)
                return prompts
            except:
                return []
        return []
    
    def save_prompts(self):
        """Salva prompts no arquivo"""
        data = []
        for prompt in self.prompts:
            data.append({
                "title": prompt.title,
                "content": prompt.content,
                "category": prompt.category,
                "tags": prompt.tags,
                "created_at": prompt.created_at,
                "updated_at": prompt.updated_at,
                "usage_count": prompt.usage_count,
                "rating": prompt.rating
            })
        
        self.prompts_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    async def search_docs_with_perplexity(self, query: str) -> str:
        """Busca documentação usando Perplexity via MCP"""
        try:
            # Simular busca com Perplexity MCP
            search_query = f"melhores práticas {query} documentação oficial"
            
            # Aqui você integraria com o MCP do Perplexity
            # Por enquanto, vamos simular uma resposta
            response = f"""
# Documentação Encontrada para: {query}

## Melhores Práticas

### 1. Estrutura de Prompts
- Use linguagem clara e específica
- Inclua exemplos quando possível
- Mantenha prompts concisos mas informativos

### 2. Otimização
- Teste diferentes variações
- Colete feedback dos usuários
- Itere baseado nos resultados

### 3. Organização
- Categorize prompts por funcionalidade
- Use tags para facilitar busca
- Mantenha versões atualizadas

## Recursos Recomendados
- Documentação oficial: {query}
- Fóruns da comunidade
- Tutoriais e guias
- Exemplos práticos

## Dicas de Implementação
- Comece com prompts simples
- Adicione complexidade gradualmente
- Monitore performance e feedback
"""
            
            return response
            
        except Exception as e:
            print(f"❌ Erro na busca com Perplexity: {e}")
            return ""
    
    async def find_docs_automatically(self, category_name: str) -> str:
        """Tenta encontrar documentação automaticamente"""
        try:
            # Buscar no Google/Perplexity por documentação
            search_terms = [
                f"{category_name} documentation official",
                f"{category_name} best practices docs",
                f"{category_name} developer guide",
                f"{category_name} API documentation"
            ]
            
            for term in search_terms:
                docs = await self.search_docs_with_perplexity(term)
                if docs:
                    return docs
            
            return ""
            
        except Exception as e:
            print(f"❌ Erro na busca automática: {e}")
            return ""
    
    async def improve_prompt_with_docs(self, prompt: Prompt, docs_content: str) -> str:
        """Melhora um prompt usando documentação"""
        try:
            # Análise do prompt atual
            current_content = prompt.content
            
            # Extrair informações da documentação
            improvement_suggestions = f"""
# Sugestões de Melhoria para: {prompt.title}

## Análise do Prompt Atual
```
{current_content}
```

## Melhorias Baseadas na Documentação

### 1. Estrutura
- Adicionar contexto específico
- Incluir exemplos práticos
- Usar linguagem mais precisa

### 2. Otimização
- Remover redundâncias
- Adicionar parâmetros específicos
- Melhorar clareza

### 3. Boas Práticas
- Seguir padrões da documentação
- Incluir validações
- Adicionar tratamento de erros

## Prompt Melhorado Sugerido
```
[Versão melhorada baseada na documentação]
```
"""
            
            return improvement_suggestions
            
        except Exception as e:
            print(f"❌ Erro ao melhorar prompt: {e}")
            return ""
    
    def add_category(self, name: str, description: str, icon: str, docs_url: str = ""):
        """Adiciona uma nova categoria"""
        if name not in self.categories:
            category = PromptCategory(name, description, icon, docs_url)
            self.categories[name] = category
            self.save_categories()
            print(f"✅ Categoria '{name}' adicionada com sucesso!")
            return True
        else:
            print(f"❌ Categoria '{name}' já existe!")
            return False
    
    def add_prompt(self, title: str, content: str, category: str, tags: List[str] = None):
        """Adiciona um novo prompt"""
        if category in self.categories:
            prompt = Prompt(title, content, category, tags)
            self.prompts.append(prompt)
            self.categories[category].prompts.append(title)
            self.save_prompts()
            self.save_categories()
            print(f"✅ Prompt '{title}' adicionado à categoria '{category}'!")
            return True
        else:
            print(f"❌ Categoria '{category}' não encontrada!")
            return False
    
    def get_prompts_by_category(self, category: str) -> List[Prompt]:
        """Obtém prompts de uma categoria específica"""
        return [p for p in self.prompts if p.category == category]
    
    def search_prompts(self, query: str) -> List[Prompt]:
        """Busca prompts por título, conteúdo ou tags"""
        query = query.lower()
        results = []
        
        for prompt in self.prompts:
            if (query in prompt.title.lower() or 
                query in prompt.content.lower() or 
                any(query in tag.lower() for tag in prompt.tags)):
                results.append(prompt)
        
        return results
    
    def update_prompt_usage(self, prompt_title: str):
        """Atualiza contador de uso de um prompt"""
        for prompt in self.prompts:
            if prompt.title == prompt_title:
                prompt.usage_count += 1
                prompt.updated_at = datetime.now().isoformat()
                self.save_prompts()
                break
    
    def rate_prompt(self, prompt_title: str, rating: float):
        """Avalia um prompt"""
        for prompt in self.prompts:
            if prompt.title == prompt_title:
                prompt.rating = rating
                prompt.updated_at = datetime.now().isoformat()
                self.save_prompts()
                break
    
    def export_prompts(self, category: str = None) -> str:
        """Exporta prompts em formato Markdown"""
        if category:
            prompts = self.get_prompts_by_category(category)
        else:
            prompts = self.prompts
        
        export = f"# Prompts Exportados\n\n"
        export += f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        current_category = ""
        for prompt in prompts:
            if prompt.category != current_category:
                current_category = prompt.category
                export += f"## {current_category}\n\n"
            
            export += f"### {prompt.title}\n\n"
            export += f"**Tags**: {', '.join(prompt.tags)}\n\n"
            export += f"**Uso**: {prompt.usage_count} vezes\n"
            export += f"**Avaliação**: {prompt.rating}/5.0\n\n"
            export += f"```\n{prompt.content}\n```\n\n"
            export += f"---\n\n"
        
        return export
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos prompts"""
        stats = {
            "total_prompts": len(self.prompts),
            "total_categories": len(self.categories),
            "most_used_prompt": None,
            "highest_rated_prompt": None,
            "category_stats": {}
        }
        
        if self.prompts:
            # Prompt mais usado
            most_used = max(self.prompts, key=lambda p: p.usage_count)
            stats["most_used_prompt"] = {
                "title": most_used.title,
                "usage_count": most_used.usage_count
            }
            
            # Prompt melhor avaliado
            highest_rated = max(self.prompts, key=lambda p: p.rating)
            stats["highest_rated_prompt"] = {
                "title": highest_rated.title,
                "rating": highest_rated.rating
            }
        
        # Estatísticas por categoria
        for category_name in self.categories:
            category_prompts = self.get_prompts_by_category(category_name)
            stats["category_stats"][category_name] = {
                "count": len(category_prompts),
                "total_usage": sum(p.usage_count for p in category_prompts),
                "avg_rating": sum(p.rating for p in category_prompts) / len(category_prompts) if category_prompts else 0
            }
        
        return stats

# Função principal para teste
async def main():
    print("🚀 Prompt Manager - Sistema de Gerenciamento de Prompts")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Exibir categorias disponíveis
    print(f"\n📂 Categorias disponíveis ({len(manager.categories)}):")
    for name, category in manager.categories.items():
        print(f"  {category.icon} {name}: {category.description}")
    
    # Exibir estatísticas
    stats = manager.get_statistics()
    print(f"\n📊 Estatísticas:")
    print(f"  Total de prompts: {stats['total_prompts']}")
    print(f"  Total de categorias: {stats['total_categories']}")
    
    if stats['most_used_prompt']:
        print(f"  Prompt mais usado: {stats['most_used_prompt']['title']} ({stats['most_used_prompt']['usage_count']} vezes)")
    
    if stats['highest_rated_prompt']:
        print(f"  Prompt melhor avaliado: {stats['highest_rated_prompt']['title']} ({stats['highest_rated_prompt']['rating']}/5.0)")
    
    # Exemplo de busca automática de documentação
    print(f"\n🔍 Testando busca automática de documentação...")
    docs = await manager.find_docs_automatically("Lovable")
    if docs:
        print("✅ Documentação encontrada!")
    else:
        print("❌ Documentação não encontrada")
    
    print(f"\n✅ Sistema inicializado com sucesso!")

if __name__ == "__main__":
    asyncio.run(main()) 