document.addEventListener('DOMContentLoaded', function() {
    const metricsGrid = document.getElementById('metrics-grid');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const lastUpdated = document.getElementById('last-updated');
    const systemSummary = document.getElementById('system-summary');
    const overallStatus = document.getElementById('overall-status');

    // Format timestamp
    function formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    // Format relative time
    function formatRelativeTime(timestamp) {
        const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
        const diff = (timestamp - Date.now()) / 1000;
        
        if (Math.abs(diff) < 60) return rtf.format(Math.round(diff), 'second');
        if (Math.abs(diff) < 3600) return rtf.format(Math.round(diff / 60), 'minute');
        if (Math.abs(diff) < 86400) return rtf.format(Math.round(diff / 3600), 'hour');
        return rtf.format(Math.round(diff / 86400), 'day');
    }

    // Determine status based on metric values
    function getMetricStatus(metric, value) {
        const thresholds = {
            'CPUUtilization': { warning: 70, critical: 85 },
            'RequestLatency': { warning: 200, critical: 500 },
            'HTTP4xxErrorRate': { warning: 5, critical: 10 },
            'DBConnectionErrors': { warning: 1, critical: 3 }
        };

        const threshold = thresholds[metric];
        if (!threshold) return 'normal';

        if (value >= threshold.critical) return 'critical';
        if (value >= threshold.warning) return 'warning';
        return 'normal';
    }

    // Create metric card
    function createMetricCard(metric) {
        const services = metric.services;
        const cards = [];
        
        for (const [serviceName, serviceData] of Object.entries(services)) {
            const status = serviceData.status;
            const mainMetric = Object.entries(serviceData)
                .find(([key, value]) => 
                    typeof value === 'number' && 
                    !['status'].includes(key)
                );

            if (mainMetric) {
                cards.push(`
                    <div class="col-md-4">
                        <div class="card metric-card">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h6 class="card-title text-secondary mb-0">${serviceName}</h6>
                                    <span class="status-indicator status-${status}"></span>
                                </div>
                                <div class="metric-value">${mainMetric[1]}</div>
                                <div class="metric-label">${mainMetric[0]}</div>
                                <div class="text-muted small mt-2">${serviceData.logs?.[0]?.message || ''}</div>
                                <div class="timestamp mt-2">
                                    ${formatTimestamp(metric.timestamp)}
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            }
        }
        
        return cards.join('');
    }

    // Update system summary
    function updateSystemSummary(metrics) {
        fetch('http://localhost:3000/api/recommendation')
            .then(response => response.json())
            .then(data => {
                const services = metrics[0].services;
                const criticalIssues = Object.values(services)
                    .filter(service => service.status === 'critical').length;
                const warningIssues = Object.values(services)
                    .filter(service => service.status === 'warning').length;

                const overallStatusClass = criticalIssues > 0 ? 'critical' : 
                                         warningIssues > 0 ? 'warning' : 'normal';

                overallStatus.innerHTML = `
                    <i class="fas fa-circle-${criticalIssues > 0 ? 'xmark' : warningIssues > 0 ? 'exclamation' : 'check'} me-1"></i>
                    ${criticalIssues > 0 ? 'Critical Issues Detected' : 
                      warningIssues > 0 ? 'Warnings Present' : 'All Systems Normal'}
                `;
                overallStatus.className = `status-badge status-${overallStatusClass}`;

                systemSummary.innerHTML = `
                    <div class="row">
                        <div class="col-md-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="fas fa-triangle-exclamation fa-lg me-2"></i>
                                <div>
                                    <div class="h4 mb-0">${criticalIssues}</div>
                                    <div class="small">Critical Issues</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="fas fa-exclamation-circle fa-lg me-2"></i>
                                <div>
                                    <div class="h4 mb-0">${warningIssues}</div>
                                    <div class="small">Warnings</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="d-flex align-items-center mb-3">
                                <i class="fas fa-check-circle fa-lg me-2"></i>
                                <div>
                                    <div class="h4 mb-0">${Object.values(services).length - criticalIssues - warningIssues}</div>
                                    <div class="small">Healthy Metrics</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h6 class="mb-2">AI Recommendation:</h6>
                        <div class="mb-0 recommendation-text">${marked.parse(data.recommendation)}</div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error fetching recommendation:', error);
                systemSummary.innerHTML = '<div class="alert alert-danger">Error loading system summary</div>';
            });
    }

    // Fetch metrics from the backend API
    function fetchMetrics() {
        fetch('http://localhost:3000/api/metrics')
            .then(response => response.json())
            .then(data => {
                metricsGrid.innerHTML = data.map(createMetricCard).join('');
                lastUpdated.textContent = `Last updated: ${new Date().toLocaleString()}`;
                updateSystemSummary(data);
            })
            .catch(error => {
                console.error('Error fetching metrics:', error);
                metricsGrid.innerHTML = '<div class="col-12"><div class="alert alert-danger">Error loading metrics</div></div>';
            });
    }

    // Add message to chat window
    function addChatMessage(message, isAI = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isAI ? 'ai-message' : 'user-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (isAI) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-robot message-icon';
            messageContent.appendChild(icon);
            
            const messageText = document.createElement('div');
            messageText.className = 'message-text markdown-content';
            // Use marked to parse markdown for AI messages
            messageText.innerHTML = marked.parse(message);
            // Enable links to open in new tab
            messageText.querySelectorAll('a').forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            });
            messageContent.appendChild(messageText);
        } else {
            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.textContent = message;
            messageContent.appendChild(messageText);
        }
        
        messageDiv.appendChild(messageContent);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        const now = new Date();
        messageTime.innerHTML = `
            <i class="fas fa-clock me-1"></i>
            ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        `;
        messageDiv.appendChild(messageTime);
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Add fade-in animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
    }

    // Suggest question
    window.suggestQuestion = function(question) {
        chatInput.value = question;
        chatInput.focus();
    };

    // Send chat message to the backend API
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addChatMessage(message, false);
        chatInput.value = '';

        fetch('http://localhost:3000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            addChatMessage(data.response, true);
        })
        .catch(error => {
            console.error('Error sending message:', error);
            addChatMessage('Sorry, there was an error processing your message.', true);
        });
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Fetch metrics initially and set an interval to update them
    fetchMetrics();
    setInterval(fetchMetrics, 300000); // Update every 5 minutes
}); 