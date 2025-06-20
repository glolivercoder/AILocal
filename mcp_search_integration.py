#!/usr/bin/env python3
"""
MCP Search Integration - Integração com serviços de busca para documentação
"""

import asyncio
import json
import aiohttp
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

class MCPSearchIntegration:
    def __init__(self):
        self.config_file = Path("mcp_search_config.json")
        self.cache_file = Path("search_cache.json")
        self.load_config()
        
    def load_config(self):
        """Carrega configuração do MCP Search"""
        default_config = {
            "perplexity_api_key": "",
            "google_api_key": "",
            "brave_api_key": "",
            "search_engines": ["perplexity", "google", "brave"],
            "cache_enabled": True,
            "cache_duration": 3600,  # 1 hora
            "max_results": 10
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Salva configuração"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def load_cache(self) -> Dict[str, Any]:
        """Carrega cache de buscas"""
        if self.cache_file.exists() and self.config.get("cache_enabled", True):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self, cache: Dict[str, Any]):
        """Salva cache de buscas"""
        if self.config.get("cache_enabled", True):
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
    
    async def search_with_perplexity(self, query: str) -> Dict[str, Any]:
        """Busca usando Perplexity API"""
        try:
            api_key = self.config.get("perplexity_api_key")
            if not api_key:
                return {"error": "API key do Perplexity não configurada"}
            
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em buscar e analisar documentação técnica. Forneça informações detalhadas e práticas sobre o tópico solicitado."
                    },
                    {
                        "role": "user",
                        "content": f"Busque documentação oficial e melhores práticas sobre: {query}. Inclua exemplos práticos e dicas de implementação."
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "source": "perplexity"
                        }
                    else:
                        return {"error": f"Erro na API Perplexity: {response.status}"}
                        
        except Exception as e:
            return {"error": f"Erro na busca Perplexity: {e}"}
    
    async def search_with_google(self, query: str) -> Dict[str, Any]:
        """Busca usando Google Custom Search API"""
        try:
            api_key = self.config.get("google_api_key")
            if not api_key:
                return {"error": "API key do Google não configurada"}
            
            # Você precisaria configurar um Custom Search Engine ID
            search_engine_id = self.config.get("google_search_engine_id", "")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "num": self.config.get("max_results", 10)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": self.parse_google_results(result),
                            "source": "google"
                        }
                    else:
                        return {"error": f"Erro na API Google: {response.status}"}
                        
        except Exception as e:
            return {"error": f"Erro na busca Google: {e}"}
    
    def parse_google_results(self, results: Dict[str, Any]) -> str:
        """Parse resultados do Google"""
        content = "# Resultados da Busca Google\n\n"
        
        if "items" in results:
            for item in results["items"]:
                content += f"## {item.get('title', 'Sem título')}\n\n"
                content += f"**URL**: {item.get('link', 'N/A')}\n\n"
                content += f"{item.get('snippet', 'Sem descrição')}\n\n"
                content += "---\n\n"
        
        return content
    
    async def search_with_brave(self, query: str) -> Dict[str, Any]:
        """Busca usando Brave Search API"""
        try:
            api_key = self.config.get("brave_api_key")
            if not api_key:
                return {"error": "API key do Brave não configurada"}
            
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            
            params = {
                "q": query,
                "count": self.config.get("max_results", 10)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": self.parse_brave_results(result),
                            "source": "brave"
                        }
                    else:
                        return {"error": f"Erro na API Brave: {response.status}"}
                        
        except Exception as e:
            return {"error": f"Erro na busca Brave: {e}"}
    
    def parse_brave_results(self, results: Dict[str, Any]) -> str:
        """Parse resultados do Brave"""
        content = "# Resultados da Busca Brave\n\n"
        
        if "web" in results and "results" in results["web"]:
            for item in results["web"]["results"]:
                content += f"## {item.get('title', 'Sem título')}\n\n"
                content += f"**URL**: {item.get('url', 'N/A')}\n\n"
                content += f"{item.get('description', 'Sem descrição')}\n\n"
                content += "---\n\n"
        
        return content
    
    async def search_documentation(self, query: str, category: str = "") -> Dict[str, Any]:
        """Busca documentação usando múltiplos serviços"""
        # Verificar cache primeiro
        cache = self.load_cache()
        cache_key = f"{query}_{category}"
        
        if cache_key in cache:
            cached_result = cache[cache_key]
            # Verificar se cache ainda é válido
            if cached_result.get("timestamp", 0) + self.config.get("cache_duration", 3600) > asyncio.get_event_loop().time():
                return cached_result["data"]
        
        # Buscar em múltiplos serviços
        results = []
        search_engines = self.config.get("search_engines", ["perplexity"])
        
        # Construir query melhorada
        enhanced_query = f"{category} {query} documentation best practices official docs"
        
        for engine in search_engines:
            if engine == "perplexity":
                result = await self.search_with_perplexity(enhanced_query)
            elif engine == "google":
                result = await self.search_with_google(enhanced_query)
            elif engine == "brave":
                result = await self.search_with_brave(enhanced_query)
            else:
                continue
            
            if result.get("success"):
                results.append(result)
        
        # Combinar resultados
        if results:
            combined_result = {
                "success": True,
                "content": self.combine_search_results(results),
                "sources": [r.get("source", "unknown") for r in results],
                "query": enhanced_query
            }
            
            # Salvar no cache
            cache[cache_key] = {
                "data": combined_result,
                "timestamp": asyncio.get_event_loop().time()
            }
            self.save_cache(cache)
            
            return combined_result
        else:
            return {"error": "Nenhum resultado encontrado"}
    
    def combine_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Combina resultados de múltiplas fontes"""
        combined = "# Documentação Encontrada\n\n"
        combined += f"**Busca realizada em**: {', '.join([r.get('source', 'unknown') for r in results])}\n\n"
        
        for i, result in enumerate(results, 1):
            source = result.get("source", "unknown")
            content = result.get("content", "")
            
            combined += f"## Fonte {i}: {source.upper()}\n\n"
            combined += content
            combined += "\n\n---\n\n"
        
        return combined
    
    async def find_docs_for_category(self, category: str) -> Dict[str, Any]:
        """Encontra documentação específica para uma categoria"""
        search_terms = [
            f"{category} official documentation",
            f"{category} developer guide",
            f"{category} best practices",
            f"{category} API documentation",
            f"{category} getting started"
        ]
        
        all_results = []
        
        for term in search_terms:
            result = await self.search_documentation(term, category)
            if result.get("success"):
                all_results.append(result)
        
        if all_results:
            # Combinar todos os resultados
            combined_content = "# Documentação Completa para " + category + "\n\n"
            
            for result in all_results:
                combined_content += result.get("content", "") + "\n\n"
            
            return {
                "success": True,
                "content": combined_content,
                "category": category,
                "sources": list(set([s for r in all_results for s in r.get("sources", [])]))
            }
        else:
            return {"error": f"Não foi possível encontrar documentação para {category}"}
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de busca"""
        cache = self.load_cache()
        
        stats = {
            "total_searches": len(cache),
            "cache_size": len(json.dumps(cache)),
            "config": {
                "search_engines": self.config.get("search_engines", []),
                "cache_enabled": self.config.get("cache_enabled", True),
                "max_results": self.config.get("max_results", 10)
            }
        }
        
        return stats

# Função principal para teste
async def main():
    print("🔍 MCP Search Integration - Teste")
    print("=" * 40)
    
    integration = MCPSearchIntegration()
    
    # Testar busca
    print("\n🔍 Testando busca de documentação...")
    result = await integration.find_docs_for_category("Lovable")
    
    if result.get("success"):
        print("✅ Documentação encontrada!")
        print(f"📊 Fontes: {', '.join(result.get('sources', []))}")
        print(f"📝 Conteúdo: {len(result.get('content', ''))} caracteres")
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    # Mostrar estatísticas
    stats = integration.get_search_statistics()
    print(f"\n📊 Estatísticas:")
    print(f"  Total de buscas: {stats['total_searches']}")
    print(f"  Tamanho do cache: {stats['cache_size']} bytes")
    print(f"  Motores de busca: {', '.join(stats['config']['search_engines'])}")

if __name__ == "__main__":
    asyncio.run(main()) 