import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

def main():
    print("Criando janela...")
    root = tk.Tk()
    root.title("Teste Tkinter")
    root.geometry("400x300")
    
    print("Criando widgets...")
    frame = ttk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    label = ttk.Label(frame, text="Teste do Tkinter")
    label.pack()
    
    button = ttk.Button(frame, text="Clique Aqui", command=lambda: print("Botão clicado!"))
    button.pack()
    
    print("Iniciando loop principal...")
    root.mainloop()
    print("Aplicação encerrada.")

if __name__ == "__main__":
    print("Python version:", sys.version)
    print("Tkinter version:", tk.TkVersion)
    main() 