document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("query-form");
    const queryInput = document.getElementById("query");
    const chatBox = document.getElementById("chat-box");

    function appendMessage(text, sender) {
        const msg = document.createElement("div");
        msg.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        msg.innerHTML = text;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendLoading() {
        const msg = document.createElement("div");
        msg.classList.add("message", "bot-message");
        msg.id = "loading-msg";
        msg.innerHTML = `<span class="spinner"></span> Thinking...`;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeLoading() {
        const loading = document.getElementById("loading-msg");
        if (loading) loading.remove();
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage(query, "user");
        queryInput.value = "";

        appendLoading();

        try {
            const response = await fetch("/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error("Failed to fetch answer.");

            const data = await response.json();
            removeLoading();
            appendMessage(data.final_answer, "bot");
        } catch (err) {
            removeLoading();
            appendMessage(`<span style="color:red;">Error: ${err.message}</span>`, "bot");
        }
    });
});
