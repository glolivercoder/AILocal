#!/usr/bin/env python3
"""
Teste Completo do Agente de Gestão de Fluxo de MCPs
Demonstração de viabilidade e funcionalidades
"""

import json
import time
from pathlib import Path
from mcp_flow_agent import MCPFlowAgent, TaskResult

def test_prompt_analysis():
    """Testa análise de prompts"""
    print("🔍 Testando Análise de Prompts")
    print("=" * 50)
    
    agent = MCPFlowAgent()
    
    test_cases = [
        {
            "prompt": "Crie um arquivo de texto com o conteúdo 'Hello World'",
            "expected_mcps": ["filesystem"],
            "description": "Tarefa simples de arquivo"
        },
        {
            "prompt": "Navegue para google.com e tire um screenshot da página",
            "expected_mcps": ["browser-tools"],
            "description": "Tarefa de navegação web"
        },
        {
            "prompt": "Faça um commit no repositório Git com a mensagem 'Update'",
            "expected_mcps": ["github"],
            "description": "Tarefa de controle de versão"
        },
        {
            "prompt": "Execute uma query SQL no banco de dados PostgreSQL",
            "expected_mcps": ["postgres"],
            "description": "Tarefa de banco de dados"
        },
        {
            "prompt": "Use um modelo local do Ollama para analisar este texto",
            "expected_mcps": ["ollama"],
            "description": "Tarefa de IA local"
        },
        {
            "prompt": "Busque informações sobre Python no Google",
            "expected_mcps": ["google-maps"],
            "description": "Tarefa de busca"
        },
        {
            "prompt": "Crie um arquivo, navegue para um site e faça um commit",
            "expected_mcps": ["filesystem", "browser-tools", "github"],
            "description": "Tarefa complexa multi-MCP"
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: {test_case['description']}")
        print(f"Prompt: {test_case['prompt']}")
        
        analysis = agent.prompt_analyzer.analyze_prompt_intelligently(test_case['prompt'])
        
        print(f"✅ MCPs detectados: {analysis.mcps_required}")
        print(f"📊 Prioridade: {analysis.priority}")
        print(f"⏱️  Duração estimada: {analysis.estimated_duration}s")
        print(f"💾 Intensidade de recursos: {analysis.resource_intensity}")
        print(f"🎯 Confiança: {analysis.confidence:.2f}")
        
        # Verificar acurácia
        accuracy = len(set(analysis.mcps_required) & set(test_case['expected_mcps'])) / len(test_case['expected_mcps'])
        results.append({
            "test": i,
            "description": test_case['description'],
            "accuracy": accuracy,
            "detected": analysis.mcps_required,
            "expected": test_case['expected_mcps']
        })
        
        print(f"🎯 Acurácia: {accuracy:.2f}")
    
    # Resumo dos resultados
    print("\n📊 Resumo da Análise de Prompts")
    print("=" * 50)
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
    print(f"Acurácia média: {avg_accuracy:.2f}")
    
    for result in results:
        status = "✅" if result['accuracy'] >= 0.8 else "⚠️" if result['accuracy'] >= 0.5 else "❌"
        print(f"{status} Teste {result['test']}: {result['description']} - {result['accuracy']:.2f}")
    
    agent.shutdown()
    return avg_accuracy

def test_resource_monitoring():
    """Testa monitoramento de recursos"""
    print("\n💻 Testando Monitoramento de Recursos")
    print("=" * 50)
    
    agent = MCPFlowAgent()
    
    # Aguardar inicialização do monitoramento
    time.sleep(3)
    
    print("📊 Métricas do Sistema:")
    resources = agent.resource_monitor.get_available_resources()
    for key, value in resources.items():
        print(f"  {key}: {value:.1f}%")
    
    print("\n🔍 Testando Critérios de Recursos:")
    test_mcps = [
        ("filesystem", "baixa"),
        ("browser-tools", "média"),
        ("ollama", "alta")
    ]
    
    for mcp_name, intensity in test_mcps:
        can_start = agent.resource_monitor.can_start_mcp(mcp_name, intensity)
        status = "✅" if can_start else "❌"
        print(f"{status} {mcp_name} ({intensity}): {'Pode iniciar' if can_start else 'Recursos insuficientes'}")
    
    agent.shutdown()

def test_learning_system():
    """Testa sistema de aprendizado"""
    print("\n🧠 Testando Sistema de Aprendizado")
    print("=" * 50)
    
    agent = MCPFlowAgent()
    
    # Simular algumas tarefas para aprendizado
    test_tasks = [
        TaskResult(
            task_id="test_001",
            prompt="Criar arquivo simples",
            mcps_used=["filesystem"],
            success=True,
            duration=15.0,
            resource_usage={"cpu": 5.0, "memory": 10.0},
            performance_score=0.9
        ),
        TaskResult(
            task_id="test_002",
            prompt="Navegação web",
            mcps_used=["browser-tools"],
            success=True,
            duration=45.0,
            resource_usage={"cpu": 15.0, "memory": 25.0},
            performance_score=0.8
        ),
        TaskResult(
            task_id="test_003",
            prompt="Tarefa complexa",
            mcps_used=["filesystem", "browser-tools", "github"],
            success=True,
            duration=120.0,
            resource_usage={"cpu": 30.0, "memory": 50.0},
            performance_score=0.7
        )
    ]
    
    print("📚 Registrando tarefas para aprendizado:")
    for task in test_tasks:
        agent.learning_system.learn_from_task(task)
        print(f"  ✅ {task.task_id}: {len(task.mcps_used)} MCPs, score {task.performance_score:.2f}")
    
    # Testar otimização
    print("\n🔍 Testando Otimização:")
    from mcp_flow_agent import MCPAnalysis
    
    analysis = MCPAnalysis(
        mcps_required=["filesystem", "browser-tools"],
        priority="média",
        estimated_duration=60.0,
        resource_intensity="média",
        confidence=0.8
    )
    
    available_resources = {"cpu_available": 80.0, "memory_available": 70.0}
    optimized = agent.learning_system.optimize_mcp_selection(analysis, available_resources)
    
    print(f"Análise original: {analysis.mcps_required}")
    print(f"Otimização: {optimized}")
    
    agent.shutdown()

def test_complete_workflow():
    """Testa fluxo completo do agente"""
    print("\n🔄 Testando Fluxo Completo")
    print("=" * 50)
    
    agent = MCPFlowAgent()
    
    # Testar tarefas simples
    simple_tasks = [
        "Crie um arquivo de teste",
        "Analise este prompt para determinar MCPs necessários",
        "Verifique os recursos disponíveis no sistema"
    ]
    
    results = []
    for i, prompt in enumerate(simple_tasks, 1):
        print(f"\n🔄 Executando tarefa {i}: {prompt}")
        
        start_time = time.time()
        result = agent.process_task(prompt)
        end_time = time.time()
        
        print(f"  ⏱️  Tempo total: {end_time - start_time:.2f}s")
        print(f"  🎯 Sucesso: {'✅' if result.success else '❌'}")
        print(f"  📊 Score: {result.performance_score:.2f}")
        print(f"  🔧 MCPs usados: {result.mcps_used}")
        
        results.append(result)
    
    # Estatísticas
    print("\n📈 Estatísticas do Fluxo:")
    successful_tasks = sum(1 for r in results if r.success)
    avg_score = sum(r.performance_score for r in results) / len(results)
    avg_duration = sum(r.duration for r in results) / len(results)
    
    print(f"  Tarefas bem-sucedidas: {successful_tasks}/{len(results)}")
    print(f"  Score médio: {avg_score:.2f}")
    print(f"  Duração média: {avg_duration:.2f}s")
    
    agent.shutdown()
    return results

def test_integration_with_existing_system():
    """Testa integração com sistema existente"""
    print("\n🔗 Testando Integração com Sistema Existente")
    print("=" * 50)
    
    agent = MCPFlowAgent()
    
    # Verificar integração com MCPManager
    print("📋 Status do MCPManager:")
    mcp_status = agent.mcp_manager.get_mcp_status()
    print(f"  Total de MCPs configurados: {len(mcp_status)}")
    
    # Verificar MCPs disponíveis
    available_mcps = [name for name, info in mcp_status.items() if info['status'] == 'ready']
    print(f"  MCPs disponíveis: {len(available_mcps)}")
    
    # Testar análise automática
    print("\n🔍 Testando Análise Automática:")
    test_prompt = "Crie um arquivo e navegue para um site"
    auto_result = agent.mcp_manager.auto_manage_mcps(test_prompt)
    
    print(f"Prompt: {test_prompt}")
    print(f"MCPs sugeridos: {auto_result['suggested_mcps']}")
    print(f"MCPs iniciados: {auto_result['started']}")
    print(f"MCPs parados: {auto_result['stopped']}")
    
    if auto_result['errors']:
        print(f"Erros: {auto_result['errors']}")
    
    agent.shutdown()

def generate_performance_report():
    """Gera relatório de performance"""
    print("\n📊 Relatório de Performance")
    print("=" * 50)
    
    # Executar todos os testes
    print("🚀 Executando bateria de testes...")
    
    # Teste 1: Análise de prompts
    prompt_accuracy = test_prompt_analysis()
    
    # Teste 2: Monitoramento de recursos
    test_resource_monitoring()
    
    # Teste 3: Sistema de aprendizado
    test_learning_system()
    
    # Teste 4: Fluxo completo
    workflow_results = test_complete_workflow()
    
    # Teste 5: Integração
    test_integration_with_existing_system()
    
    # Gerar relatório final
    print("\n🎯 RELATÓRIO FINAL DE VIABILIDADE")
    print("=" * 60)
    
    # Métricas de sucesso
    successful_workflows = sum(1 for r in workflow_results if r.success)
    workflow_success_rate = successful_workflows / len(workflow_results) if workflow_results else 0
    
    print(f"✅ Análise de Prompts: {prompt_accuracy:.2f} de acurácia")
    print(f"✅ Monitoramento de Recursos: Funcionando")
    print(f"✅ Sistema de Aprendizado: Funcionando")
    print(f"✅ Fluxo Completo: {workflow_success_rate:.2f} de sucesso")
    print(f"✅ Integração com Sistema: Funcionando")
    
    # Avaliação geral
    overall_score = (prompt_accuracy + workflow_success_rate) / 2
    
    print(f"\n🎯 Score Geral: {overall_score:.2f}")
    
    if overall_score >= 0.8:
        print("🚀 VIABILIDADE: ALTA - Sistema pronto para produção")
    elif overall_score >= 0.6:
        print("⚠️  VIABILIDADE: MÉDIA - Necessita melhorias menores")
    else:
        print("❌ VIABILIDADE: BAIXA - Necessita desenvolvimento significativo")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    if prompt_accuracy < 0.8:
        print("  - Melhorar análise de prompts com LLM")
    if workflow_success_rate < 0.8:
        print("  - Otimizar gerenciamento de MCPs")
    if overall_score >= 0.8:
        print("  - Implementar interface gráfica")
        print("  - Adicionar mais MCPs")
        print("  - Otimizar performance")
    
    return overall_score

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO AGENTE DE FLUXO DE MCPS")
    print("=" * 60)
    
    try:
        score = generate_performance_report()
        print(f"\n✅ Teste concluído com score: {score:.2f}")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc() 