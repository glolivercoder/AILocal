#!/usr/bin/env python3
"""
Script para ajustar pastas do Google Drive
"""

from google_service_account import GoogleServiceAccount

def main():
    print("\n🔧 Ajustando pastas do Google Drive...")
    print("=" * 50)
    
    # Email do usuário
    user_email = "glolivercoder@gmail.com"
    
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
            
            # Listar pastas compartilhadas
            print("\n📁 Listando pastas compartilhadas:")
            results = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.folder'",
                pageSize=10
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                print("Nenhuma pasta encontrada.")
            else:
                for item in items:
                    print(f"\nProcessando pasta: {item['name']} ({item['id']})")
                    
                    # Tentar mover para raiz
                    success, message = google_service.move_to_root(item['id'])
                    print(f"Mover para raiz: {message}")
                    
                    # Compartilhar com usuário como editor
                    success, message = google_service.share_with_user(item['id'], user_email)
                    print(f"Compartilhar pasta: {message}")
    else:
        print("\n❌ Falha na conexão")
        print(f"Erro: {message}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 