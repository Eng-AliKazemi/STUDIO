document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('data-form');
    const chatWindow = document.getElementById('chat-window');

    // --- Modal Logic ---
    const settingsModal = document.getElementById('settings-modal');
    const settingsBtn = document.getElementById('settings-btn');
    const closeBtn = document.querySelector('.close-btn');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const tempSlider = document.getElementById('api-temp');
    const tempValue = document.getElementById('temp-value');

    settingsBtn.onclick = () => {
        settingsModal.style.display = 'block';
        const feedback = document.getElementById('settings-feedback');
        feedback.textContent = '';
        feedback.className = ''; // Reset classes
    };
    closeBtn.onclick = () => { settingsModal.style.display = 'none'; };
    window.onclick = (event) => { if (event.target == settingsModal) { settingsModal.style.display = 'none'; } };
    
    tempSlider.oninput = () => { tempValue.textContent = tempSlider.value; };

    // --- Settings Save Logic ---
    saveSettingsBtn.addEventListener('click', async () => {
        const settingsData = {
            provider_url: document.getElementById('api-provider').value,
            model_name: document.getElementById('api-model').value,
            temperature: parseFloat(document.getElementById('api-temp').value)
        };

        const feedback = document.getElementById('settings-feedback');
        feedback.textContent = 'Saving...';
        feedback.className = ''; // Clear previous success/error states

        try {
            const response = await fetch('/update-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settingsData)
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Failed to save settings.');
            
            feedback.textContent = result.message;
            // FIX: Use CSS classes instead of inline styles
            feedback.classList.add('feedback-success');

            setTimeout(() => { settingsModal.style.display = 'none'; }, 1500);

        } catch (error) {
            feedback.textContent = error.message;
            // FIX: Use CSS classes instead of inline styles
            feedback.classList.add('feedback-error');
        }
    });

    // --- Form Submission Logic (unchanged from previous version) ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            daily_revenue: document.getElementById('daily_revenue').value,
            daily_cost: document.getElementById('daily_cost').value,
            daily_customers: document.getElementById('daily_customers').value,
            prev_revenue: document.getElementById('prev_revenue').value,
            prev_cost: document.getElementById('prev_cost').value,
            prev_customers: document.getElementById('prev_customers').value
        };
        
        displayUserMessage(data);
        const loadingMessage = displayAgentMessage("Analyzing...", true);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: new URLSearchParams(data)
            });
            chatWindow.removeChild(loadingMessage);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            displayAgentReport(result.report);
        } catch (error) {
            chatWindow.removeChild(loadingMessage);
            displayAgentMessage(`Error: ${error.message}`);
        }
    });

    function displayUserMessage(data) {
        const messageText = `Today:\n- Revenue: $${data.daily_revenue}, Cost: $${data.daily_cost}, Customers: ${data.daily_customers}\n\nPrevious Day:\n- Revenue: $${data.prev_revenue}, Cost: $${data.prev_cost}, Customers: ${data.prev_customers}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p style="white-space: pre-wrap;">${messageText}</p>`;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function displayAgentMessage(text, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message agent-message';
        messageDiv.innerHTML = isLoading ? `<p>${text} <i class="fas fa-spinner fa-spin"></i></p>` : `<p>${text}</p>`;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return messageDiv;
    }
    
    function displayAgentReport(report) {
        // FIX: Re-structured to prevent invalid whitespace in <ul> elements
        const createList = (items) => {
            if (!items || items.length === 0) return '';
            return `<ul>${items.map(item => `<li>${item}</li>`).join('')}</ul>`;
        };

        const warningsList = createList(report.alerts_or_warnings);
        const recommendationsList = createList(report.decision_making_recommendations);
        
        let html = '<div class="report-card">';
        html += `<h3>Analysis Report</h3><p><strong>Status:</strong> ${report.profit_loss_status}</p>`;
        if (warningsList) {
            html += `<h4>⚠️ Alerts</h4>${warningsList}`;
        }
        if (recommendationsList) {
            html += `<h4>💡 Recommendations</h4>${recommendationsList}`;
        }
        html += '</div>';

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message agent-message';
        messageDiv.innerHTML = html;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});