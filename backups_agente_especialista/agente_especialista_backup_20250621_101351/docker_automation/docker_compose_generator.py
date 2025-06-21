#!/usr/bin/env python3
"""
Gerador de Docker Compose para AILocal
Inclui N8N, Supabase, Ollama e outros serviços
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

class DockerComposeGenerator:
    """Gerador de arquivos Docker Compose personalizados"""
    
    def __init__(self):
        self.services = {}
        self.volumes = {}
        self.networks = {}
        self.environment_vars = {}
        
    def add_n8n_service(self, 
                       port: int = 5678,
                       webhook_url: str = "http://localhost:5678",
                       encryption_key: Optional[str] = None) -> Dict[str, Any]:
        """Adiciona serviço N8N"""
        
        if not encryption_key:
            import secrets
            encryption_key = secrets.token_urlsafe(32)
        
        n8n_service = {
            'image': 'n8nio/n8n:latest',
            'container_name': 'ailocal_n8n',
            'restart': 'unless-stopped',
            'ports': [f'{port}:5678'],
            'environment': {
                'N8N_BASIC_AUTH_ACTIVE': 'true',
                'N8N_BASIC_AUTH_USER': 'admin',
                'N8N_BASIC_AUTH_PASSWORD': 'admin123',
                'N8N_HOST': '0.0.0.0',
                'N8N_PORT': '5678',
                'N8N_PROTOCOL': 'http',
                'WEBHOOK_URL': webhook_url,
                'N8N_ENCRYPTION_KEY': encryption_key,
                'EXECUTIONS_DATA_PRUNE': 'true',
                'EXECUTIONS_DATA_MAX_AGE': '168',  # 7 dias
                'N8N_METRICS': 'true'
            },
            'volumes': [
                'ailocal_n8n_data:/home/node/.n8n',
                '/var/run/docker.sock:/var/run/docker.sock:ro'  # Para integração Docker
            ],
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db']
        }
        
        self.services['n8n'] = n8n_service
        self.volumes['ailocal_n8n_data'] = {}
        
        return n8n_service
    
    def add_supabase_stack(self, 
                          db_password: str = "postgres123",
                          jwt_secret: Optional[str] = None,
                          anon_key: Optional[str] = None,
                          service_role_key: Optional[str] = None) -> Dict[str, Any]:
        """Adiciona stack completo do Supabase"""
        
        if not jwt_secret:
            import secrets
            jwt_secret = secrets.token_urlsafe(32)
        
        if not anon_key:
            import secrets
            anon_key = secrets.token_urlsafe(32)
            
        if not service_role_key:
            import secrets
            service_role_key = secrets.token_urlsafe(32)
        
        # PostgreSQL Database
        postgres_service = {
            'image': 'supabase/postgres:15.1.0.147',
            'container_name': 'ailocal_supabase_db',
            'restart': 'unless-stopped',
            'ports': ['5432:5432'],
            'environment': {
                'POSTGRES_PASSWORD': db_password,
                'POSTGRES_DB': 'postgres',
                'POSTGRES_USER': 'postgres',
                'POSTGRES_HOST': 'localhost'
            },
            'volumes': [
                'ailocal_supabase_db:/var/lib/postgresql/data',
                './supabase/init.sql:/docker-entrypoint-initdb.d/init.sql:ro'
            ],
            'networks': ['ailocal_network'],
            'command': [
                'postgres',
                '-c', 'config_file=/etc/postgresql/postgresql.conf',
                '-c', 'log_statement=all'
            ]
        }
        
        # Supabase API Gateway
        kong_service = {
            'image': 'kong:2.8.1',
            'container_name': 'ailocal_supabase_kong',
            'restart': 'unless-stopped',
            'ports': ['8000:8000', '8443:8443'],
            'environment': {
                'KONG_DATABASE': 'off',
                'KONG_DECLARATIVE_CONFIG': '/var/lib/kong/kong.yml',
                'KONG_DNS_ORDER': 'LAST,A,CNAME',
                'KONG_PLUGINS': 'request-size-limiting,response-size-limiting,cors,key-auth,acl',
                'KONG_NGINX_PROXY_PROXY_BUFFER_SIZE': '160k',
                'KONG_NGINX_PROXY_PROXY_BUFFERS': '64 160k'
            },
            'volumes': ['./supabase/kong.yml:/var/lib/kong/kong.yml:ro'],
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db']
        }
        
        # Supabase Auth
        auth_service = {
            'image': 'supabase/gotrue:v2.99.0',
            'container_name': 'ailocal_supabase_auth',
            'restart': 'unless-stopped',
            'environment': {
                'GOTRUE_API_HOST': '0.0.0.0',
                'GOTRUE_API_PORT': '9999',
                'API_EXTERNAL_URL': 'http://localhost:8000',
                'GOTRUE_DB_DRIVER': 'postgres',
                'GOTRUE_DB_DATABASE_URL': f'postgresql://supabase_auth_admin:{db_password}@supabase_db:5432/postgres',
                'GOTRUE_SITE_URL': 'http://localhost:3000',
                'GOTRUE_URI_ALLOW_LIST': '*',
                'GOTRUE_DISABLE_SIGNUP': 'false',
                'GOTRUE_JWT_ADMIN_ROLES': 'service_role',
                'GOTRUE_JWT_AUD': 'authenticated',
                'GOTRUE_JWT_DEFAULT_GROUP_NAME': 'authenticated',
                'GOTRUE_JWT_EXP': '3600',
                'GOTRUE_JWT_SECRET': jwt_secret,
                'GOTRUE_EXTERNAL_EMAIL_ENABLED': 'true',
                'GOTRUE_MAILER_AUTOCONFIRM': 'false',
                'GOTRUE_SMTP_ADMIN_EMAIL': 'admin@example.com',
                'GOTRUE_SMTP_HOST': 'supabase_inbucket',
                'GOTRUE_SMTP_PORT': '2500',
                'GOTRUE_SMTP_USER': 'fake_mail_user',
                'GOTRUE_SMTP_PASS': 'fake_mail_password',
                'GOTRUE_SMTP_SENDER_NAME': 'fake_sender',
                'GOTRUE_MAILER_URLPATHS_INVITE': '/auth/v1/verify',
                'GOTRUE_MAILER_URLPATHS_CONFIRMATION': '/auth/v1/verify',
                'GOTRUE_MAILER_URLPATHS_RECOVERY': '/auth/v1/verify',
                'GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE': '/auth/v1/verify'
            },
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db']
        }
        
        # Supabase REST API
        rest_service = {
            'image': 'postgrest/postgrest:v11.2.0',
            'container_name': 'ailocal_supabase_rest',
            'restart': 'unless-stopped',
            'environment': {
                'PGRST_DB_URI': f'postgresql://authenticator:{db_password}@supabase_db:5432/postgres',
                'PGRST_DB_SCHEMAS': 'public,storage,graphql_public',
                'PGRST_DB_ANON_ROLE': 'anon',
                'PGRST_JWT_SECRET': jwt_secret,
                'PGRST_DB_USE_LEGACY_GUCS': 'false',
                'PGRST_APP_SETTINGS_JWT_SECRET': jwt_secret,
                'PGRST_APP_SETTINGS_JWT_EXP': '3600'
            },
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db']
        }
        
        # Supabase Realtime
        realtime_service = {
            'image': 'supabase/realtime:v2.25.50',
            'container_name': 'ailocal_supabase_realtime',
            'restart': 'unless-stopped',
            'environment': {
                'PORT': '4000',
                'DB_HOST': 'supabase_db',
                'DB_PORT': '5432',
                'DB_USER': 'supabase_admin',
                'DB_PASSWORD': db_password,
                'DB_NAME': 'postgres',
                'DB_AFTER_CONNECT_QUERY': 'SET search_path TO _realtime',
                'DB_ENC_KEY': 'supabaserealtime',
                'API_JWT_SECRET': jwt_secret,
                'FLY_ALLOC_ID': 'fly123',
                'FLY_APP_NAME': 'realtime',
                'SECRET_KEY_BASE': jwt_secret,
                'ERL_AFLAGS': '-proto_dist inet_tcp',
                'ENABLE_TAILSCALE': 'false',
                'DNS_NODES': "''"
            },
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db']
        }
        
        # Supabase Storage
        storage_service = {
            'image': 'supabase/storage-api:v0.40.4',
            'container_name': 'ailocal_supabase_storage',
            'restart': 'unless-stopped',
            'environment': {
                'ANON_KEY': anon_key,
                'SERVICE_KEY': service_role_key,
                'POSTGREST_URL': 'http://supabase_rest:3000',
                'PGRST_JWT_SECRET': jwt_secret,
                'DATABASE_URL': f'postgresql://supabase_storage_admin:{db_password}@supabase_db:5432/postgres',
                'FILE_SIZE_LIMIT': '52428800',
                'STORAGE_BACKEND': 'file',
                'FILE_STORAGE_BACKEND_PATH': '/var/lib/storage',
                'TENANT_ID': 'stub',
                'REGION': 'stub',
                'GLOBAL_S3_BUCKET': 'stub',
                'ENABLE_IMAGE_TRANSFORMATION': 'true',
                'IMGPROXY_URL': 'http://supabase_imgproxy:5001'
            },
            'volumes': ['ailocal_supabase_storage:/var/lib/storage'],
            'networks': ['ailocal_network'],
            'depends_on': ['supabase_db', 'supabase_rest']
        }
        
        # Adicionar serviços
        self.services.update({
            'supabase_db': postgres_service,
            'supabase_kong': kong_service,
            'supabase_auth': auth_service,
            'supabase_rest': rest_service,
            'supabase_realtime': realtime_service,
            'supabase_storage': storage_service
        })
        
        # Adicionar volumes
        self.volumes.update({
            'ailocal_supabase_db': {},
            'ailocal_supabase_storage': {}
        })
        
        return {
            'db_password': db_password,
            'jwt_secret': jwt_secret,
            'anon_key': anon_key,
            'service_role_key': service_role_key
        }
    
    def add_ollama_service(self, 
                          port: int = 11434,
                          models: List[str] = None) -> Dict[str, Any]:
        """Adiciona serviço Ollama"""
        
        if models is None:
            models = ['llama2', 'codellama', 'mistral']
        
        ollama_service = {
            'image': 'ollama/ollama:latest',
            'container_name': 'ailocal_ollama',
            'restart': 'unless-stopped',
            'ports': [f'{port}:11434'],
            'volumes': [
                'ailocal_ollama_data:/root/.ollama'
            ],
            'networks': ['ailocal_network'],
            'environment': {
                'OLLAMA_HOST': '0.0.0.0',
                'OLLAMA_ORIGINS': '*'
            }
        }
        
        # Script de inicialização para baixar modelos
        init_script = f"""#!/bin/bash
