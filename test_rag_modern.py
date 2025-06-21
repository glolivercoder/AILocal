#!/usr/bin/env python3
"""
Teste e Exemplo de Uso do Sistema RAG Moderno
"""

import os
import sys
from pathlib import Path
import logging
from typing import Dict, Any

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from rag_system_modern import (
    ModernRAGSystem, RAGConfig, VectorDBType, EmbeddingModel,
    create_modern_rag_system, create_chromadb_rag_system, create_qdrant_rag_system
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_system_dependencies():
    """Testa dependências do sistema"""
    print("🔍 Testando dependências do sistema...")
    
    dependencies = {
        "LangChain": False,
        "ChromaDB": False,
        "Qdrant": False,
        "SentenceTransformers": False,
        "NumPy": False,
        "Requests": False
    }
    
    try:
        import langchain
        dependencies["LangChain"] = True
    except ImportError:
        pass
    
    try:
        import chromadb
        dependencies["ChromaDB"] = True
    except ImportError:
        pass
    
    try:
        import qdrant_client
        dependencies["Qdrant"] = True
    except ImportError:
        pass
    
    try:
        import sentence_transformers
        dependencies["SentenceTransformers"] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies["NumPy"] = True
    except ImportError:
        pass
    
    try:
        import requests
        dependencies["Requests"] = True
    except ImportError:
        pass
    
    print("\n📋 Status das dependências:")
    for dep, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"  {status} {dep}")
    
    return dependencies

