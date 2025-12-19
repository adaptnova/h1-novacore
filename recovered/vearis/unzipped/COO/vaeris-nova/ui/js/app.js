/**
 * Vaeris Nova - Main Application
 * 
 * This script handles the core functionality of the Vaeris Nova application,
 * including server communication, message handling, and UI state management.
 */

// Global state
const state = {
    connected: false,
    processing: false,
    socket: null,
    activeModel: 'gpt-4o',
    tools: {},
    settings: {
        streamResponses: true,
        temperature: 0.7,
        maxIterations: 15,
        showTimestamps: true,
        theme: 'dark'
    },
    agents: {},
    currentStreamingMessage: null,
    activityLog: []
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    connectToServer();
});

/**
 * Initialize UI components and event listeners
 */
function initializeUI() {
    // Initialize message input and send button
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    
    // Auto-resize textarea as user types
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    });
    
    // Send message on button click
    sendButton.addEventListener('click', () => {
        sendMessage();
    });
    
    // Send message on Enter (but allow Shift+Enter for new lines)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Initialize settings button
    const settingsButton = document.getElementById('settingsButton');
    const settingsModal = document.getElementById('settingsModal');
    const closeButtons = document.querySelectorAll('.close-button');
    
    settingsButton.addEventListener('click', () => {
        settingsModal.classList.add('active');
        loadSettingsIntoModal();
    });
    
    // Close modals when clicking the close button
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('active');
            });
        });
    });
    
    // Close modals when clicking outside the modal content
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    // Save settings
    const saveSettingsButton = document.getElementById('saveSettingsButton');
    saveSettingsButton.addEventListener('click', saveSettings);
    
    // Initialize model selector
    const modelSelect = document.getElementById('modelSelect');
    modelSelect.addEventListener('change', (e) => {
        state.activeModel = e.target.value;
        if (state.connected) {
            state.socket.emit('update_settings', { model: state.activeModel });
        }
    });
    
    // Initialize agent creation
    const createAgentButton = document.getElementById('createAgentButton');
    const agentCreationModal = document.getElementById('agentCreationModal');
    
    createAgentButton.addEventListener('click', () => {
        agentCreationModal.classList.add('active');
    });
    
    const createAgentSubmitButton = document.getElementById('createAgentSubmitButton');
    createAgentSubmitButton.addEventListener('click', createSubAgent);
    
    // Initialize memory settings
    const memoryDepthSlider = document.getElementById('memoryDepth');
    const memoryDepthValue = document.getElementById('memoryDepthValue');
    
    memoryDepthSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        memoryDepthValue.textContent = `${value} messages`;
    });
    
    const clearMemoryButton = document.getElementById('clearMemoryButton');
    clearMemoryButton.addEventListener('click', clearMemory);
    
    // Initialize theme settings
    const themeSelector = document.getElementById('themeSelector');
    themeSelector.addEventListener('change', (e) => {
        setTheme(e.target.value);
    });
    
    // Set initial theme
    setTheme(state.settings.theme);
}

/**
 * Connect to the server via WebSocket
 */
function connectToServer() {
    // Create socket connection
    state.socket = io(window.location.origin);
    
    // Connection event
    state.socket.on('connect', () => {
        state.connected = true;
        logActivity('Connected to server');
        document.getElementById('sendButton').disabled = false;
    });
    
    // Disconnection event
    state.socket.on('disconnect', () => {
        state.connected = false;
        logActivity('Disconnected from server');
        document.getElementById('sendButton').disabled = true;
    });
    
    // Status updates
    state.socket.on('status', (data) => {
        updateStatus(data);
    });
    
    // Message response
    state.socket.on('response', (data) => {
        displayResponse(data);
    });
    
    // Stream chunks
    state.socket.on('stream', (data) => {
        if (state.settings.streamResponses) {
            updateStreamingMessage(data.chunk, data.agent_id);
        }
    });
    
    // Error handling
    state.socket.on('error', (data) => {
        displayError(data.message);
    });
    
    // Agent creation response
    state.socket.on('agent_created', (data) => {
        handleAgentCreated(data);
    });
    
    // Memory cleared confirmation
    state.socket.on('memory_cleared', (data) => {
        logActivity(`Memory cleared ${data.agent_id ? `for agent ${data.agent_id}` : ''}`);
    });
    
    // Activity log
    state.socket.on('activity_log', (data) => {
        state.activityLog = data.activities;
        updateActivityLog();
    });
}

