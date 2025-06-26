#!/usr/bin/env python3
"""
Teste Completo do Sistema Integrado de Conhecimento
Testa todos os componentes: LangChain, TensorFlow, Docker, N8N, MCPs
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedSystemTester:
    """Testador completo do sistema integrado"""
    
    def __init__(self):
        self.test_results = {
            "knowledge_system": {},
            "docker_manager": {},
            "n8n_manager": {},
            "mcp_integration": {},
            "document_processing": {},
            "overall": {}
        }
        self.start_time = time.time()
    
    def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("🚀 Iniciando testes do Sistema Integrado de Conhecimento")
        
        try:
            # Teste 1: Sistema de Conhecimento
            self.test_knowledge_system()
            
            # Teste 2: Processamento de Documentos
            self.test_document_processing()
            
            # Teste 3: Docker Manager
            self.test_docker_manager()
            
            # Teste 4: N8N Manager
            self.test_n8n_manager()
            
            # Teste 5: MCP Integration
            self.test_mcp_integration()
            
            # Teste 6: Integração Completa
            self.test_integration()
            
            # Gerar relatório
            self.generate_report()
            
        except Exception as e:
            logger.error(f"❌ Erro durante os testes: {e}")
            self.test_results["overall"]["error"] = str(e)
    
    def test_knowledge_system(self):
        """Testa o sistema de conhecimento"""
        logger.info("🧠 Testando Sistema de Conhecimento...")
        
        try:
            # Importar sistema
            from knowledge_enhancement_system import KnowledgeEnhancementSystem
            
            # Criar sistema
            system = KnowledgeEnhancementSystem()
            
            # Testar status
            status = system.get_system_status()
            
            self.test_results["knowledge_system"] = {
                "status": "success",
                "components": {
                    "tensorflow_available": status.get("tensorflow_available", False),
                    "langchain_available": status.get("langchain_available", False),
                    "document_processing_available": status.get("document_processing_available", False)
                },
                "metrics": {
                    "processed_documents": status.get("processed_documents", 0),
                    "knowledge_base_size": status.get("knowledge_base_size", 0),
                    "queue_size": status.get("queue_size", 0)
                }
            }
            
            logger.info("✅ Sistema de Conhecimento testado com sucesso")
            
        except ImportError as e:
            logger.warning(f"⚠️ Sistema de conhecimento não disponível: {e}")
            self.test_results["knowledge_system"] = {
                "status": "not_available",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro no sistema de conhecimento: {e}")
            self.test_results["knowledge_system"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_document_processing(self):
        """Testa processamento de documentos"""
        logger.info("📄 Testando Processamento de Documentos...")
        
        try:
            from knowledge_enhancement_system import DocumentProcessor
            
            processor = DocumentProcessor()
            
            # Criar arquivo de teste
            test_file = "test_document.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("Este é um documento de teste para verificar o processamento de documentos.")
            
            # Testar processamento
            result = processor.process_document(test_file)
            
            # Limpar arquivo de teste
            os.remove(test_file)
            
            self.test_results["document_processing"] = {
                "status": "success",
                "supported_formats": len(processor.supported_formats),
                "test_result": result.get("status", "unknown"),
                "content_length": len(result.get("content", ""))
            }
            
            logger.info("✅ Processamento de documentos testado com sucesso")
            
        except ImportError as e:
            logger.warning(f"⚠️ Processador de documentos não disponível: {e}")
            self.test_results["document_processing"] = {
                "status": "not_available",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro no processamento de documentos: {e}")
            self.test_results["document_processing"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_docker_manager(self):
        """Testa gerenciador Docker"""
        logger.info("🐳 Testando Docker Manager...")
        
        try:
            from docker_n8n_interface import DockerManager
            
            docker = DockerManager()
            
            # Testar conexão
            containers = docker.get_containers()
            images = docker.get_images()
            
            self.test_results["docker_manager"] = {
                "status": "success",
                "containers_count": len(containers),
                "images_count": len(images),
                "connection": docker.client is not None
            }
            
            logger.info("✅ Docker Manager testado com sucesso")
            
        except ImportError as e:
            logger.warning(f"⚠️ Docker Manager não disponível: {e}")
            self.test_results["docker_manager"] = {
                "status": "not_available",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro no Docker Manager: {e}")
            self.test_results["docker_manager"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_n8n_manager(self):
        """Testa gerenciador N8N"""
        logger.info("🔄 Testando N8N Manager...")
        
        try:
            from docker_n8n_interface import N8NManager
            
            # Testar conexão local
            n8n = N8NManager("http://localhost:5678")
            
            # Testar conexão
            connection = n8n.test_connection()
            
            if connection:
                workflows = n8n.get_workflows()
                self.test_results["n8n_manager"] = {
                    "status": "success",
                    "connection": True,
                    "workflows_count": len(workflows)
                }
                logger.info("✅ N8N Manager conectado com sucesso")
            else:
                self.test_results["n8n_manager"] = {
                    "status": "not_connected",
                    "connection": False,
                    "note": "N8N não está rodando localmente"
                }
                logger.info("⚠️ N8N não está rodando localmente")
            
        except ImportError as e:
            logger.warning(f"⚠️ N8N Manager não disponível: {e}")
            self.test_results["n8n_manager"] = {
                "status": "not_available",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro no N8N Manager: {e}")
            self.test_results["n8n_manager"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_mcp_integration(self):
        """Testa integração MCP"""
        logger.info("🔌 Testando MCP Integration...")
        
        try:
            from docker_n8n_interface import MCPIntegration
            
            mcp = MCPIntegration()
            
            # Testar criação de workflows
            webhook_workflow = mcp.create_webhook_workflow(
                "http://localhost:5678/webhook",
                {"test": "data"}
            )
            
            data_workflow = mcp.create_data_architecture_workflow(
                "postgres", "filesystem"
            )
            
            self.test_results["mcp_integration"] = {
                "status": "success",
                "available_mcps": len(mcp.available_mcps),
                "webhook_workflow_created": "webhook_trigger" in str(webhook_workflow),
                "data_workflow_created": "source_node" in str(data_workflow)
            }
            
            logger.info("✅ MCP Integration testado com sucesso")
            
        except ImportError as e:
            logger.warning(f"⚠️ MCP Integration não disponível: {e}")
            self.test_results["mcp_integration"] = {
                "status": "not_available",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro no MCP Integration: {e}")
            self.test_results["mcp_integration"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_integration(self):
        """Testa integração completa"""
        logger.info("🔗 Testando Integração Completa...")
        
        try:
            # Testar se todos os componentes podem trabalhar juntos
            components_status = []
            
            for component, result in self.test_results.items():
                if component != "overall":
                    if result.get("status") == "success":
                        components_status.append(True)
                    else:
                        components_status.append(False)
            
            # Calcular viabilidade
            available_components = sum(components_status)
            total_components = len(components_status)
            viability_percentage = (available_components / total_components) * 100
            
            self.test_results["overall"] = {
                "status": "completed",
                "total_components": total_components,
                "available_components": available_components,
                "viability_percentage": round(viability_percentage, 2),
                "execution_time": round(time.time() - self.start_time, 2)
            }
            
            logger.info(f"✅ Integração completa testada. Viabilidade: {viability_percentage:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Erro na integração completa: {e}")
            self.test_results["overall"] = {
                "status": "error",
                "error": str(e)
            }
    
    def generate_report(self):
        """Gera relatório completo dos testes"""
        logger.info("📊 Gerando relatório de testes...")
        
        # Calcular métricas
        total_tests = len(self.test_results) - 1  # Excluir 'overall'
        successful_tests = sum(1 for component, result in self.test_results.items() 
                             if component != "overall" and result.get("status") == "success")
        
        # Criar relatório
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": round((successful_tests / total_tests) * 100, 2),
                "execution_time": self.test_results["overall"].get("execution_time", 0)
            },
            "detailed_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Salvar relatório
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Exibir resumo
        self.display_summary(report)
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Verificar componentes não disponíveis
        for component, result in self.test_results.items():
            if component != "overall":
                if result.get("status") == "not_available":
                    recommendations.append(f"Instalar dependências para {component}")
                elif result.get("status") == "error":
                    recommendations.append(f"Corrigir erros em {component}")
        
        # Recomendações específicas
        if self.test_results.get("knowledge_system", {}).get("status") != "success":
            recommendations.append("Configurar OpenAI API key para LangChain")
        
        if self.test_results.get("docker_manager", {}).get("status") != "success":
            recommendations.append("Verificar instalação e permissões do Docker")
        
        if self.test_results.get("n8n_manager", {}).get("status") == "not_connected":
            recommendations.append("Iniciar N8N localmente ou configurar URL remota")
        
        # Recomendações gerais
        viability = self.test_results["overall"].get("viability_percentage", 0)
        if viability < 50:
            recommendations.append("Sistema com baixa viabilidade - revisar dependências")
        elif viability < 80:
            recommendations.append("Sistema com viabilidade média - otimizar componentes")
        else:
            recommendations.append("Sistema com alta viabilidade - pronto para uso")
        
        return recommendations
    
    def display_summary(self, report):
        """Exibe resumo dos testes"""
        summary = report["test_summary"]
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTES - SISTEMA INTEGRADO DE CONHECIMENTO")
        print("="*60)
        
        print(f"\n⏰ Timestamp: {summary['timestamp']}")
        print(f"🧪 Total de Testes: {summary['total_tests']}")
        print(f"✅ Testes Bem-sucedidos: {summary['successful_tests']}")
        print(f"📈 Taxa de Sucesso: {summary['success_rate']}%")
        print(f"⏱️ Tempo de Execução: {summary['execution_time']}s")
        
        print(f"\n🔗 Viabilidade Geral: {self.test_results['overall'].get('viability_percentage', 0)}%")
        
        print("\n📋 Resultados Detalhados:")
        for component, result in self.test_results.items():
            if component != "overall":
                status_icon = "✅" if result.get("status") == "success" else "❌"
                print(f"  {status_icon} {component}: {result.get('status', 'unknown')}")
        
        print("\n💡 Recomendações:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    print("🧠 Sistema Integrado de Conhecimento - Teste Completo")
    print("="*60)
    
    # Criar e executar testes
    tester = IntegratedSystemTester()
    tester.run_all_tests()
    
    print("\n🎉 Testes concluídos!")

if __name__ == "__main__":
    main() 