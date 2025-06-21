#!/usr/bin/env python3
"""
Agente Inteligente de Gestão de Fluxo de MCPs
Protótipo para demonstração de viabilidade
"""

import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import sqlite3
from datetime import datetime

# Importar componentes existentes
try:
    from mcp_manager import MCPManager
    from ai_agente_mcp import OpenRouterClient
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que mcp_manager.py e ai_agente_mcp.py estão disponíveis")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Resultado de uma tarefa executada"""
    task_id: str
    prompt: str
    mcps_used: List[str]
    success: bool
    duration: float
    resource_usage: Dict[str, float]
    error_message: Optional[str] = None
    performance_score: float = 0.0

@dataclass
class MCPAnalysis:
    """Análise de MCPs necessários para uma tarefa"""
    mcps_required: List[str]
    priority: str  # "alta", "média", "baixa"
    estimated_duration: float
    resource_intensity: str  # "baixa", "média", "alta"
    confidence: float  # 0.0 a 1.0
    dependencies: List[str] = None

class IntelligentPromptAnalyzer:
    """Analisador inteligente de prompts usando LLM"""
    
    def __init__(self, llm_client: Optional[OpenRouterClient] = None):
        self.llm_client = llm_client
        self.mcp_knowledge_base = self.load_mcp_knowledge()
        self.usage_history = []
        
    def load_mcp_knowledge(self) -> Dict[str, Any]:
        """Carrega base de conhecimento dos MCPs"""
        return {
            "filesystem": {
                "description": "Acesso ao sistema de arquivos",
                "capabilities": ["leitura", "escrita", "criação", "exclusão"],
                "keywords": ["arquivo", "file", "ler", "escrever", "criar", "deletar"],
                "resource_intensity": "baixa",
                "dependencies": []
            },
            "browser-tools": {
                "description": "Automação de navegador web",
                "capabilities": ["navegação", "screenshots", "scraping"],
                "keywords": ["web", "navegar", "site", "url", "browser", "internet"],
                "resource_intensity": "média",
                "dependencies": []
            },
            "github": {
                "description": "Controle de repositórios Git",
                "capabilities": ["commit", "push", "pull", "merge"],
                "keywords": ["git", "commit", "push", "repositório", "github"],
                "resource_intensity": "baixa",
                "dependencies": []
            },
            "postgres": {
                "description": "Banco de dados PostgreSQL",
                "capabilities": ["queries", "schema", "dados"],
                "keywords": ["banco", "database", "sql", "query", "postgres"],
                "resource_intensity": "média",
                "dependencies": []
            },
            "ollama": {
                "description": "Modelos de IA locais",
                "capabilities": ["inferência", "chat", "análise"],
                "keywords": ["ollama", "modelo local", "cpu", "ia local"],
                "resource_intensity": "alta",
                "dependencies": []
            },
            "google-maps": {
                "description": "Busca e mapas",
                "capabilities": ["busca", "localização", "direções"],
                "keywords": ["buscar", "pesquisar", "google", "mapa", "localização"],
                "resource_intensity": "baixa",
                "dependencies": []
            }
        }
    
    def analyze_prompt_intelligently(self, prompt: str) -> MCPAnalysis:
        """Análise inteligente usando LLM ou fallback para análise baseada em palavras-chave"""
        
        if self.llm_client:
            return self._analyze_with_llm(prompt)
        else:
            return self._analyze_with_keywords(prompt)
    
    def _analyze_with_llm(self, prompt: str) -> MCPAnalysis:
        """Análise usando LLM"""
        try:
            system_prompt = f"""
            Analise o prompt e determine quais MCPs são necessários.
            
            MCPs disponíveis: {json.dumps(self.mcp_knowledge_base, indent=2)}
            
            Considere:
            1. Complexidade da tarefa
            2. Dependências entre MCPs
            3. Recursos necessários
            4. Histórico de uso similar
            
            Retorne JSON com:
            - mcps_required: lista de MCPs necessários
            - priority: alta/média/baixa
            - estimated_duration: tempo estimado em segundos
            - resource_intensity: baixa/média/alta
            - confidence: 0.0 a 1.0
            - dependencies: lista de dependências
            """
            
            response = self.llm_client.chat_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            
            # Tentar extrair JSON da resposta
            try:
                result = json.loads(response.content)
                return MCPAnalysis(**result)
            except:
                # Fallback para análise de palavras-chave
                return self._analyze_with_keywords(prompt)
                
        except Exception as e:
            logger.warning(f"Erro na análise LLM: {e}, usando fallback")
            return self._analyze_with_keywords(prompt)
    
    def _analyze_with_keywords(self, prompt: str) -> MCPAnalysis:
        """Análise baseada em palavras-chave (fallback)"""
        prompt_lower = prompt.lower()
        mcps_required = []
        confidence = 0.7  # Confiança base para análise de palavras-chave
        
        # Análise baseada em palavras-chave
        for mcp_name, mcp_info in self.mcp_knowledge_base.items():
            keywords = mcp_info["keywords"]
            if any(keyword in prompt_lower for keyword in keywords):
                mcps_required.append(mcp_name)
        
        # Determinar prioridade baseada no número de MCPs
        if len(mcps_required) > 3:
            priority = "alta"
        elif len(mcps_required) > 1:
            priority = "média"
        else:
            priority = "baixa"
        
        # Estimar duração baseada na complexidade
        estimated_duration = len(mcps_required) * 30  # 30 segundos por MCP
        
        # Determinar intensidade de recursos
        resource_intensity = "baixa"
        for mcp in mcps_required:
            if self.mcp_knowledge_base[mcp]["resource_intensity"] == "alta":
                resource_intensity = "alta"
                break
            elif self.mcp_knowledge_base[mcp]["resource_intensity"] == "média":
                resource_intensity = "média"
        
        return MCPAnalysis(
            mcps_required=mcps_required,
            priority=priority,
            estimated_duration=estimated_duration,
            resource_intensity=resource_intensity,
            confidence=confidence,
            dependencies=[]
        )

