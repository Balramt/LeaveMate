function toggleChatbot() {
    const box = document.getElementById("chatbot-box");
    const toggle = document.getElementById("chatbot-toggle");
    if (box.style.display === "flex") {
        box.style.display = "none";
        toggle.style.display = "flex";
    } else {
        box.style.display = "flex";
        box.style.flexDirection = "column";
        toggle.style.display = "none";
    }
}

function addMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("msg", sender);
    msgDiv.innerText = text;
    document.getElementById("chatbot-messages").appendChild(msgDiv);
    document.getElementById("chatbot-messages").scrollTop =
        document.getElementById("chatbot-messages").scrollHeight;
}

async function sendMessage() {
    const inputField = document.getElementById("chatbot-input");
    const message = inputField.value.trim();
    if (!message) return;
    
    addMessage(message, "user");
    inputField.value = "";

    document.getElementById("chatbot-typing").style.display = "block";

    try {
        const res = await fetch("/admin/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ text: message }),
        });
        const data = await res.json();

        document.getElementById("chatbot-typing").style.display = "none";
        addMessage(data.bot_reply || data.response || data.error || "No response", "bot");
    } catch (err) {
        document.getElementById("chatbot-typing").style.display = "none";
        addMessage("❌ Error: Could not reach chatbot backend", "bot");
    }
}
