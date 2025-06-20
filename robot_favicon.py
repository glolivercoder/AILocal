#!/usr/bin/env python3
"""
Gerador de Favicon de Robô
Cria um ícone simples de robô para a aplicação
"""

from PIL import Image, ImageDraw
import os

def create_robot_favicon():
    """Cria um favicon de robô 32x32"""
    # Criar imagem 32x32
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cabeça do robô (retângulo cinza)
    head_rect = [6, 8, 26, 24]
    draw.rectangle(head_rect, fill=(100, 100, 100, 255), outline=(60, 60, 60, 255), width=1)
    
    # Olhos (círculos azuis)
    eye1 = [10, 12, 14, 16]
    eye2 = [18, 12, 22, 16]
    draw.ellipse(eye1, fill=(0, 150, 255, 255))
    draw.ellipse(eye2, fill=(0, 150, 255, 255))
    
    # Boca (linha)
    draw.line([(12, 19), (20, 19)], fill=(60, 60, 60, 255), width=2)
    
    # Antenas
    draw.line([(12, 8), (12, 4)], fill=(60, 60, 60, 255), width=2)
    draw.line([(20, 8), (20, 4)], fill=(60, 60, 60, 255), width=2)
    
    # Pontos nas antenas
    draw.ellipse([11, 3, 13, 5], fill=(255, 100, 100, 255))
    draw.ellipse([19, 3, 21, 5], fill=(255, 100, 100, 255))
    
    return img

def save_favicon():
    """Salva o favicon em diferentes formatos"""
    robot_img = create_robot_favicon()
    
    # Salvar como ICO
    robot_img.save('robot_favicon.ico', format='ICO', sizes=[(32, 32)])
    
    # Salvar como PNG
    robot_img.save('robot_favicon.png', format='PNG')
    
    print("✅ Favicon de robô criado:")
    print("   - robot_favicon.ico (32x32)")
    print("   - robot_favicon.png (32x32)")

if __name__ == "__main__":
    try:
        save_favicon()
    except ImportError:
        print("⚠️ PIL não disponível. Instale com: pip install Pillow")
    except Exception as e:
        print(f"❌ Erro ao criar favicon: {e}") 