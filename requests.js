// Función para enviar el mensaje al servidor
async function sendMessage() {
    const userInput = document.getElementById('user-input'); // Asegúrate que el ID coincida con tu HTML
    const message = userInput.value.trim();

    if (!message) return;

    // Mostrar el mensaje del usuario en la interfaz (opcional, si ya lo haces no repitas)
    // appendMessage(message, 'user-message'); 

    userInput.value = ''; // Limpiar el input

    try {
        // Petición POST a la ruta relativa /chat
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`Error en el servidor: ${response.status}`);
        }

        const data = await response.json();

        // IMPORTANTE: Aquí leemos 'data.response' porque así lo definimos en Flask
        if (data.response) {
            appendMessage(data.response, 'bot-message');
        } else if (data.error) {
            appendMessage("Error: " + data.error, 'error-message');
        }

    } catch (error) {
        console.error("Error al enviar el pase:", error);
        // Mostrar el banner de "Tarjeta Roja" que tienes en tu HTML
        const errorBanner = document.getElementById('error-banner'); 
        if (errorBanner) errorBanner.style.display = 'block';
    }
}

// Función auxiliar para agregar los globos de texto al chat
function appendMessage(text, className) {
    const chatWindow = document.getElementById('chat-window');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    msgDiv.innerText = text;
    chatWindow.appendChild(msgDiv);
    
    // Auto-scroll hacia abajo
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
