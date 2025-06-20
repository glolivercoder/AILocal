#!/usr/bin/env python3
"""
Gerador de Favicons Avançados - Robô Sorrindo e Microfone
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_smiling_robot_favicon(size=32):
    """Cria favicon de robô sorrindo"""
    # Criar imagem com fundo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cores
    robot_color = (100, 149, 237)  # Azul robô
    eye_color = (0, 255, 127)      # Verde neon
    smile_color = (255, 255, 0)    # Amarelo
    outline_color = (255, 255, 255) # Branco
    
    # Cabeça do robô (retângulo arredondado)
    head_margin = 2
    head_rect = [head_margin, head_margin, size-head_margin, size-head_margin-4]
    draw.rounded_rectangle(head_rect, radius=4, fill=robot_color, outline=outline_color, width=1)
    
    # Olhos (círculos verdes brilhantes)
    eye_size = size // 8
    left_eye = [size//4 - eye_size//2, size//3 - eye_size//2, size//4 + eye_size//2, size//3 + eye_size//2]
    right_eye = [3*size//4 - eye_size//2, size//3 - eye_size//2, 3*size//4 + eye_size//2, size//3 + eye_size//2]
    
    draw.ellipse(left_eye, fill=eye_color, outline=outline_color, width=1)
    draw.ellipse(right_eye, fill=eye_color, outline=outline_color, width=1)
    
    # Sorriso (arco)
    smile_rect = [size//4, size//2, 3*size//4, 3*size//4]
    draw.arc(smile_rect, start=0, end=180, fill=smile_color, width=2)
    
    # Antenas (pequenas linhas no topo)
    antenna_y = head_margin
    draw.line([size//3, antenna_y, size//3, antenna_y-3], fill=outline_color, width=1)
    draw.line([2*size//3, antenna_y, 2*size//3, antenna_y-3], fill=outline_color, width=1)
    
    # Pontos nas antenas
    draw.ellipse([size//3-1, antenna_y-4, size//3+1, antenna_y-2], fill=eye_color)
    draw.ellipse([2*size//3-1, antenna_y-4, 2*size//3+1, antenna_y-2], fill=eye_color)
    
    return img

def create_microphone_favicon(size=32):
    """Cria favicon de microfone"""
    # Criar imagem com fundo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cores
    mic_color = (220, 20, 60)      # Vermelho
    stand_color = (105, 105, 105)  # Cinza
    outline_color = (255, 255, 255) # Branco
    
    # Corpo do microfone (cápsula)
    mic_width = size // 3
    mic_height = size // 2
    mic_x = size // 2 - mic_width // 2
    mic_y = size // 6
    
    mic_rect = [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height]
    draw.rounded_rectangle(mic_rect, radius=mic_width//2, fill=mic_color, outline=outline_color, width=1)
    
    # Suporte do microfone
    stand_x = size // 2
    stand_y = mic_y + mic_height
    stand_bottom = size - 4
    
    # Haste vertical
    draw.line([stand_x, stand_y, stand_x, stand_bottom-4], fill=stand_color, width=2)
    
    # Base do suporte
    base_width = size // 2
    base_rect = [stand_x - base_width//2, stand_bottom-4, stand_x + base_width//2, stand_bottom]
    draw.rectangle(base_rect, fill=stand_color, outline=outline_color, width=1)
    
    # Detalhes do microfone (linhas horizontais)
    for i in range(3):
        line_y = mic_y + mic_height//4 + i * mic_height//6
        draw.line([mic_x + 2, line_y, mic_x + mic_width - 2, line_y], fill=outline_color, width=1)
    
    return img

def create_microphone_muted_favicon(size=32):
    """Cria favicon de microfone mutado"""
    img = create_microphone_favicon(size)
    draw = ImageDraw.Draw(img)
    
    # Adicionar X vermelho para indicar mudo
    x_color = (255, 0, 0)
    margin = 2
    
    # Linha diagonal 1
    draw.line([margin, margin, size-margin, size-margin], fill=x_color, width=3)
    # Linha diagonal 2  
    draw.line([margin, size-margin, size-margin, margin], fill=x_color, width=3)
    
    return img

def save_favicons():
    """Salva todos os favicons"""
    # Criar diretório se não existir
    os.makedirs('static/icons', exist_ok=True)
    
    # Favicon robô sorrindo
    robot_img = create_smiling_robot_favicon(32)
    robot_img.save('static/icons/robot_smiling.png')
    robot_img.save('static/icons/robot_smiling.ico')
    
    # Favicon microfone ativo
    mic_img = create_microphone_favicon(32)
    mic_img.save('static/icons/microphone_active.png')
    mic_img.save('static/icons/microphone_active.ico')
    
    # Favicon microfone mutado
    mic_muted_img = create_microphone_muted_favicon(32)
    mic_muted_img.save('static/icons/microphone_muted.png')
    mic_muted_img.save('static/icons/microphone_muted.ico')
    
    print("✅ Favicons criados com sucesso:")
    print("   - static/icons/robot_smiling.png/ico")
    print("   - static/icons/microphone_active.png/ico") 
    print("   - static/icons/microphone_muted.png/ico")

if __name__ == "__main__":
    save_favicons() 