def create_test_documents():
    """Cria documentos de teste"""
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Documento sobre desenvolvimento de apps
    app_dev_content = """
# Desenvolvimento de Aplicações Móveis

## Introdução
O desenvolvimento de aplicações móveis é uma área em constante evolução, com novas tecnologias e frameworks surgindo regularmente.

## Tecnologias Principais

### React Native
React Native é um framework que permite desenvolver aplicações nativas para iOS e Android usando JavaScript e React.

**Vantagens:**
- Código compartilhado entre plataformas
- Performance próxima ao nativo
- Grande comunidade
- Hot reload para desenvolvimento rápido

**Desvantagens:**
- Algumas limitações para funcionalidades muito específicas
- Dependência de bibliotecas nativas para certas funcionalidades

### Flutter
Flutter é o framework do Google para desenvolvimento multiplataforma usando Dart.

**Vantagens:**
- Performance excelente
- UI consistente entre plataformas
- Hot reload
- Crescimento rápido da comunidade

**Desvantagens:**
- Linguagem Dart menos popular
- Tamanho do app pode ser maior

### Desenvolvimento Nativo

#### iOS (Swift/Objective-C)
- Performance máxima
- Acesso completo às APIs do sistema
- Melhor integração com o ecossistema Apple

#### Android (Kotlin/Java)
- Performance máxima
- Acesso completo às APIs do Android
- Flexibilidade total de customização

## Arquitetura de Apps

### MVVM (Model-View-ViewModel)
Padrão recomendado para aplicações modernas, especialmente com frameworks como React Native e Flutter.

### Clean Architecture
Arquitetura que promove separação de responsabilidades e testabilidade.

## Banco de Dados

### SQLite
Banco local padrão para aplicações móveis.

### Realm
Banco de dados objeto-relacional com boa performance.

### Firebase Firestore
Banco NoSQL em nuvem com sincronização em tempo real.

## Segurança

### Autenticação
- OAuth 2.0
- JWT tokens
- Biometria (Touch ID, Face ID, Fingerprint)

### Criptografia
- HTTPS obrigatório
- Criptografia de dados sensíveis
- Keychain/Keystore para armazenamento seguro

### Proteção de APIs
- Rate limiting
- Validação de entrada
- Sanitização de dados

## Deploy

### iOS
- App Store Connect
- TestFlight para beta testing
- Certificados e provisioning profiles

### Android
- Google Play Console
- Play Console Internal Testing
- Assinatura de apps

## Monetização

### Modelos de Negócio
- Freemium
- Assinatura (SaaS)
- Compras in-app
- Publicidade
- Pagamento único

### Ferramentas de Analytics
- Google Analytics
- Firebase Analytics
- Mixpanel
- Amplitude
"""
    
    # Documento sobre SaaS
    saas_content = """
# Desenvolvimento de SaaS (Software as a Service)

## Conceitos Fundamentais

SaaS é um modelo de distribuição de software onde as aplicações são hospedadas por um provedor de serviços e disponibilizadas aos clientes através da internet.

## Arquitetura SaaS

### Multi-tenancy
Arquitetura onde uma única instância da aplicação serve múltiplos clientes (tenants).

**Tipos:**
1. **Single-tenant**: Cada cliente tem sua própria instância
2. **Multi-tenant compartilhado**: Todos os clientes compartilham a mesma instância
3. **Multi-tenant isolado**: Dados separados por tenant na mesma instância

### Microserviços
Arquitetura que divide a aplicação em serviços pequenos e independentes.

**Benefícios:**
- Escalabilidade independente
- Tecnologias diversas
- Desenvolvimento paralelo
- Resiliência

## Stack Tecnológico

### Backend
- **Node.js**: JavaScript no servidor
- **Python**: Django, FastAPI, Flask
- **Java**: Spring Boot
- **C#**: .NET Core
- **Go**: Performance e concorrência

### Frontend
- **React**: Biblioteca JavaScript
- **Vue.js**: Framework progressivo
- **Angular**: Framework completo
- **Svelte**: Compilador moderno

### Banco de Dados
- **PostgreSQL**: Relacional robusto
- **MongoDB**: NoSQL flexível
- **Redis**: Cache e sessões
- **Elasticsearch**: Busca e analytics

### Infraestrutura
- **AWS**: Amazon Web Services
- **Google Cloud**: GCP
- **Azure**: Microsoft Cloud
- **Docker**: Containerização
- **Kubernetes**: Orquestração

## Segurança

### Autenticação e Autorização
- **OAuth 2.0**: Padrão de autorização
- **OpenID Connect**: Camada de identidade
- **SAML**: Security Assertion Markup Language
- **Multi-factor Authentication (MFA)**

### Proteção de Dados
- **GDPR**: Regulamentação europeia
- **LGPD**: Lei brasileira de proteção de dados
- **Criptografia**: Em trânsito e em repouso
- **Backup**: Estratégias de recuperação

## Métricas e KPIs

### Métricas de Negócio
- **MRR**: Monthly Recurring Revenue
- **ARR**: Annual Recurring Revenue
- **Churn Rate**: Taxa de cancelamento
- **LTV**: Lifetime Value
- **CAC**: Customer Acquisition Cost

### Métricas Técnicas
- **Uptime**: Disponibilidade do serviço
- **Response Time**: Tempo de resposta
- **Throughput**: Requisições por segundo
- **Error Rate**: Taxa de erro

## Pricing e Monetização

### Modelos de Preço
- **Freemium**: Versão gratuita limitada
- **Tiered**: Planos escalonados
- **Per-user**: Por usuário
- **Usage-based**: Baseado no uso
- **Enterprise**: Preço customizado

## Deploy e DevOps

### CI/CD
- **GitHub Actions**: Automação GitHub
- **GitLab CI**: Pipeline integrado
- **Jenkins**: Servidor de automação
- **CircleCI**: Integração contínua

### Monitoramento
- **Prometheus**: Métricas
- **Grafana**: Visualização
- **ELK Stack**: Logs
- **Sentry**: Error tracking

### Escalabilidade
- **Load Balancing**: Distribuição de carga
- **Auto Scaling**: Escala automática
- **CDN**: Content Delivery Network
- **Caching**: Estratégias de cache
"""
    
    # Documento sobre MVP
    mvp_content = """
# MVP (Minimum Viable Product) - Guia Completo

## Definição

MVP é a versão mais simples de um produto que pode ser lançada com o mínimo de recursos necessários para validar uma hipótese de negócio.

## Princípios do MVP

### Build-Measure-Learn
Ciclo fundamental do desenvolvimento lean:
1. **Build**: Construir o mínimo necessário
2. **Measure**: Medir resultados e feedback
3. **Learn**: Aprender e iterar

### Validação de Hipóteses
- **Problem-Solution Fit**: O problema existe?
- **Product-Market Fit**: A solução resolve o problema?
- **Business Model Fit**: O modelo de negócio é viável?

## Tipos de MVP

### Landing Page MVP
Página simples para validar interesse e capturar leads.

**Elementos essenciais:**
- Proposta de valor clara
- Call-to-action
- Formulário de cadastro
- Analytics para medir conversão

### Concierge MVP
Serviço manual que simula a experiência automatizada.

**Vantagens:**
- Validação rápida
- Feedback direto
- Baixo custo inicial

### Wizard of Oz MVP
Interface automatizada com processos manuais por trás.

### Prototype MVP
Versão funcional básica com features essenciais.

## Metodologias de Validação

### Lean Startup
Metodologia focada em aprendizado validado e iteração rápida.

### Design Thinking
Abordagem centrada no usuário para inovação.

**Etapas:**
1. **Empatizar**: Entender o usuário
2. **Definir**: Definir o problema
3. **Idear**: Gerar soluções
4. **Prototipar**: Criar protótipos
5. **Testar**: Validar com usuários

### Jobs to be Done
Framework para entender motivações dos clientes.

## Métricas de Validação

### Métricas de Engajamento
- **DAU/MAU**: Daily/Monthly Active Users
- **Session Duration**: Tempo de sessão
- **Page Views**: Visualizações de página
- **Bounce Rate**: Taxa de rejeição

### Métricas de Conversão
- **Conversion Rate**: Taxa de conversão
- **Funnel Analysis**: Análise de funil
- **A/B Testing**: Testes comparativos

### Métricas de Retenção
- **Retention Rate**: Taxa de retenção
- **Cohort Analysis**: Análise de coorte
- **Churn Rate**: Taxa de abandono

## Ferramentas para MVP

### No-Code/Low-Code
- **Bubble**: Desenvolvimento visual
- **Webflow**: Design e desenvolvimento
- **Airtable**: Banco de dados visual
- **Zapier**: Automação de processos

### Prototipagem
- **Figma**: Design de interfaces
- **InVision**: Prototipagem interativa
- **Marvel**: Prototipagem simples
- **Framer**: Prototipagem avançada

### Analytics
- **Google Analytics**: Web analytics
- **Mixpanel**: Event tracking
- **Hotjar**: Heatmaps e gravações
- **Amplitude**: Product analytics

## Estratégias de Lançamento

### Soft Launch
Lançamento limitado para grupo restrito de usuários.

### Beta Testing
Teste com usuários reais antes do lançamento oficial.

### Product Hunt
Plataforma para lançamento de produtos tech.

### Growth Hacking
Técnicas de crescimento rápido e escalável.

## Erros Comuns

### Over-engineering
Construir mais do que o necessário para validação.

### Vanity Metrics
Focar em métricas que não indicam sucesso real.

### Ignorar Feedback
Não incorporar aprendizados dos usuários.

### Perfeccionismo
Esperar muito tempo para lançar.

## Próximos Passos

### Após Validação
1. **Scale**: Escalar o produto validado
2. **Optimize**: Otimizar performance e UX
3. **Expand**: Adicionar novas features
4. **Monetize**: Implementar modelo de receita

### Pivoting
Quando mudar direção baseado nos aprendizados:
- **Customer Segment Pivot**: Mudar público-alvo
- **Problem Pivot**: Mudar problema a resolver
- **Solution Pivot**: Mudar solução
- **Business Model Pivot**: Mudar modelo de negócio
"""
    
    # Salvar documentos
    documents = {
        "desenvolvimento_apps.md": app_dev_content,
        "desenvolvimento_saas.md": saas_content,
        "mvp_guia_completo.md": mvp_content
    }
    
    for filename, content in documents.items():
        file_path = test_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"📄 Documentos de teste criados em: {test_dir}")
    return test_dir

