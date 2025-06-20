# 🤖🎤 Widgets de Controle - Seletor de Agente e Controle de Áudio

## 📋 Resumo da Implementação

Foram implementados dois widgets de controle no canto direito da aplicação principal, proporcionando acesso rápido à seleção de agentes de IA e controle de áudio/comando de voz.

## 🎨 Interface Visual

### Barra de Controle
- **Localização**: Topo da aplicação, canto direito
- **Altura**: 50px fixos
- **Estilo**: Tema escuro integrado com bordas elegantes
- **Componentes**: Título da aplicação + Widgets de controle

### Widgets Implementados

#### 1. 🤖 Widget Seletor de Agente
- **Ícone**: Robô sorrindo (favicon personalizado)
- **Função**: Seleção de agentes OpenRouter/OpenAI
- **Tooltip**: "Clique para selecionar agente de IA"

#### 2. 🎤 Widget Controle de Áudio  
- **Ícone**: Microfone (ativo/mutado)
- **Função**: Configuração de áudio e comando de voz
- **Estados**: Ativo (verde) / Desabilitado (vermelho)

## 🚀 Funcionalidades

### Seletor de Agente OpenRouter

#### Dialog de Seleção
- **Filtros Disponíveis**:
  - ✅ Apenas modelos gratuitos
  - 🏢 Filtro por provedor (OpenAI, Anthropic, Google, Meta, Mistral AI)
  
- **Informações dos Agentes**:
  - Nome e provedor
  - Descrição detalhada
  - Preço por token (ou "GRATUITO")
  - Tamanho do contexto
  - Badge especial para modelos gratuitos

- **Agentes Pré-configurados**:
  - GPT-4 Turbo (OpenAI)
  - GPT-3.5 Turbo (OpenAI)
  - Claude 3 Sonnet (Anthropic)
  - Gemini Pro (Google) - GRATUITO
  - Llama 3 70B (Meta) - GRATUITO
  - Mixtral 8x7B (Mistral AI) - GRATUITO

#### Sistema de Cache
- Salva último agente selecionado em `config/last_agent.json`
- Carregamento automático ao iniciar aplicação
- Timestamp da seleção para auditoria

### Controle de Áudio

#### Dialog de Configuração
- **Status das Dependências**:
  - PyAudio (captura/reprodução)
  - pyttsx3 (síntese de fala)
  - SpeechRecognition (reconhecimento de voz)

- **Configurações de Entrada**:
  - ✅ Habilitar comando de voz
  - 🎤 Seleção de dispositivo de entrada
  - 🔊 Ativação por palavra-chave

- **Configurações de Saída**:
  - 🔊 Habilitar sons do sistema
  - 📻 Seleção de dispositivo de saída
  - 🎚️ Controle de volume (0-100%)

#### Funcionalidades de Teste
- **🎤 Testar Microfone**: Reconhecimento de fala em português
- **🔊 Testar Alto-falante**: Síntese de voz em português
- **📦 Instalar Dependências**: Link para instalação automática

#### Sistema de Configuração
- Salva configurações em `config/audio_settings.json`
- Carregamento automático das preferências
- Integração com reconhecimento de voz em tempo real

## 🔧 Arquivos Criados

### Geradores de Favicons
```
robot_favicon_advanced.py
├── create_smiling_robot_favicon() - Robô sorrindo 32x32
├── create_microphone_favicon() - Microfone ativo
└── create_microphone_muted_favicon() - Microfone mutado
```

### Widgets de Interface
```
agent_selector_widget.py
├── AgentSelectorDialog - Dialog completo de seleção
├── AgentSelectorWidget - Widget compacto para barra
└── Sistema de cache e filtros

audio_control_widget.py  
├── AudioControlDialog - Dialog de configuração completa
├── AudioControlWidget - Widget compacto para barra
└── Sistema de testes e configuração
```

### Dependências e Instalação
```
requirements_audio.txt - Lista de dependências de áudio
install_audio_deps.py - Script de instalação automática
```

