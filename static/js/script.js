document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question-input');
    const chatHistory = document.getElementById('chat-history');
    const clearBtn = document.getElementById('clear-btn');
    const uploadForm = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');

    // Function to add a message to the chat history
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);
        chatHistory.appendChild(messageDiv);

        // Scroll to the bottom of the chat history
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Function to clear the welcome message if it exists
    function clearWelcomeMessage() {
        const welcomeMessage = chatHistory.querySelector('.welcome-message');
        if (welcomeMessage) {
            chatHistory.removeChild(welcomeMessage);
        }
    }

    // Handle question form submission
    questionForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const question = questionInput.value.trim();
        if (!question) return;

        // Clear the welcome message if it exists
        clearWelcomeMessage();

        // Add the user's question to the chat
        addMessage(question, true);

        // Clear the input field
        questionInput.value = '';

        // Add a temporary "thinking" message
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message ai-message thinking';
        thinkingDiv.innerHTML = '<div class="message-content">Thinking...</div>';
        chatHistory.appendChild(thinkingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        // Get form data
        const formData = new FormData();
        formData.append('question', question);

        // Send request to the server
        fetch('/ask', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Remove the thinking message
            chatHistory.removeChild(thinkingDiv);

            if (data.status === 'success') {
                // Add the AI's response to the chat
                addMessage(data.response);
            } else {
                // Add an error message
                addMessage(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            // Remove the thinking message
            chatHistory.removeChild(thinkingDiv);

            // Add an error message
            addMessage(`Error: ${error.message}`);
        });
    });

    // Handle clear button click
    clearBtn.addEventListener('click', function() {
        // Send request to clear chat history
        fetch('/clear_history', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear the chat history UI
                chatHistory.innerHTML = `
                    <div class="welcome-message">
                        <p>Hello! I'm a simple AI assistant. Ask me a question to get started.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error clearing chat history:', error);
        });
    });

    // Handle corpus upload form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Show loading state
        uploadStatus.innerHTML = 'Uploading...';
        uploadStatus.className = '';

        // Get form data
        const formData = new FormData(uploadForm);

        // Send request to the server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                uploadStatus.innerHTML = data.message;
                uploadStatus.className = 'success';
                // Clear the file input
                document.getElementById('corpus-file').value = '';

                // Add a system message to the chat
                clearWelcomeMessage();
                addMessage("I've learned new information from the uploaded file. Feel free to ask me about it!");
            } else {
                uploadStatus.innerHTML = `Error: ${data.message}`;
                uploadStatus.className = 'error';
            }
        })
        .catch(error => {
            uploadStatus.innerHTML = `Error: ${error.message}`;
            uploadStatus.className = 'error';
        });
    });
});