class ResourceMonitor:
    """Monitor de recursos do sistema"""
    
    def __init__(self):
        self.mcp_metrics = {}
        self.system_metrics = {}
        self.monitoring_active = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Monitoramento de recursos iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Monitoramento de recursos parado")
    
    def _monitor_loop(self):
        """Loop de monitoramento"""
        while self.monitoring_active:
            try:
                # Monitorar recursos do sistema
                self.system_metrics = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                    "timestamp": datetime.now().isoformat()
                }
                
                time.sleep(5)  # Atualizar a cada 5 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(10)
    
    def get_available_resources(self) -> Dict[str, float]:
        """Retorna recursos disponíveis"""
        return {
            "cpu_available": 100 - self.system_metrics.get("cpu_percent", 0),
            "memory_available": 100 - self.system_metrics.get("memory_percent", 0),
            "disk_available": 100 - self.system_metrics.get("disk_percent", 0)
        }
    
    def can_start_mcp(self, mcp_name: str, resource_intensity: str) -> bool:
        """Verifica se pode iniciar um MCP baseado nos recursos"""
        available = self.get_available_resources()
        
        # Critérios baseados na intensidade de recursos
        if resource_intensity == "alta":
            return available["cpu_available"] > 30 and available["memory_available"] > 40
        elif resource_intensity == "média":
            return available["cpu_available"] > 20 and available["memory_available"] > 30
        else:  # baixa
            return available["cpu_available"] > 10 and available["memory_available"] > 20

