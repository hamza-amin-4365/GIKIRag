// Add session management
let sessionId = 'session-' + Date.now(); // Generate unique session ID
let chatHistory = []; // Maintain chat history

// GIKI-specific help text
const gikiHelpText = "<span class='sk'>Ask me about GIK Institute! I can provide information on:<br><span class='bold'>'Admissions'</span> - Admission procedures and requirements<br><span class='bold'>'Programs'</span> - Available academic programs (e.g., Computer Science, Engineering)<br><span class='bold'>'Faculty'</span> - Information about faculty members<br><span class='bold'>'Campus'</span> - Campus life and facilities<br><span class='bold'>'News'</span> - Latest news and events<br><span class='bold'>'Alumni'</span> - Alumni Association information<br><span class='bold'>'clear'</span> - to clear conversation<br>Just type your question!";

function startFunction() {
    // Initial welcome message
    sendTextMessage("Hello! I'm the GIKI Assistant. Ask me anything about GIK Institute - Programs, Admissions, Faculty, News, etc.");
    // sendTextMessage(gikiHelpText); // Optionally show help on start
}

function closeFullDP() {
    const x = document.getElementById("fullScreenDP");
    x.style.display = 'none';
}

function openFullScreenDP() {
    const x = document.getElementById("fullScreenDP");
    x.style.display = 'flex';
}

function isEnter(event) {
    if (event.keyCode === 13) {
        sendMsg();
    }
}

function sendMsg() {
    const input = document.getElementById("inputMSG");
    const inputText = input.value.trim(); // Trim whitespace

    if (inputText === "") {
        return; // Don't send empty messages
    }

    const date = new Date();
    const timeString = date.getHours() + ":" + (date.getMinutes() < 10 ? '0' : '') + date.getMinutes(); // Format time

    // Add user message to UI
    const userLI = document.createElement("li");
    userLI.classList.add("sent");
    const userDiv = document.createElement("div");
    userDiv.classList.add("green");
    userDiv.textContent = inputText;
    const userTimeLabel = document.createElement("label");
    userTimeLabel.classList.add("dateLabel");
    userTimeLabel.textContent = timeString;
    userDiv.appendChild(userTimeLabel);
    userLI.appendChild(userDiv);
    document.getElementById("listUL").appendChild(userLI);

    // Clear input and scroll to bottom
    input.value = "";
    scrollToBottom();

    // Show typing indicator
    const typingLI = document.createElement("li");
    typingLI.id = "typingIndicator";
    typingLI.classList.add("received");
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("grey");
    typingDiv.textContent = "Thinking...";
    const typingTimeLabel = document.createElement("label");
    typingTimeLabel.classList.add("dateLabel");
    typingTimeLabel.textContent = timeString;
    typingDiv.appendChild(typingTimeLabel);
    typingLI.appendChild(typingDiv);
    document.getElementById("listUL").appendChild(typingLI);
    scrollToBottom();

    // Call backend API with session ID and history
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            question: inputText,
            session_id: sessionId,
            history: chatHistory  // Send current history
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        const typingElement = document.getElementById("typingIndicator");
        if (typingElement) {
            typingElement.remove();
        }

        // Update chat history with the response
        chatHistory = data.history; // Update with history from the response

        // Add bot response to UI
        const botLI = document.createElement("li");
        botLI.classList.add("received");
        const botDiv = document.createElement("div");
        botDiv.classList.add("grey");
        botDiv.innerHTML = data.answer; // Use innerHTML to render HTML if needed
        const botTimeLabel = document.createElement("label");
        botTimeLabel.classList.add("dateLabel");
        botTimeLabel.textContent = timeString; // Use same time as when request was sent
        botDiv.appendChild(botTimeLabel);
        botLI.appendChild(botDiv);
        document.getElementById("listUL").appendChild(botLI);
        scrollToBottom();
    })
    .catch(error => {
        console.error('Error:', error);
        // Remove typing indicator
        const typingElement = document.getElementById("typingIndicator");
        if (typingElement) {
            typingElement.remove();
        }
        // Add error message
        const errorLI = document.createElement("li");
        errorLI.classList.add("received");
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("grey");
        errorDiv.textContent = "Sorry, I encountered an error processing your request. Please try again.";
        const errorTimeLabel = document.createElement("label");
        errorTimeLabel.classList.add("dateLabel");
        errorTimeLabel.textContent = timeString;
        errorDiv.appendChild(errorTimeLabel);
        errorLI.appendChild(errorDiv);
        document.getElementById("listUL").appendChild(errorLI);
        scrollToBottom();
    });
}

function scrollToBottom() {
    const scrollable = document.getElementById("myScrollable");
    scrollable.scrollTop = scrollable.scrollHeight;
}

// Function to send text messages from the bot (for initial messages or errors)
function sendTextMessage(textToSend) {
    const date = new Date();
    const timeString = date.getHours() + ":" + (date.getMinutes() < 10 ? '0' : '') + date.getMinutes();

    const botLI = document.createElement("li");
    botLI.classList.add("received");
    const botDiv = document.createElement("div");
    botDiv.classList.add("grey");
    botDiv.innerHTML = textToSend; // Use innerHTML to render HTML if needed
    const botTimeLabel = document.createElement("label");
    botTimeLabel.classList.add("dateLabel");
    botTimeLabel.textContent = timeString;
    botDiv.appendChild(botTimeLabel);
    botLI.appendChild(botDiv);
    document.getElementById("listUL").appendChild(botLI);
    scrollToBottom();
}

function clearChat() {
    document.getElementById("listUL").innerHTML = "";
    // Reset session and history
    sessionId = 'session-' + Date.now(); // Generate new session ID
    chatHistory = []; // Clear history
    startFunction(); // Re-add the initial welcome message
}