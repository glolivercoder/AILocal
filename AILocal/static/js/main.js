// Main JavaScript for AI Development Command Assistant

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const commandInput = document.getElementById('command-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const voiceIndicator = document.getElementById('voice-indicator');
    const terminalContent = document.getElementById('terminal-content');
    const historyContainer = document.getElementById('history-container');
    const modelSelector = document.getElementById('model-selector');
    const executeCommandsCheckbox = document.getElementById('execute-commands');
    const technologyBadges = document.querySelectorAll('.technology-badge');
    const selectedTechBadge = document.getElementById('selected-tech');
    const techNameSpan = document.getElementById('tech-name');
    
    // OpenRouter related elements
    const openrouterModelsContainer = document.getElementById('openrouter-models-container');
    const openrouterModelSelector = document.getElementById('openrouter-model-selector');
    const openrouterModelSearch = document.getElementById('openrouter-model-search');
    
    // Additional elements for web search and docs (may need to be added to HTML)
    const useWebCheckbox = document.getElementById('use-web') || { checked: false };
    const useDocsCheckbox = document.getElementById('use-docs') || { checked: true };
    
    // Application State
    let state = {
        selectedTechnology: null,
        isListening: false,
        recognition: null,
        commandHistory: [],
        lastCommand: null,
        docsStatus: {},
        apiStatus: {}
    };
    
    // Load settings from localStorage
    function loadSettings() {
        const savedModel = localStorage.getItem('selectedModel');
        if (savedModel && modelSelector.querySelector(`option[value="${savedModel}"]`)) {
            modelSelector.value = savedModel;
        }
        
        // Load OpenRouter model setting
        if (openrouterModelSelector) {
            const savedOpenRouterModel = localStorage.getItem('openrouterModel');
            if (savedOpenRouterModel && openrouterModelSelector.querySelector(`option[value="${savedOpenRouterModel}"]`)) {
                openrouterModelSelector.value = savedOpenRouterModel;
            }
        }
        
        // Show/hide OpenRouter models dropdown based on current model selection
        toggleOpenRouterModels();
        
        const executeCommands = localStorage.getItem('executeCommands');
        executeCommandsCheckbox.checked = executeCommands === 'true';
        
        const selectedTech = localStorage.getItem('selectedTechnology');
        if (selectedTech) {
            selectTechnology(selectedTech);
        }
        
        // Load additional settings
        if (useWebCheckbox && 'id' in useWebCheckbox) {
            useWebCheckbox.checked = localStorage.getItem('useWeb') === 'true';
        }
        
        if (useDocsCheckbox && 'id' in useDocsCheckbox) {
            useDocsCheckbox.checked = localStorage.getItem('useDocs') !== 'false'; // Default to true
        }
    }
    
    // Save settings to localStorage
    function saveSettings() {
        localStorage.setItem('selectedModel', modelSelector.value);
        localStorage.setItem('executeCommands', executeCommandsCheckbox.checked);
        if (state.selectedTechnology) {
            localStorage.setItem('selectedTechnology', state.selectedTechnology);
        }
        
        // Save OpenRouter model selection
        if (openrouterModelSelector) {
            localStorage.setItem('openrouterModel', openrouterModelSelector.value);
        }
        
        // Save additional settings
        if (useWebCheckbox && 'id' in useWebCheckbox) {
            localStorage.setItem('useWeb', useWebCheckbox.checked);
        }
        
        if (useDocsCheckbox && 'id' in useDocsCheckbox) {
            localStorage.setItem('useDocs', useDocsCheckbox.checked);
        }
    }
    
    // Initialize Speech Recognition
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            state.recognition = new webkitSpeechRecognition();
            state.recognition.continuous = false;
            state.recognition.interimResults = false;
            state.recognition.lang = 'en-US';
            
            state.recognition.onstart = function() {
                state.isListening = true;
                voiceIndicator.classList.remove('hidden');
                micButton.classList.add('text-red-500');
            };
            
            state.recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                commandInput.value = transcript;
                processCommand();
            };
            
            state.recognition.onend = function() {
                state.isListening = false;
                voiceIndicator.classList.add('hidden');
                micButton.classList.remove('text-red-500');
            };
            
            state.recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                addToTerminal(`Speech recognition error: ${event.error}`, 'error');
                state.isListening = false;
                voiceIndicator.classList.add('hidden');
                micButton.classList.remove('text-red-500');
            };
        } else {
            micButton.disabled = true;
            micButton.classList.add('opacity-50');
            console.error('Speech recognition not supported in this browser');
        }
    }
    
    // Toggle Speech Recognition
    function toggleSpeechRecognition() {
        if (!state.recognition) {
            initSpeechRecognition();
        }
        
        if (state.isListening) {
            state.recognition.stop();
        } else {
            state.recognition.start();
        }
    }
    
    // Add message to terminal
    function addToTerminal(message, type = 'info') {
        const element = document.createElement('div');
        
        if (type === 'command') {
            element.className = 'terminal-prompt mt-4 mb-2';
            element.textContent = message;
        } else if (type === 'output') {
            element.className = 'terminal-output mb-4';
            element.textContent = message;
        } else if (type === 'error') {
            element.className = 'terminal-output mb-4 text-red-400';
            element.textContent = message;
        } else if (type === 'success') {
            element.className = 'terminal-output mb-4 text-green-400';
            element.textContent = message;
        } else {
            element.className = 'terminal-info mb-2 text-blue-300';
            element.textContent = message;
        }
        
        terminalContent.appendChild(element);
        
        // Auto scroll to bottom
        const outputContainer = document.getElementById('output-container');
        outputContainer.scrollTop = outputContainer.scrollHeight;
    }
    
    // Process the command
    function processCommand() {
        const command = commandInput.value.trim();
        if (!command) return;
        
        // Add command to terminal
        addToTerminal(command, 'command');
        addToTerminal('Processing command...', 'info');
        
        // Clear input
        commandInput.value = '';
        
        // Prepare request data
        const requestData = {
            command: command,
            model: modelSelector.value,
            execute: executeCommandsCheckbox.checked,
            technology: state.selectedTechnology,
            use_web: useWebCheckbox.checked,
            use_docs: useDocsCheckbox.checked
        };
        
        // Add OpenRouter model if applicable
        if (modelSelector.value === 'openrouter' && openrouterModelSelector) {
            requestData.openrouter_model = openrouterModelSelector.value;
        }
        
        // Save as last command
        state.lastCommand = command;
        
        // Send to backend
        fetch('/api/process_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Add response to terminal
            const terminalLines = terminalContent.querySelectorAll('div');
            if (terminalLines.length > 0) {
                terminalLines[terminalLines.length - 1].remove(); // Remove "Processing command..."
            }
            
            // Display technology if detected
            if (data.technology && !state.selectedTechnology) {
                addToTerminal(`Detected technology: ${data.technology}`, 'info');
            }
            
            // Display model used if different from default
            if (data.model_used && data.model_used !== DEFAULT_MODEL) {
                addToTerminal(`Using model: ${data.model_used}`, 'info');
            }
            
            // Display AI response
            addToTerminal(data.ai_response, 'output');
            
            // Add to history
            addToHistory({
                command: command,
                response: data.ai_response,
                technology: data.technology || state.selectedTechnology || 'Unknown',
                timestamp: new Date().toISOString()
            });
        })
        .catch(error => {
            console.error('Error processing command:', error);
            addToTerminal(`Error processing command: ${error.message}`, 'error');
        });
    }
    
    // Perform web search
    function performWebSearch(query, numResults = 5) {
        addToTerminal(`Searching web for: ${query}`, 'info');
        
        fetch('/api/web_search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                num_results: numResults
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                addToTerminal(`Found ${data.results.length} results:`, 'success');
                
                data.results.forEach((result, index) => {
                    addToTerminal(`${index + 1}. ${result.title} - ${result.url}`, 'output');
                    addToTerminal(result.summary, 'info');
                });
            } else {
                addToTerminal('No search results found.', 'error');
            }
        })
        .catch(error => {
            console.error('Error searching web:', error);
            addToTerminal(`Error searching web: ${error.message}`, 'error');
        });
    }
    
    // Download documentation
    function downloadDocs(technology = null) {
        const message = technology 
            ? `Starting download of ${technology} documentation...` 
            : 'Starting download of ALL documentation. This may take a while...';
        
        addToTerminal(message, 'info');
        
        fetch('/api/docs/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                technology: technology
            })
        })
        .then(response => response.json())
        .then(data => {
            addToTerminal(data.message || `Documentation download ${data.success ? 'started' : 'failed'}.`, 
                         data.success !== false ? 'success' : 'error');
            
            // Refresh status after a delay
            setTimeout(checkStatus, 5000);
        })
        .catch(error => {
            console.error('Error downloading documentation:', error);
            addToTerminal(`Error downloading documentation: ${error.message}`, 'error');
        });
    }
    
    // Search documentation
    function searchDocs(technology, query, maxResults = 5) {
        if (!technology) {
            addToTerminal('Please select a technology first.', 'error');
            return;
        }
        
        addToTerminal(`Searching ${technology} documentation for: ${query}`, 'info');
        
        fetch('/api/docs/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                technology: technology,
                query: query,
                max_results: maxResults
            })
        })
        .then(response => response.json())
        .then(results => {
            if (results && results.length > 0) {
                addToTerminal(`Found ${results.length} results:`, 'success');
                
                results.forEach((result, index) => {
                    addToTerminal(`${index + 1}. ${result.title}`, 'output');
                    addToTerminal(result.context, 'info');
                });
            } else {
                addToTerminal(`No results found in ${technology} documentation. Consider downloading the documentation first.`, 'error');
            }
        })
        .catch(error => {
            console.error('Error searching documentation:', error);
            addToTerminal(`Error searching documentation: ${error.message}`, 'error');
        });
    }
    
    // Add command to history
    function addToHistory(item) {
        // Add to state
        state.commandHistory.unshift(item);
        if (state.commandHistory.length > 50) {
            state.commandHistory.pop();
        }
        
        // Update UI
        updateHistoryUI();
    }
    
    // Update history UI
    function updateHistoryUI() {
        historyContainer.innerHTML = '';
        
        state.commandHistory.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item bg-dark-900 rounded-lg p-3 border border-gray-800 hover:border-blue-700 cursor-pointer';
            historyItem.onclick = () => {
                commandInput.value = item.command;
                commandInput.focus();
            };
            
            const timestamp = new Date(item.timestamp);
            const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            historyItem.innerHTML = `
                <div class="flex justify-between items-start">
                    <div class="text-blue-400 font-medium text-sm mb-1">${item.technology}</div>
                    <div class="text-gray-500 text-xs">${formattedTime}</div>
                </div>
                <div class="text-gray-300 text-sm mb-1 truncate">${item.command}</div>
                <div class="text-gray-400 text-xs truncate">${item.response}</div>
            `;
            
            historyContainer.appendChild(historyItem);
        });
        
        // If empty, show message
        if (state.commandHistory.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'text-center text-gray-500 py-4';
            emptyMessage.textContent = 'No command history yet';
            historyContainer.appendChild(emptyMessage);
        }
    }
    
    // Fetch command history from server
    function fetchHistory() {
        fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    // Convert to our history format
                    state.commandHistory = data.map(item => ({
                        command: item.user_input,
                        response: item.ai_response,
                        technology: 'Unknown', // Server doesn't store this yet
                        timestamp: item.timestamp
                    }));
                    updateHistoryUI();
                }
            })
            .catch(error => {
                console.error('Error fetching history:', error);
            });
    }
    
    // Select a technology
    function selectTechnology(tech) {
        // Update state
        state.selectedTechnology = tech === 'all' ? null : tech;
        
        // Update UI
        technologyBadges.forEach(badge => {
            if (badge.dataset.tech === tech) {
                badge.classList.add('ring-2', 'ring-blue-500');
            } else {
                badge.classList.remove('ring-2', 'ring-blue-500');
            }
        });
        
        // Update selected tech badge
        if (tech === 'all') {
            selectedTechBadge.classList.add('hidden');
        } else {
            selectedTechBadge.classList.remove('hidden');
            techNameSpan.textContent = tech.charAt(0).toUpperCase() + tech.slice(1);
        }
        
        // Save setting
        saveSettings();
    }
    
    // Update the UI based on documentation status
    function updateDocsUI() {
        // This function would be used if we add UI elements for documentation status
        // For example, adding indicators to show which docs are downloaded
        if (typeof updateDocIndicators === 'function') {
            updateDocIndicators(state.docsStatus);
        }
    }
    
    // Check system status
    function checkStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('System status:', data);
                
                // Save documentation status
                if (data.docs) {
                    state.docsStatus = data.docs;
                    updateDocsUI();
                }
                
                // Save API status
                if (data.apis) {
                    state.apiStatus = data.apis;
                    updateModelOptionsUI();
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
            });
    }
    
    // Update the model selector based on available APIs
    function updateModelOptionsUI() {
        // This would be implemented if we want to dynamically show/hide
        // model options based on what's available
        if (modelSelector) {
            // Enable/disable options based on availability
            Array.from(modelSelector.options).forEach(option => {
                const value = option.value;
                if (value in state.apiStatus) {
                    option.disabled = !state.apiStatus[value];
                    if (option.disabled) {
                        option.title = `${value} API key not configured`;
                    } else {
                        option.title = `${value} API available`;
                    }
                }
            });
        }
    }
    
    // Filter OpenRouter models based on search input
    function filterOpenRouterModels() {
        const searchText = openrouterModelSearch.value.toLowerCase();
        const options = openrouterModelSelector.options;
        
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            const optionText = option.text.toLowerCase();
            const optionValue = option.value.toLowerCase();
            
            // Show/hide options based on matching text in model name or value
            if (optionText.includes(searchText) || optionValue.includes(searchText)) {
                option.style.display = "";
            } else {
                option.style.display = "none";
            }
        }
    }
    
    // Toggle OpenRouter models dropdown visibility
    function toggleOpenRouterModels() {
        if (modelSelector.value === 'openrouter') {
            openrouterModelsContainer.classList.remove('hidden');
        } else {
            openrouterModelsContainer.classList.add('hidden');
        }
    }
    
    // Event Listeners
    sendButton.addEventListener('click', processCommand);
    
    commandInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            processCommand();
        }
    });
    
    micButton.addEventListener('click', toggleSpeechRecognition);
    
    modelSelector.addEventListener('change', function() {
        toggleOpenRouterModels();
        saveSettings();
    });
    
    if (openrouterModelSelector) {
        openrouterModelSelector.addEventListener('change', saveSettings);
    }
    
    if (openrouterModelSearch) {
        openrouterModelSearch.addEventListener('input', filterOpenRouterModels);
    }
    
    executeCommandsCheckbox.addEventListener('change', saveSettings);
    
    // Add event listeners for new UI elements if they exist
    if (useWebCheckbox && 'id' in useWebCheckbox) {
        useWebCheckbox.addEventListener('change', saveSettings);
    }
    
    if (useDocsCheckbox && 'id' in useDocsCheckbox) {
        useDocsCheckbox.addEventListener('change', saveSettings);
    }
    
    technologyBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            selectTechnology(this.dataset.tech);
        });
    });
    
    // Initialize
    loadSettings();
    fetchHistory();
    checkStatus();
    initSpeechRecognition();
    
    // Initial filtering of OpenRouter models if search has a value
    if (openrouterModelSearch && openrouterModelSearch.value.trim()) {
        filterOpenRouterModels();
    }
    
    // Welcome message
    setTimeout(() => {
        addToTerminal('System initialized and ready. You can type or speak your commands.', 'info');
        
        // Check if any documentation is downloaded, if not, suggest downloading
        setTimeout(() => {
            if (state.docsStatus && Object.values(state.docsStatus).every(status => !status)) {
                addToTerminal('No documentation is currently downloaded. Consider downloading documentation for better results.', 'info');
            }
        }, 2000);
    }, 500);
}); 