echo "Iniciando Ollama..."
ollama serve &
sleep 10

echo "Baixando modelos..."
{chr(10).join([f'ollama pull {model}' for model in models])}

echo "Modelos instalados com sucesso!"
wait
"""
        
        self.services['ollama'] = ollama_service
        self.volumes['ailocal_ollama_data'] = {}
        
        return {
            'service': ollama_service,
            'init_script': init_script
        }
    
    def add_redis_service(self, port: int = 6379) -> Dict[str, Any]:
        """Adiciona serviço Redis para cache"""
        
        redis_service = {
            'image': 'redis:7-alpine',
            'container_name': 'ailocal_redis',
            'restart': 'unless-stopped',
            'ports': [f'{port}:6379'],
            'volumes': [
                'ailocal_redis_data:/data'
            ],
            'networks': ['ailocal_network'],
            'command': 'redis-server --appendonly yes --requirepass redis123'
        }
        
        self.services['redis'] = redis_service
        self.volumes['ailocal_redis_data'] = {}
        
        return redis_service
    
    def add_ailocal_app_service(self, 
                               port: int = 8080,
                               openrouter_key: Optional[str] = None) -> Dict[str, Any]:
        """Adiciona serviço principal do AILocal"""
        
        app_service = {
            'build': {
                'context': '.',
                'dockerfile': 'Dockerfile'
            },
            'container_name': 'ailocal_app',
            'restart': 'unless-stopped',
            'ports': [f'{port}:8080'],
            'environment': {
                'PYTHONPATH': '/app',
                'OLLAMA_URL': 'http://ollama:11434',
                'SUPABASE_URL': 'http://supabase_kong:8000',
                'SUPABASE_ANON_KEY': '${SUPABASE_ANON_KEY}',
                'SUPABASE_SERVICE_KEY': '${SUPABASE_SERVICE_KEY}',
                'N8N_URL': 'http://n8n:5678',
                'REDIS_URL': 'redis://redis123@redis:6379',
                'OPENROUTER_API_KEY': openrouter_key or '${OPENROUTER_API_KEY}'
            },
            'volumes': [
                './rag_data:/app/rag_data',
                './config:/app/config',
                './logs:/app/logs'
            ],
            'networks': ['ailocal_network'],
            'depends_on': [
                'supabase_db',
                'supabase_kong',
                'n8n',
                'ollama',
                'redis'
            ]
        }
        
        self.services['ailocal_app'] = app_service
        
        return app_service
    
    def create_network(self):
        """Cria rede personalizada"""
        self.networks['ailocal_network'] = {
            'driver': 'bridge',
            'ipam': {
                'config': [
                    {'subnet': '172.20.0.0/16'}
                ]
            }
        }
    
    def generate_compose_file(self, 
                            include_n8n: bool = True,
                            include_supabase: bool = True,
                            include_ollama: bool = True,
                            include_redis: bool = True,
                            include_app: bool = True) -> Dict[str, Any]:
        """Gera arquivo docker-compose.yml completo"""
        
        # Limpar serviços existentes
        self.services = {}
        self.volumes = {}
        self.networks = {}
        
        # Criar rede
        self.create_network()
        
        # Adicionar serviços conforme solicitado
        config = {}
        
        if include_supabase:
            config['supabase'] = self.add_supabase_stack()
            
        if include_n8n:
            config['n8n'] = self.add_n8n_service()
            
        if include_ollama:
            config['ollama'] = self.add_ollama_service()
            
        if include_redis:
            config['redis'] = self.add_redis_service()
            
        if include_app:
            config['app'] = self.add_ailocal_app_service()
        
        # Montar estrutura do docker-compose
        compose_structure = {
            'version': '3.8',
            'services': self.services,
            'volumes': self.volumes,
            'networks': self.networks
        }
        
        return {
            'compose': compose_structure,
            'config': config
        }
    
    def save_compose_file(self, 
                         output_path: str = "docker-compose.yml",
                         **kwargs) -> Dict[str, Any]:
        """Salva arquivo docker-compose.yml"""
        
        result = self.generate_compose_file(**kwargs)
        compose_data = result['compose']
        config = result['config']
        
        # Salvar docker-compose.yml
        with open(output_path, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        # Criar arquivo .env de exemplo
        env_content = self._generate_env_file(config)
        with open('.env.example', 'w') as f:
            f.write(env_content)
        
        # Criar arquivos de configuração necessários
        self._create_config_files(config)
        
        return {
            'compose_file': output_path,
            'config': config,
            'env_file': '.env.example'
        }
    
    def _generate_env_file(self, config: Dict[str, Any]) -> str:
        """Gera arquivo .env de exemplo"""
        env_lines = [
            "# Arquivo de configuração do AILocal",
            "# Copie para .env e configure as variáveis",
            "",
            "# OpenRouter API",
            "OPENROUTER_API_KEY=your_openrouter_key_here",
            "",
        ]
        
        if 'supabase' in config:
            supabase_config = config['supabase']
            env_lines.extend([
                "# Supabase Configuration",
                f"SUPABASE_DB_PASSWORD={supabase_config['db_password']}",
                f"SUPABASE_JWT_SECRET={supabase_config['jwt_secret']}",
                f"SUPABASE_ANON_KEY={supabase_config['anon_key']}",
                f"SUPABASE_SERVICE_KEY={supabase_config['service_role_key']}",
                ""
            ])
        
        if 'n8n' in config:
            env_lines.extend([
                "# N8N Configuration",
                "N8N_BASIC_AUTH_USER=admin",
                "N8N_BASIC_AUTH_PASSWORD=admin123",
                ""
            ])
        
        return "\n".join(env_lines)
    
    def _create_config_files(self, config: Dict[str, Any]):
        """Cria arquivos de configuração necessários"""
        
        # Criar diretório supabase se necessário
        if 'supabase' in config:
            supabase_dir = Path('supabase')
            supabase_dir.mkdir(exist_ok=True)
            
            # Arquivo de inicialização do banco
            init_sql = """
