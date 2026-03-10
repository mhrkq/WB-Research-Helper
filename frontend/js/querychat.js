async function sendMessage() {

    const input = document.getElementById("chatInput");
    const chat = document.getElementById("chatWindow");

    const question = input.value;

    input.value = "";

    const userMsg = document.createElement("p");
    userMsg.innerText = "You: " + question;
    chat.appendChild(userMsg);

    const response = await apiPost("/querychat", {
        query: question
    });

    const botMsg = document.createElement("p");
    botMsg.innerText = "AI: " + response.answer;

    chat.appendChild(botMsg);

}