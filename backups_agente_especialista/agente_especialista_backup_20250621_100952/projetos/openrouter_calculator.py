#!/usr/bin/env python3
"""
Calculadora de Tokens e Créditos OpenRouter
Monitoramento de uso e custos
"""

import requests
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import tiktoken

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterCalculator:
    """Calculadora de tokens e créditos OpenRouter"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.usage_file = Path("config/openrouter_usage.json")
        self.models_info = self.load_models_info()
        self.usage_history = self.load_usage_history()
        
    def load_models_info(self) -> Dict[str, Any]:
        """Carrega informações dos modelos OpenRouter"""
        models = {
            # Modelos Gratuitos
            "google/gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "provider": "Google",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 8192,
                "context_length": 1048576,
                "description": "Modelo rápido e eficiente da Google"
            },
            "meta-llama/llama-3-8b-instruct": {
                "name": "Llama 3 8B Instruct",
                "provider": "Meta",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 8192,
                "context_length": 8192,
                "description": "Modelo Llama 3 otimizado para instruções"
            },
            "microsoft/phi-3-mini": {
                "name": "Phi-3 Mini",
                "provider": "Microsoft",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 4096,
                "context_length": 4096,
                "description": "Modelo pequeno e rápido da Microsoft"
            },
            "nousresearch/nous-hermes-2-mixtral-8x7b-dpo": {
                "name": "Nous Hermes 2 Mixtral",
                "provider": "Nous Research",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 32768,
                "context_length": 32768,
                "description": "Modelo Mixtral otimizado"
            },
            "openchat/openchat-3.5": {
                "name": "OpenChat 3.5",
                "provider": "OpenChat",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 4096,
                "context_length": 4096,
                "description": "Modelo de chat otimizado"
            },
            "qwen/qwen2.5-7b-instruct": {
                "name": "Qwen 2.5 7B Instruct",
                "provider": "Alibaba",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 32768,
                "context_length": 32768,
                "description": "Modelo Qwen 2.5 multilingue"
            },
            "snowflake/snowflake-arctic-instruct": {
                "name": "Snowflake Arctic Instruct",
                "provider": "Snowflake",
                "type": "free",
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "max_tokens": 4096,
                "context_length": 4096,
                "description": "Modelo Snowflake para instruções"
            },
            
            # Modelos Premium
            "anthropic/claude-3-opus": {
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "type": "premium",
                "input_cost_per_1k": 0.015,
                "output_cost_per_1k": 0.075,
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Modelo mais avançado da Anthropic"
            },
            "anthropic/claude-3-sonnet": {
                "name": "Claude 3 Sonnet",
                "provider": "Anthropic",
                "type": "premium",
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015,
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Modelo equilibrado da Anthropic"
            },
            "anthropic/claude-3-haiku": {
                "name": "Claude 3 Haiku",
                "provider": "Anthropic",
                "type": "premium",
                "input_cost_per_1k": 0.00025,
                "output_cost_per_1k": 0.00125,
                "max_tokens": 4096,
                "context_length": 200000,
                "description": "Modelo rápido da Anthropic"
            },
            "google/gemini-pro": {
                "name": "Gemini Pro",
                "provider": "Google",
                "type": "premium",
                "input_cost_per_1k": 0.0005,
                "output_cost_per_1k": 0.0015,
                "max_tokens": 8192,
                "context_length": 32768,
                "description": "Modelo Pro da Google"
            },
            "google/gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "provider": "Google",
                "type": "premium",
                "input_cost_per_1k": 0.0035,
                "output_cost_per_1k": 0.0105,
                "max_tokens": 8192,
                "context_length": 1048576,
                "description": "Modelo Pro com contexto longo"
            },
            "mistralai/mistral-large": {
                "name": "Mistral Large",
                "provider": "Mistral AI",
                "type": "premium",
                "input_cost_per_1k": 0.007,
                "output_cost_per_1k": 0.024,
                "max_tokens": 4096,
                "context_length": 32768,
                "description": "Modelo grande da Mistral"
            },
            "openai/gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "type": "premium",
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03,
                "max_tokens": 4096,
                "context_length": 128000,
                "description": "GPT-4 Turbo da OpenAI"
            },
            "openai/gpt-4o": {
                "name": "GPT-4o",
                "provider": "OpenAI",
                "type": "premium",
                "input_cost_per_1k": 0.005,
                "output_cost_per_1k": 0.015,
                "max_tokens": 4096,
                "context_length": 128000,
                "description": "GPT-4o otimizado"
            },
            "openai/gpt-4o-mini": {
                "name": "GPT-4o Mini",
                "provider": "OpenAI",
                "type": "premium",
                "input_cost_per_1k": 0.00015,
                "output_cost_per_1k": 0.0006,
                "max_tokens": 4096,
                "context_length": 128000,
                "description": "GPT-4o versão mini"
            },
            "deepseek/deepseek-coder": {
                "name": "DeepSeek Coder",
                "provider": "DeepSeek",
                "type": "premium",
                "input_cost_per_1k": 0.00014,
                "output_cost_per_1k": 0.00028,
                "max_tokens": 16384,
                "context_length": 16384,
                "description": "Modelo especializado em código"
            }
        }
        return models
    
    def load_usage_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de uso"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar histórico: {e}")
        
        return []
    
    def save_usage_history(self):
        """Salva histórico de uso"""
        self.usage_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Conta tokens em um texto"""
        try:
            # Usar tiktoken para contar tokens
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Erro ao contar tokens: {e}")
            # Fallback: estimativa aproximada (1 token ≈ 4 caracteres)
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> Dict[str, float]:
        """Calcula custo de uma requisição"""
        if model not in self.models_info:
            return {"input_cost": 0, "output_cost": 0, "total_cost": 0}
        
        model_info = self.models_info[model]
        
        # Calcular custos
        input_cost = (input_tokens / 1000) * model_info["input_cost_per_1k"]
        output_cost = (output_tokens / 1000) * model_info["output_cost_per_1k"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Obtém saldo da conta OpenRouter"""
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/auth/key", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "credits": data.get("credits", 0),
                    "spent": data.get("spent", 0),
                    "limit": data.get("limit", 0),
                    "remaining": data.get("remaining", 0)
                }
            else:
                logger.error(f"Erro ao obter saldo: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {e}")
            return None
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas de uso"""
        if not self.api_key:
            return {}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Calcular datas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            response = requests.get(f"{self.base_url}/auth/usage", headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter estatísticas: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def add_usage_record(self, model: str, input_tokens: int, output_tokens: int, 
                        cost: float, timestamp: str = None):
        """Adiciona registro de uso"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "model_info": self.models_info.get(model, {})
        }
        
        self.usage_history.append(record)
        self.save_usage_history()
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Obtém resumo do uso local"""
        if not self.usage_history:
            return {}
        
        # Filtrar por período
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [
            record for record in self.usage_history
            if datetime.fromisoformat(record["timestamp"]) > cutoff_date
        ]
        
        if not recent_usage:
            return {}
        
        # Calcular estatísticas
        total_requests = len(recent_usage)
        total_input_tokens = sum(record["input_tokens"] for record in recent_usage)
        total_output_tokens = sum(record["output_tokens"] for record in recent_usage)
        total_cost = sum(record["cost"] for record in recent_usage)
        
        # Modelos mais usados
        model_usage = {}
        for record in recent_usage:
            model = record["model"]
            if model not in model_usage:
                model_usage[model] = {
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0
                }
            
            model_usage[model]["requests"] += 1
            model_usage[model]["input_tokens"] += record["input_tokens"]
            model_usage[model]["output_tokens"] += record["output_tokens"]
            model_usage[model]["cost"] += record["cost"]
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost": round(total_cost, 6),
            "average_cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0,
            "model_usage": model_usage
        }
    
    def estimate_cost(self, text: str, model: str, expected_output_length: int = 100) -> Dict[str, Any]:
        """Estima custo de uma requisição"""
        input_tokens = self.count_tokens(text, model)
        
        # Estimar tokens de saída baseado no comprimento esperado
        output_tokens = self.count_tokens("a" * expected_output_length, model)
        
        cost_info = self.calculate_cost(input_tokens, output_tokens, model)
        
        return {
            "input_text_length": len(text),
            "input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_total_tokens": input_tokens + output_tokens,
            "cost_estimate": cost_info,
            "model_info": self.models_info.get(model, {})
        }
    
    def get_free_models(self) -> List[str]:
        """Retorna lista de modelos gratuitos"""
        return [
            model_id for model_id, info in self.models_info.items()
            if info["type"] == "free"
        ]
    
    def get_premium_models(self) -> List[str]:
        """Retorna lista de modelos premium"""
        return [
            model_id for model_id, info in self.models_info.items()
            if info["type"] == "premium"
        ]
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Retorna informações de um modelo específico"""
        return self.models_info.get(model)
    
    def get_all_models(self) -> Dict[str, Any]:
        """Retorna todos os modelos disponíveis"""
        return self.models_info
    
    def set_api_key(self, api_key: str):
        """Define a API key"""
        self.api_key = api_key
    
    def get_cost_comparison(self, text: str, models: List[str] = None) -> Dict[str, Any]:
        """Compara custos entre diferentes modelos"""
        if models is None:
            models = list(self.models_info.keys())
        
        comparison = {}
        
        for model in models:
            if model in self.models_info:
                estimate = self.estimate_cost(text, model)
                comparison[model] = {
                    "name": self.models_info[model]["name"],
                    "provider": self.models_info[model]["provider"],
                    "type": self.models_info[model]["type"],
                    "estimated_cost": estimate["cost_estimate"]["total_cost"],
                    "input_tokens": estimate["input_tokens"],
                    "estimated_output_tokens": estimate["estimated_output_tokens"]
                }
        
        # Ordenar por custo
        sorted_comparison = dict(sorted(
            comparison.items(),
            key=lambda x: x[1]["estimated_cost"]
        ))
        
        return sorted_comparison

# Função de teste
def test_calculator():
    """Testa a calculadora"""
    print("🧮 Testando Calculadora OpenRouter")
    print("=" * 50)
    
    calculator = OpenRouterCalculator()
    
    # Testar contagem de tokens
    test_text = "Olá! Como você está hoje? Este é um teste da calculadora de tokens."
    tokens = calculator.count_tokens(test_text)
    print(f"Texto: '{test_text}'")
    print(f"Tokens: {tokens}")
    
    # Testar cálculo de custo
    cost = calculator.calculate_cost(100, 50, "anthropic/claude-3-sonnet")
    print(f"\nCusto para 100 input + 50 output tokens (Claude 3 Sonnet): ${cost['total_cost']}")
    
    # Testar estimativa
    estimate = calculator.estimate_cost(test_text, "google/gemini-1.5-flash")
    print(f"\nEstimativa para Gemini 1.5 Flash:")
    print(f"- Input tokens: {estimate['input_tokens']}")
    print(f"- Output estimado: {estimate['estimated_output_tokens']}")
    print(f"- Custo estimado: ${estimate['cost_estimate']['total_cost']}")
    
    # Listar modelos gratuitos
    free_models = calculator.get_free_models()
    print(f"\nModelos gratuitos ({len(free_models)}):")
    for model in free_models[:5]:  # Mostrar apenas os primeiros 5
        info = calculator.get_model_info(model)
        print(f"- {info['name']} ({model})")
    
    # Comparação de custos
    print(f"\nComparação de custos:")
    comparison = calculator.get_cost_comparison(test_text, [
        "google/gemini-1.5-flash",
        "anthropic/claude-3-sonnet",
        "openai/gpt-4o-mini"
    ])
    
    for model, info in comparison.items():
        print(f"- {info['name']}: ${info['estimated_cost']} ({info['type']})")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_calculator() 