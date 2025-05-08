const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

sendBtn.addEventListener('click', () => {
    const userMessage = userInput.value.trim();
    if (userMessage) {
        displayMessage(userMessage, 'user');
        userInput.value = '';
        getResponse(userMessage);
    }
});

function markdownToHtml(text) {
    // Safely escape HTML first
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Convert **bold** to <strong>bold</strong>
    return escaped.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function displayMessage(message, sender) {
  const wrapper = document.createElement('div');
  wrapper.classList.add('message-wrapper', sender);

  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');
  messageDiv.innerHTML = markdownToHtml(message);

  wrapper.appendChild(messageDiv);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop = chatBox.scrollHeight;
}


function getResponse(userMessage) {
    const payload = { query: userMessage };

    fetch('http://localhost:5000/response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        const botMessage = data.response;
        displayMessage(botMessage, 'bot');
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage("Sorry, there was an error processing your request. Please try again.", 'bot');
    });
}