### Ícones Gerados
```
static/icons/
├── robot_smiling.png/ico - Robô sorrindo
├── microphone_active.png/ico - Microfone ativo
└── microphone_muted.png/ico - Microfone mutado
```

## 🔗 Integração com Sistema Principal

### Sinais PyQt5
- `agent_changed` - Emitido quando agente é selecionado
- `audio_settings_changed` - Emitido quando áudio é configurado
- `voice_command_received` - Emitido quando comando de voz é reconhecido

### Métodos de Callback
```python
def on_agent_selected(self, agent_data):
    """Manipula seleção de novo agente"""
    
def on_audio_settings_changed(self, settings):
    """Manipula mudança nas configurações de áudio"""
    
def on_voice_command_received(self, command):
    """Manipula comando de voz recebido"""
```

### Integração com Chat
- Comando de voz automaticamente inserido no campo de mensagem
- Processamento automático após reconhecimento
- Histórico de comandos de voz no chat

## 📦 Instalação das Dependências

### Automática
```bash
python install_audio_deps.py
```

### Manual
```bash
pip install -r requirements_audio.txt
```

### Dependências Específicas
```bash
pip install pyaudio pyttsx3 SpeechRecognition
```

## 🎯 Como Usar

### 1. Seleção de Agente
1. Clique no ícone do robô sorrindo 🤖
2. Escolha filtros desejados (gratuito, provedor)
3. Clique em um agente da lista
4. Clique em "✅ Selecionar Agente"
5. Agente será salvo e carregado automaticamente

### 2. Configuração de Áudio
1. Clique no ícone do microfone 🎤
2. Instale dependências se necessário
3. Configure dispositivos de entrada/saída
4. Teste microfone e alto-falante
5. Habilite comando de voz
6. Salve configurações

### 3. Comando de Voz
1. Configure áudio conforme item 2
2. Habilite "comando de voz" 
3. Fale próximo ao microfone
4. Comando será automaticamente processado
5. Resposta aparecerá no chat

## 🔍 Status e Feedback

### Barra de Status
- Mostra agente selecionado atual
- Indica status do microfone (ativo/desabilitado)
- Exibe comandos de voz recebidos
- Reporta erros de configuração

### Indicadores Visuais
- **🤖 Verde**: Agente selecionado e ativo
- **🎤 Verde**: Microfone ativo e funcionando
- **🔇 Vermelho**: Microfone desabilitado
- **⚠️ Amarelo**: Dependências não instaladas

## 🚨 Solução de Problemas

### Agente não Carrega
- Verificar chave da API OpenRouter/OpenAI
- Confirmar conectividade com internet
- Checar logs na barra de status

### Microfone não Funciona
- Executar `python install_audio_deps.py`
- Verificar permissões do microfone no Windows
- Testar dispositivo em outras aplicações
- Checar configurações de privacidade

### Comando de Voz não Reconhece
- Falar claramente próximo ao microfone
- Verificar idioma (configurado para português)
- Testar conectividade (usa Google Speech API)
- Ajustar sensibilidade do microfone

## 📈 Próximas Melhorias

### Planejadas
- [ ] Suporte a Whisper offline
- [ ] Ativação por palavra-chave personalizada
- [ ] Múltiplos idiomas de reconhecimento
- [ ] Configuração de hotkeys
- [ ] Integração com TTS personalizado
- [ ] Histórico de comandos de voz
- [ ] Estatísticas de uso dos agentes

### Sugestões de Uso
- Configurar agente gratuito para testes
- Usar comando de voz para consultas rápidas
- Testar diferentes dispositivos de áudio
- Personalizar volume conforme ambiente
- Salvar configurações para diferentes cenários

---

**Status**: ✅ **IMPLEMENTADO E FUNCIONAL**  
**Versão**: 1.0.0  
**Data**: 20/06/2025  
**Commit**: `5cd00b6` - 🤖🎤 Implementar Widgets de Controle 