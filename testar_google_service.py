#!/usr/bin/env python3
"""
Script para testar Google Service Account isoladamente
"""

from google_service_account import GoogleServiceAccount

def main():
    print("\n🔍 Testando Google Service Account...")
    print("=" * 50)
    
    # Criar instância do Service Account
    google_service = GoogleServiceAccount()
    
    # Testar conexão
    success, message = google_service.test_connection()
    print(f"\n📝 Resultado do teste: {message}")
    
    if success:
        print("\n✅ Conexão bem sucedida!")
        
        # Testar serviço do Drive
        drive_service = google_service.get_drive_service()
        if drive_service:
            print("✅ Serviço Google Drive criado com sucesso")
            
            # Listar alguns arquivos como teste
            print("\n📁 Listando alguns arquivos do Drive:")
            results = drive_service.files().list(pageSize=5).execute()
            items = results.get('files', [])
            
            if not items:
                print("Nenhum arquivo encontrado.")
            else:
                for item in items:
                    print(f"- {item['name']} ({item['id']})")
    else:
        print("\n❌ Falha na conexão")
        print(f"Erro: {message}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 