-- Configuração inicial do Supabase
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema para RAG
CREATE SCHEMA IF NOT EXISTS rag;

-- Tabela para documentos
CREATE TABLE IF NOT EXISTS rag.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca por similaridade
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON rag.documents USING ivfflat (embedding vector_cosine_ops);

-- Função para busca por similaridade
CREATE OR REPLACE FUNCTION rag.search_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    filename TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        documents.id,
        documents.filename,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM rag.documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;
"""
            
            with open(supabase_dir / 'init.sql', 'w') as f:
                f.write(init_sql)
            
            # Configuração do Kong
            kong_config = {
                '_format_version': '2.1',
                'services': [
                    {
                        'name': 'auth-v1-open',
                        'url': 'http://supabase_auth:9999/verify',
                        'plugins': [
                            {
                                'name': 'cors',
                                'config': {
                                    'origins': ['*'],
                                    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                                    'headers': ['Accept', 'Accept-Version', 'Content-Length', 'Content-MD5', 'Content-Type', 'Date', 'X-Api-Version', 'Authorization']
                                }
                            }
                        ]
                    },
                    {
                        'name': 'rest-v1',
                        'url': 'http://supabase_rest:3000/',
                        'plugins': [
                            {
                                'name': 'cors',
                                'config': {
                                    'origins': ['*'],
                                    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                                    'headers': ['Accept', 'Accept-Version', 'Content-Length', 'Content-MD5', 'Content-Type', 'Date', 'X-Api-Version', 'Authorization']
                                }
                            }
                        ]
                    }
                ],
                'routes': [
                    {
                        'service': 'auth-v1-open',
                        'name': 'auth-v1-open',
                        'strip_path': True,
                        'paths': ['/auth/v1/verify']
                    },
                    {
                        'service': 'rest-v1',
                        'name': 'rest-v1-all',
                        'strip_path': True,
                        'paths': ['/rest/v1/']
                    }
                ]
            }
            
            with open(supabase_dir / 'kong.yml', 'w') as f:
                yaml.dump(kong_config, f, default_flow_style=False)

def create_docker_compose(services: List[str] = None, 
                         output_path: str = "docker-compose.yml") -> Dict[str, Any]:
    """Função de conveniência para criar docker-compose"""
    
    if services is None:
        services = ['supabase', 'n8n', 'ollama', 'redis', 'app']
    
    generator = DockerComposeGenerator()
    
    return generator.save_compose_file(
        output_path=output_path,
        include_supabase='supabase' in services,
        include_n8n='n8n' in services,
        include_ollama='ollama' in services,
        include_redis='redis' in services,
        include_app='app' in services
    )

if __name__ == "__main__":
    # Exemplo de uso
    print("🐳 Gerando Docker Compose para AILocal...")
    
    result = create_docker_compose()
    
    print(f"✅ Arquivos criados:")
    print(f"   - {result['compose_file']}")
    print(f"   - {result['env_file']}")
    print(f"   - supabase/init.sql")
    print(f"   - supabase/kong.yml")
    print()
    print("📋 Para usar:")
    print("   1. cp .env.example .env")
    print("   2. Configure as variáveis no arquivo .env")
    print("   3. docker-compose up -d")
    print()
    print("🌐 Serviços disponíveis:")
    print("   - AILocal App: http://localhost:8080")
    print("   - N8N: http://localhost:5678")
    print("   - Supabase: http://localhost:8000")
    print("   - Ollama: http://localhost:11434") 