def test_chromadb_system():
    """Testa sistema com ChromaDB"""
    print("\n🧪 Testando Sistema RAG com ChromaDB...")
    
    try:
        # Criar sistema
        rag = create_chromadb_rag_system(
            data_dir="test_rag_chromadb",
            embedding_model=EmbeddingModel.MINILM  # Modelo menor para teste
        )
        
        print("✅ Sistema ChromaDB criado com sucesso")
        
        # Status do sistema
        status = rag.get_system_status()
        print(f"📊 Status: {status}")
        
        # Criar documentos de teste
        test_dir = create_test_documents()
        
        # Adicionar documentos
        for doc_file in test_dir.glob("*.md"):
            success = rag.add_document(doc_file)
            if success:
                print(f"✅ Documento adicionado: {doc_file.name}")
            else:
                print(f"❌ Falha ao adicionar: {doc_file.name}")
        
        # Testar buscas
        test_queries = [
            "Como desenvolver aplicações React Native?",
            "Qual a diferença entre SaaS e aplicações tradicionais?",
            "Como validar um MVP?",
            "Quais são as melhores práticas de segurança para apps móveis?",
            "Como implementar multi-tenancy em SaaS?"
        ]
        
        print("\n🔍 Testando buscas:")
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            results = rag.search(query, top_k=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result['source']}] Score: {result['similarity_score']:.3f}")
                    print(f"     {result['text'][:100]}...")
            else:
                print("  ❌ Nenhum resultado encontrado")
        
        # Testar contexto
        print("\n📋 Testando geração de contexto:")
        context = rag.get_context_for_query("Como desenvolver um MVP para SaaS?")
        print(f"Contexto gerado ({len(context)} caracteres):")
        print(context[:500] + "..." if len(context) > 500 else context)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste ChromaDB: {e}")
        return False

