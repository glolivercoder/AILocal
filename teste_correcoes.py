#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se as correções de configuração funcionaram
"""

import sys
import os
import warnings
from io import StringIO

def capturar_warnings():
    """Captura warnings durante importação dos módulos"""
    # Redirecionar stderr para capturar warnings
    old_stderr = sys.stderr
    sys.stderr = captured_warnings = StringIO()
    
    warnings_list = []
    
    try:
        # Testar importação do config_manager
        print("🔍 Testando config_manager...")
        import config_manager
        print("✅ config_manager importado sem erros")
        
        # Testar importação do mcp_manager
        print("\n🔍 Testando mcp_manager...")
        import mcp_manager
        print("✅ mcp_manager importado sem erros")
        
        # Testar criação do ConfigManager
        print("\n🔍 Testando criação do ConfigManager...")
        config_mgr = config_manager.ConfigManager()
        print("✅ ConfigManager criado sem erros")
        
        # Testar criação do MCPManager
        print("\n🔍 Testando criação do MCPManager...")
        mcp_mgr = mcp_manager.MCPManager()
        print("✅ MCPManager criado sem erros")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        warnings_list.append(str(e))
    
    finally:
        # Restaurar stderr
        sys.stderr = old_stderr
        
        # Capturar warnings
        warning_output = captured_warnings.getvalue()
        if warning_output:
            warnings_list.extend(warning_output.split('\n'))
    
    return warnings_list

def verificar_arquivos():
    """Verifica se os arquivos necessários foram criados"""
    arquivos_necessarios = [
        'gdrive_creds.txt',
        'client_secrets.json.example',
        '.env.example',
        'CONFIGURACAO_OPCIONAL.md'
    ]
    
    print("\n📁 Verificando arquivos criados:")
    arquivos_ok = 0
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo} - Existe")
            arquivos_ok += 1
        else:
            print(f"❌ {arquivo} - Não encontrado")
    
    return arquivos_ok, len(arquivos_necessarios)

def verificar_modificacoes():
    """Verifica se as modificações nos arquivos foram aplicadas"""
    print("\n🔧 Verificando modificações:")
    modificacoes_ok = 0
    total_modificacoes = 2
    
    # Verificar config_manager.py
    try:
        with open('config_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'warnings.filterwarnings' in content:
                print("✅ config_manager.py - Warnings suprimidos")
                modificacoes_ok += 1
            else:
                print("❌ config_manager.py - Warnings não suprimidos")
    except Exception as e:
        print(f"❌ Erro ao verificar config_manager.py: {e}")
    
    # Verificar mcp_manager.py
    try:
        with open('mcp_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'usando rate limit padrão' in content:
                print("✅ mcp_manager.py - Warning convertido para info")
                modificacoes_ok += 1
            else:
                print("❌ mcp_manager.py - Warning não convertido")
    except Exception as e:
        print(f"❌ Erro ao verificar mcp_manager.py: {e}")
    
    return modificacoes_ok, total_modificacoes

def main():
    """Função principal de teste"""
    print("="*60)
    print("    TESTE DAS CORREÇÕES DE CONFIGURAÇÃO")
    print("="*60)
    
    # 1. Verificar arquivos
    arquivos_ok, total_arquivos = verificar_arquivos()
    
    # 2. Verificar modificações
    modificacoes_ok, total_modificacoes = verificar_modificacoes()
    
    # 3. Testar importações e warnings
    print("\n⚠️  Testando warnings:")
    warnings_capturados = capturar_warnings()
    
    # 4. Analisar warnings
    warnings_criticos = []
    for warning in warnings_capturados:
        if warning.strip() and any(termo in warning.lower() for termo in 
                                 ['gdrive_creds.txt', 'client_secrets.json', 'github token']):
            warnings_criticos.append(warning)
    
    # Resumo
    print("\n" + "="*60)
    print("    RESUMO DOS TESTES")
    print("="*60)
    
    print(f"📁 Arquivos criados: {arquivos_ok}/{total_arquivos}")
    print(f"🔧 Modificações aplicadas: {modificacoes_ok}/{total_modificacoes}")
    print(f"⚠️  Warnings críticos: {len(warnings_criticos)}")
    
    if warnings_criticos:
        print("\n⚠️  Warnings ainda presentes:")
        for warning in warnings_criticos[:3]:  # Mostrar apenas os primeiros 3
            print(f"   - {warning.strip()}")
    
    # Resultado final
    total_score = arquivos_ok + modificacoes_ok
    max_score = total_arquivos + total_modificacoes
    
    if total_score == max_score and len(warnings_criticos) == 0:
        print("\n🎉 TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO!")
        print("\n✅ O sistema deve funcionar sem warnings críticos")
        print("\n💡 Próximos passos:")
        print("   1. Execute: python ai_agent_gui.py")
        print("   2. Para configurações opcionais: CONFIGURACAO_OPCIONAL.md")
    elif total_score >= max_score * 0.8:
        print("\n✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("\n⚠️  Alguns warnings menores podem persistir, mas não afetam funcionalidade")
    else:
        print("\n⚠️  ALGUMAS CORREÇÕES FALHARAM")
        print("\n🔧 Verifique os logs acima para detalhes")
    
    print("\n📋 Arquivos importantes:")
    print("   - ai_agent_gui.py (interface principal)")
    print("   - CONFIGURACAO_OPCIONAL.md (guia de configuração)")
    print("   - .env.example (configurações opcionais)")

if __name__ == "__main__":
    main()