/**
 * Send a message to the server
 */
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message || !state.connected || state.processing) {
        return;
    }
    
    // Display user message
    displayMessage('user', message);
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Set processing state
    state.processing = true;
    document.getElementById('sendButton').disabled = true;
    
    // Send message to server
    state.socket.emit('message', { message });
    
    // Prepare for streaming if enabled
    if (state.settings.streamResponses) {
        // Add empty AI message for streaming
        state.currentStreamingMessage = addMessageElement('ai');
    }
    
    // Log activity
    logActivity(`Sent message: ${message.substring(0, 30)}${message.length > 30 ? '...' : ''}`);
    
    // Update UI
    updateResponseTimeDisplay(0);
}

/**
 * Display a message in the chat
 */
function displayMessage(role, content, agentId = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');
    
    // Set appropriate class based on role
    messageElement.className = `message ${role}`;
    
    // Create message header with sender and timestamp
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const sender = document.createElement('span');
    sender.className = 'message-sender';
    sender.textContent = getSenderName(role, agentId);
    
    const timestamp = document.createElement('span');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    header.appendChild(sender);
    header.appendChild(timestamp);
    
    // Create message content
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Parse markdown if it's not a user message
    if (role !== 'user') {
        messageContent.innerHTML = marked.parse(content);
        
        // Highlight code blocks
        messageContent.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    } else {
        // Simple text for user messages
        messageContent.textContent = content;
    }
    
    // Assemble message
    messageElement.appendChild(header);
    messageElement.appendChild(messageContent);
    
    // Add to chat
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageElement;
}

/**
 * Add a message element to the chat (for streaming)
 */
function addMessageElement(role, agentId = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');
    
    // Set appropriate class based on role
    messageElement.className = `message ${role}`;
    
    // Create message header with sender and timestamp
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const sender = document.createElement('span');
    sender.className = 'message-sender';
    sender.textContent = getSenderName(role, agentId);
    
    const timestamp = document.createElement('span');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    header.appendChild(sender);
    header.appendChild(timestamp);
    
    // Create message content
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Assemble message
    messageElement.appendChild(header);
    messageElement.appendChild(messageContent);
    
    // Add to chat
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageElement;
}

/**
 * Update a streaming message with new content
 */
