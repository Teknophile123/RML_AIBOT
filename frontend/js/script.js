async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();
    if (!message) return;

    // show user message
    chatBox.innerHTML += `<div><b>You:</b> ${message}</div>`;
    input.value = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        // show assistant reply
        chatBox.innerHTML += `<div><b>Tek AI:</b> ${data.text}</div>`;

        // scroll down
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (err) {
        console.error(err);
        chatBox.innerHTML += `<div>Error connecting to server</div>`;
    }
}