class LearningSystem:
    """Sistema de aprendizado para otimização"""
    
    def __init__(self, db_path: str = "mcp_learning.db"):
        self.db_path = db_path
        self.usage_patterns = {}
        self.success_metrics = {}
        self.init_database()
    
    def init_database(self):
        """Inicializa banco de dados para aprendizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS task_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT,
                        prompt TEXT,
                        mcps_used TEXT,
                        success BOOLEAN,
                        duration REAL,
                        resource_usage TEXT,
                        performance_score REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS mcp_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_hash TEXT UNIQUE,
                        mcps_combination TEXT,
                        success_rate REAL,
                        avg_duration REAL,
                        avg_performance REAL,
                        usage_count INTEGER DEFAULT 0
                    )
                """)
                
                conn.commit()
                logger.info("Banco de dados de aprendizado inicializado")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    def learn_from_task(self, task_result: TaskResult):
        """Aprende com o resultado de uma tarefa"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Salvar resultado da tarefa
                conn.execute("""
                    INSERT INTO task_history 
                    (task_id, prompt, mcps_used, success, duration, resource_usage, performance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_result.task_id,
                    task_result.prompt,
                    json.dumps(task_result.mcps_used),
                    task_result.success,
                    task_result.duration,
                    json.dumps(task_result.resource_usage),
                    task_result.performance_score
                ))
                
                # Atualizar padrões de uso
                pattern_hash = self._hash_mcp_combination(task_result.mcps_used)
                self._update_pattern(pattern_hash, task_result)
                
                conn.commit()
                logger.info(f"Aprendizado registrado para tarefa {task_result.task_id}")
                
        except Exception as e:
            logger.error(f"Erro ao salvar aprendizado: {e}")
    
    def _hash_mcp_combination(self, mcps: List[str]) -> str:
        """Gera hash para combinação de MCPs"""
        return hash(tuple(sorted(mcps)))
    
    def _update_pattern(self, pattern_hash: str, task_result: TaskResult):
        """Atualiza padrão de uso"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar se padrão existe
                cursor = conn.execute(
                    "SELECT * FROM mcp_patterns WHERE pattern_hash = ?",
                    (pattern_hash,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Atualizar padrão existente
                    new_success_rate = (existing[3] + (1 if task_result.success else 0)) / 2
                    new_avg_duration = (existing[4] + task_result.duration) / 2
                    new_avg_performance = (existing[5] + task_result.performance_score) / 2
                    new_usage_count = existing[6] + 1
                    
                    conn.execute("""
                        UPDATE mcp_patterns 
                        SET success_rate = ?, avg_duration = ?, avg_performance = ?, usage_count = ?
                        WHERE pattern_hash = ?
                    """, (new_success_rate, new_avg_duration, new_avg_performance, new_usage_count, pattern_hash))
                else:
                    # Criar novo padrão
                    conn.execute("""
                        INSERT INTO mcp_patterns 
                        (pattern_hash, mcps_combination, success_rate, avg_duration, avg_performance, usage_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        pattern_hash,
                        json.dumps(task_result.mcps_used),
                        1.0 if task_result.success else 0.0,
                        task_result.duration,
                        task_result.performance_score,
                        1
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao atualizar padrão: {e}")
    
    def optimize_mcp_selection(self, analysis: MCPAnalysis, available_resources: Dict[str, float]) -> List[str]:
        """Otimiza seleção de MCPs baseado em aprendizado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Buscar padrões similares
                cursor = conn.execute("""
                    SELECT mcps_combination, success_rate, avg_performance, usage_count
                    FROM mcp_patterns
                    WHERE success_rate > 0.7
                    ORDER BY avg_performance DESC, usage_count DESC
                    LIMIT 5
                """)
                
                patterns = cursor.fetchall()
                
                if patterns:
                    # Usar padrão com melhor performance
                    best_pattern = patterns[0]
                    mcps_combination = json.loads(best_pattern[0])
                    
                    # Filtrar MCPs baseado nos recursos disponíveis
                    filtered_mcps = []
                    for mcp in mcps_combination:
                        if mcp in analysis.mcps_required:
                            filtered_mcps.append(mcp)
                    
                    if filtered_mcps:
                        logger.info(f"Usando padrão otimizado: {filtered_mcps}")
                        return filtered_mcps
                
                # Fallback para análise original
                return analysis.mcps_required
                
        except Exception as e:
            logger.error(f"Erro na otimização: {e}")
            return analysis.mcps_required

class MCPFlowAgent:
    """Agente principal de gestão de fluxo de MCPs"""
    
    def __init__(self, config_file: str = "config/flow_agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Inicializar componentes
        self.mcp_manager = MCPManager()
        
        # Inicializar LLM client se configurado
        self.llm_client = None
        if self.config.get("openrouter_api_key"):
            self.llm_client = OpenRouterClient(self.config["openrouter_api_key"])
        
        # Inicializar componentes do agente
        self.prompt_analyzer = IntelligentPromptAnalyzer(self.llm_client)
        self.resource_monitor = ResourceMonitor()
        self.learning_system = LearningSystem()
        
        # Estado do agente
        self.active_tasks = {}
        self.task_counter = 0
        
        # Iniciar monitoramento
        self.resource_monitor.start_monitoring()
        
        logger.info("MCPFlowAgent inicializado com sucesso")
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do agente"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Configuração padrão
                default_config = {
                    "openrouter_api_key": "",
                    "default_model": "anthropic/claude-3-haiku",
                    "max_concurrent_tasks": 5,
                    "resource_threshold": {
                        "cpu": 80,
                        "memory": 85,
                        "disk": 90
                    },
                    "learning_enabled": True,
                    "monitoring_enabled": True
                }
                
                # Salvar configuração padrão
                Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def process_task(self, prompt: str) -> TaskResult:
        """Processa uma tarefa completa"""
        start_time = time.time()
        task_id = f"task_{self.task_counter:06d}"
        self.task_counter += 1
        
        logger.info(f"Iniciando tarefa {task_id}: {prompt[:50]}...")
        
        try:
            # 1. Análise inteligente do prompt
            analysis = self.prompt_analyzer.analyze_prompt_intelligently(prompt)
            logger.info(f"Análise: {analysis.mcps_required} MCPs necessários")
            
            # 2. Verificação de recursos disponíveis
            available_resources = self.resource_monitor.get_available_resources()
            logger.info(f"Recursos disponíveis: {available_resources}")
            
            # 3. Otimização baseada em histórico
            if self.config.get("learning_enabled", True):
                optimized_mcps = self.learning_system.optimize_mcp_selection(analysis, available_resources)
            else:
                optimized_mcps = analysis.mcps_required
            
            # 4. Verificar se pode iniciar MCPs
            mcps_to_start = []
            for mcp in optimized_mcps:
                if self.resource_monitor.can_start_mcp(mcp, analysis.resource_intensity):
                    mcps_to_start.append(mcp)
                else:
                    logger.warning(f"Recursos insuficientes para MCP {mcp}")
            
            # 5. Executar plano
            success = self._execute_mcp_plan(mcps_to_start, prompt)
            
            # 6. Calcular métricas
            duration = time.time() - start_time
            resource_usage = self.resource_monitor.system_metrics.copy()
            performance_score = self._calculate_performance_score(success, duration, len(mcps_to_start))
            
            # 7. Criar resultado
            task_result = TaskResult(
                task_id=task_id,
                prompt=prompt,
                mcps_used=mcps_to_start,
                success=success,
                duration=duration,
                resource_usage=resource_usage,
                performance_score=performance_score
            )
            
            # 8. Aprender com o resultado
            if self.config.get("learning_enabled", True):
                self.learning_system.learn_from_task(task_result)
            
            logger.info(f"Tarefa {task_id} concluída: {'sucesso' if success else 'falha'}")
            return task_result
            
        except Exception as e:
            logger.error(f"Erro na tarefa {task_id}: {e}")
            duration = time.time() - start_time
            
            return TaskResult(
                task_id=task_id,
                prompt=prompt,
                mcps_used=[],
                success=False,
                duration=duration,
                resource_usage={},
                performance_score=0.0,
                error_message=str(e)
            )
    
    def _execute_mcp_plan(self, mcps_to_start: List[str], prompt: str) -> bool:
        """Executa plano de MCPs"""
        try:
            # Parar MCPs não necessários
            current_mcps = [name for name, mcp in self.mcp_manager.mcps.items() if mcp.enabled]
            mcps_to_stop = [name for name in current_mcps if name not in mcps_to_start]
            
            for mcp_name in mcps_to_stop:
                self.mcp_manager.stop_mcp(mcp_name)
                logger.info(f"MCP {mcp_name} parado")
            
            # Iniciar MCPs necessários
            for mcp_name in mcps_to_start:
                if not self.mcp_manager.mcps[mcp_name].enabled:
                    if self.mcp_manager.start_mcp(mcp_name):
                        logger.info(f"MCP {mcp_name} iniciado")
                    else:
                        logger.error(f"Erro ao iniciar MCP {mcp_name}")
                        return False
            
            # Aguardar inicialização
            time.sleep(2)
            
            # Verificar se todos os MCPs estão ativos
            active_mcps = [name for name, mcp in self.mcp_manager.mcps.items() if mcp.enabled]
            all_started = all(mcp in active_mcps for mcp in mcps_to_start)
            
            if all_started:
                logger.info(f"Todos os MCPs iniciados: {mcps_to_start}")
                return True
            else:
                logger.error(f"Alguns MCPs não iniciaram: {mcps_to_start}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar plano: {e}")
            return False
    
    def _calculate_performance_score(self, success: bool, duration: float, mcp_count: int) -> float:
        """Calcula score de performance"""
        if not success:
            return 0.0
        
        # Score baseado em duração e número de MCPs
        base_score = 1.0
        
        # Penalizar por duração longa
        if duration > 60:
            duration_penalty = (duration - 60) / 60 * 0.3
            base_score -= duration_penalty
        
        # Penalizar por muitos MCPs
        if mcp_count > 3:
            mcp_penalty = (mcp_count - 3) * 0.1
            base_score -= mcp_penalty
        
        return max(0.0, min(1.0, base_score))
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retorna status atual do agente"""
        return {
            "active_tasks": len(self.active_tasks),
            "total_tasks_processed": self.task_counter,
            "learning_enabled": self.config.get("learning_enabled", True),
            "monitoring_enabled": self.config.get("monitoring_enabled", True),
            "llm_configured": self.llm_client is not None,
            "available_resources": self.resource_monitor.get_available_resources(),
            "active_mcps": [name for name, mcp in self.mcp_manager.mcps.items() if mcp.enabled]
        }
    
    def shutdown(self):
        """Desliga o agente de forma segura"""
        logger.info("Desligando MCPFlowAgent...")
        
        # Parar monitoramento
        self.resource_monitor.stop_monitoring()
        
        # Parar todos os MCPs ativos
        active_mcps = [name for name, mcp in self.mcp_manager.mcps.items() if mcp.enabled]
        for mcp_name in active_mcps:
            self.mcp_manager.stop_mcp(mcp_name)
        
        logger.info("MCPFlowAgent desligado com sucesso")

def main():
    """Função principal para teste do agente"""
    print("🚀 Iniciando MCPFlowAgent...")
    
    # Criar agente
    agent = MCPFlowAgent()
    
    # Exemplos de teste
    test_prompts = [
        "Crie um arquivo de texto com o conteúdo 'Hello World'",
        "Navegue para google.com e tire um screenshot",
        "Faça um commit no repositório Git com a mensagem 'Update'",
        "Execute uma query SQL no banco de dados PostgreSQL"
    ]
    
    print("\n📝 Testando análise de prompts:")
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        analysis = agent.prompt_analyzer.analyze_prompt_intelligently(prompt)
        print(f"MCPs sugeridos: {analysis.mcps_required}")
        print(f"Prioridade: {analysis.priority}")
        print(f"Duração estimada: {analysis.estimated_duration}s")
        print(f"Intensidade de recursos: {analysis.resource_intensity}")
    
    print("\n🔄 Testando processamento de tarefa:")
    result = agent.process_task("Crie um arquivo de teste")
    print(f"Resultado: {asdict(result)}")
    
    print("\n📊 Status do agente:")
    status = agent.get_agent_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Desligar agente
    agent.shutdown()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main() 