function updateStreamingMessage(chunk, agentId = null) {
    if (!state.currentStreamingMessage) {
        state.currentStreamingMessage = addMessageElement('ai', agentId);
    }
    
    const content = state.currentStreamingMessage.querySelector('.message-content');
    
    // Append the new chunk
    let currentContent = content.innerHTML;
    content.innerHTML = currentContent + chunk;
    
    // Scroll to bottom
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Display a response from the server
 */
function displayResponse(data) {
    // If streaming is enabled, we've already been building the message
    if (state.settings.streamResponses && state.currentStreamingMessage) {
        // Replace current streaming message with properly formatted markdown
        const content = state.currentStreamingMessage.querySelector('.message-content');
        content.innerHTML = marked.parse(data.message);
        
        // Highlight code blocks
        content.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        state.currentStreamingMessage = null;
    } else {
        // Otherwise, display the full message at once
        displayMessage('ai', data.message, data.agent_id);
    }
    
    // Reset processing state
    state.processing = false;
    document.getElementById('sendButton').disabled = false;
    
    // Update UI
    updateResponseTimeDisplay(data.processing_time ? data.processing_time * 1000 : 0);
    updateToolsUsedDisplay(data.tools_used ? data.tools_used.length : 0);
    
    // Log activity
    logActivity(`Received response (${data.processing_time ? Math.round(data.processing_time * 1000) : '?'}ms)`);
}

/**
 * Display an error message
 */
function displayError(message) {
    // Create system message for the error
    displayMessage('system', `**Error:** ${message}`);
    
    // Reset processing state
    state.processing = false;
    document.getElementById('sendButton').disabled = false;
    
    // Clear any streaming message
    state.currentStreamingMessage = null;
    
    // Log activity
    logActivity(`Error: ${message}`);
}

/**
 * Update application status
 */
function updateStatus(data) {
    // Update UI based on status
    if (data.status === 'processing') {
        state.processing = true;
        document.getElementById('sendButton').disabled = true;
    } else if (data.status === 'ready') {
        state.processing = false;
        document.getElementById('sendButton').disabled = false;
    } else if (data.status === 'error') {
        state.processing = false;
        document.getElementById('sendButton').disabled = false;
        displayError(data.message);
    }
    
    // Log activity
    logActivity(`Status: ${data.status}${data.message ? ` - ${data.message}` : ''}`);
}

/**
 * Clear memory
 */
function clearMemory() {
    if (!state.connected) {
        return;
    }
    
    state.socket.emit('clear_memory', {});
    logActivity('Clearing memory...');
}

/**
 * Create a new sub-agent
 */
function createSubAgent() {
    if (!state.connected) {
        return;
    }
    
    const agentName = document.getElementById('agentName').value.trim();
    const agentModel = document.getElementById('agentModel').value;
    const agentSpecialization = document.getElementById('agentSpecialization').value;
    const agentDescription = document.getElementById('agentDescription').value.trim();
    
    if (!agentName) {
        displayError('Agent name is required');
        return;
    }
    
    // Get selected tool categories
    const codeTools = document.getElementById('agentCodeTools').checked;
    const searchTools = document.getElementById('agentSearchTools').checked;
    const fileTools = document.getElementById('agentFileTools').checked;
    
    // Create agent
    state.socket.emit('create_agent', {
        name: agentName,
        model: agentModel,
        specialization: agentSpecialization,
        system_prompt: agentDescription,
        tools: {
            code: codeTools,
            search: searchTools,
            file: fileTools
        }
    });
    
    // Log activity
    logActivity(`Creating agent: ${agentName} (${agentModel})`);
    
    // Close modal
    document.getElementById('agentCreationModal').classList.remove('active');
}

/**
 * Handle agent creation response
 */
function handleAgentCreated(data) {
    // Store agent information
    state.agents[data.agent_id] = {
        id: data.agent_id,
        name: data.name,
        model: data.model,
        specialization: data.specialization
    };
    
    // Add agent to UI
    addAgentToUI(data);
    
    // Update agent count
    updateActiveAgentsDisplay(Object.keys(state.agents).length + 1); // +1 for main agent
    
    // Display system message about agent creation
    displayMessage('system', `Created agent **${data.name}** with model ${data.model}`);
    
    // Log activity
    logActivity(`Agent created: ${data.name} (${data.agent_id})`);
}

/**
 * Add agent to UI
 */
function addAgentToUI(agentData) {
    const agentList = document.getElementById('agentList');
    
    const agentCard = document.createElement('div');
    agentCard.className = 'agent-card';
    agentCard.dataset.agentId = agentData.agent_id;
    
    const header = document.createElement('div');
    header.className = 'agent-card-header';
    
    const agentInfo = document.createElement('div');
    agentInfo.className = 'agent-info';
    
    const agentName = document.createElement('span');
    agentName.className = 'agent-name';
    agentName.textContent = agentData.name;
    
    const agentModel = document.createElement('span');
    agentModel.className = 'agent-model';
    agentModel.textContent = agentData.model;
    
    agentInfo.appendChild(agentName);
    agentInfo.appendChild(agentModel);
    
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'agent-actions';
    
    const chatButton = document.createElement('button');
    chatButton.className = 'agent-action-button';
    chatButton.textContent = 'Chat';
    chatButton.addEventListener('click', () => {
        // TODO: Implement agent chat
    });
    
    const clearButton = document.createElement('button');
    clearButton.className = 'agent-action-button';
    clearButton.textContent = 'Clear';
    clearButton.addEventListener('click', () => {
        clearAgentMemory(agentData.agent_id);
    });
    
    actionsContainer.appendChild(chatButton);
    actionsContainer.appendChild(clearButton);
    
    header.appendChild(agentInfo);
    header.appendChild(actionsContainer);
    
    agentCard.appendChild(header);
    agentList.appendChild(agentCard);
}

/**
 * Clear agent memory
 */
function clearAgentMemory(agentId) {
    if (!state.connected) {
        return;
    }
    
    state.socket.emit('clear_memory', { agent_id: agentId });
    logActivity(`Clearing memory for agent ${agentId}...`);
}

/**
 * Log activity to the activity log
 */
function logActivity(message) {
    const timestamp = new Date().toLocaleTimeString();
    state.activityLog.push({
        timestamp: Date.now() / 1000,
        message: message
    });
    
    // Update activity log display
    updateActivityLog();
}

/**
 * Update activity log display
 */
function updateActivityLog() {
    const activityLog = document.getElementById('activityLog');
    
    // Sort activities by timestamp (newest first)
    const sortedActivities = [...state.activityLog].sort((a, b) => b.timestamp - a.timestamp);
    
    // Limit to 50 most recent
    const recentActivities = sortedActivities.slice(0, 50);
    
    // Clear current log
    activityLog.innerHTML = '';
    
    // Add activities
    recentActivities.forEach(activity => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        // Format timestamp
        const date = new Date(activity.timestamp * 1000);
        const timestamp = date.toLocaleTimeString();
        
        entry.textContent = `${timestamp}: ${activity.message}`;
        activityLog.appendChild(entry);
    });
}