def test_simple_system():
    """Testa sistema simples sem dependências avançadas"""
    print("\n🧪 Testando Sistema RAG Simples...")
    
    try:
        # Configuração mínima
        config = RAGConfig(
            data_dir="test_rag_simple",
            vector_db_type=VectorDBType.CHROMADB,
            embedding_model=EmbeddingModel.MINILM,
            chunk_size=500,
            chunk_overlap=50
        )
        
        rag = ModernRAGSystem(config)
        print("✅ Sistema simples criado")
        
        # Status
        status = rag.get_system_status()
        print(f"📊 Status: {status['system_version']} - {status['documents_count']} docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste simples: {e}")
        return False

def run_comprehensive_test():
    """Executa teste abrangente do sistema"""
    print("🚀 Iniciando Teste Abrangente do Sistema RAG Moderno")
    print("=" * 60)
    
    # Testar dependências
    deps = test_system_dependencies()
    
    # Determinar quais testes executar
    tests_to_run = []
    
    if deps["ChromaDB"] and deps["SentenceTransformers"]:
        tests_to_run.append(("ChromaDB", test_chromadb_system))
    
    if deps["NumPy"] and deps["Requests"]:
        tests_to_run.append(("Simples", test_simple_system))
    
    if not tests_to_run:
        print("\n❌ Nenhum teste pode ser executado - dependências insuficientes")
        print("\n📦 Para instalar dependências:")
        print("pip install -r requirements_rag_modern.txt")
        return False
    
    # Executar testes
    results = {}
    for test_name, test_func in tests_to_run:
        print(f"\n{'='*20} TESTE {test_name.upper()} {'='*20}")
        results[test_name] = test_func()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\n🎯 Resultado Geral: {'✅ SUCESSO' if overall_success else '❌ FALHA'}")
    
    if overall_success:
        print("\n🎉 Sistema RAG Moderno está funcionando corretamente!")
        print("\n📚 Próximos passos:")
        print("  1. Adicione seus próprios documentos")
        print("  2. Configure APIs de LLM (OpenRouter, OpenAI, etc.)")
        print("  3. Integre com sua aplicação")
        print("  4. Configure monitoramento e logs")
    else:
        print("\n🔧 Algumas funcionalidades precisam de ajustes")
        print("\n💡 Sugestões:")
        print("  1. Verifique instalação das dependências")
        print("  2. Configure variáveis de ambiente")
        print("  3. Verifique conectividade de rede")
    
    return overall_success

if __name__ == "__main__":
    run_comprehensive_test()