/**
 * Update response time display
 */
function updateResponseTimeDisplay(time) {
    const responseTimeValue = document.getElementById('responseTimeValue');
    responseTimeValue.textContent = `${Math.round(time)}ms`;
}

/**
 * Update tools used display
 */
function updateToolsUsedDisplay(count) {
    const toolsUsedValue = document.getElementById('toolsUsedValue');
    toolsUsedValue.textContent = count;
}

/**
 * Update active agents display
 */
function updateActiveAgentsDisplay(count) {
    const activeAgentsValue = document.getElementById('activeAgentsValue');
    activeAgentsValue.textContent = count;
}

/**
 * Load settings into the settings modal
 */
function loadSettingsIntoModal() {
    // API keys
    document.getElementById('openaiApiKey').value = localStorage.getItem('openai_api_key') || '';
    document.getElementById('anthropicApiKey').value = localStorage.getItem('anthropic_api_key') || '';
    document.getElementById('googleApiKey').value = localStorage.getItem('google_api_key') || '';
    document.getElementById('mistralApiKey').value = localStorage.getItem('mistral_api_key') || '';
    
    // UI settings
    document.getElementById('themeSelector').value = state.settings.theme;
    document.getElementById('showTimestamps').checked = state.settings.showTimestamps;
    
    // Agent settings
    document.getElementById('maxIterations').value = state.settings.maxIterations;
    document.getElementById('responseTemperature').value = state.settings.temperature;
    document.getElementById('temperatureValue').textContent = state.settings.temperature;
    document.getElementById('streamResponses').checked = state.settings.streamResponses;
}

/**
 * Save settings from the settings modal
 */
function saveSettings() {
    // API keys
    const openaiApiKey = document.getElementById('openaiApiKey').value.trim();
    const anthropicApiKey = document.getElementById('anthropicApiKey').value.trim();
    const googleApiKey = document.getElementById('googleApiKey').value.trim();
    const mistralApiKey = document.getElementById('mistralApiKey').value.trim();
    
    // Store API keys securely
    if (openaiApiKey) localStorage.setItem('openai_api_key', openaiApiKey);
    if (anthropicApiKey) localStorage.setItem('anthropic_api_key', anthropicApiKey);
    if (googleApiKey) localStorage.setItem('google_api_key', googleApiKey);
    if (mistralApiKey) localStorage.setItem('mistral_api_key', mistralApiKey);
    
    // UI settings
    const theme = document.getElementById('themeSelector').value;
    const showTimestamps = document.getElementById('showTimestamps').checked;
    
    // Agent settings
    const maxIterations = parseInt(document.getElementById('maxIterations').value, 10);
    const temperature = parseFloat(document.getElementById('responseTemperature').value);
    const streamResponses = document.getElementById('streamResponses').checked;
    
    // Update state
    state.settings.theme = theme;
    state.settings.showTimestamps = showTimestamps;
    state.settings.maxIterations = maxIterations;
    state.settings.temperature = temperature;
    state.settings.streamResponses = streamResponses;
    
    // Apply theme
    setTheme(theme);
    
    // Update server settings
    if (state.connected) {
        state.socket.emit('update_settings', {
            max_iterations: maxIterations,
            temperature: temperature,
            stream_responses: streamResponses
        });
    }
    
    // Close modal
    document.getElementById('settingsModal').classList.remove('active');
    
    // Log activity
    logActivity('Settings saved');
}

/**
 * Set the application theme
 */
function setTheme(theme) {
    const body = document.body;
    
    // Remove all theme classes
    body.classList.remove('dark-theme', 'darker-theme', 'light-theme');
    
    // Add the selected theme class
    body.classList.add(`${theme}-theme`);
    
    // Update state
    state.settings.theme = theme;
}

/**
 * Get sender name based on role and agent ID
 */
function getSenderName(role, agentId = null) {
    if (role === 'user') {
        return 'You';
    } else if (role === 'system') {
        return 'System';
    } else if (agentId && state.agents[agentId]) {
        return state.agents[agentId].name;
    } else {
        return 'Vaeris';
    }
}