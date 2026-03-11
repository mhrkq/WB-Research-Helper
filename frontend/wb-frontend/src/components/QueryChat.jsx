import { useState, useRef, useEffect } from "react";
import api from "../api/api";

export default function QueryChat() {
  const [query, setQuery] = useState("");
  const [responses, setResponses] = useState([]);
  const chatEndRef = useRef(null);

  const handleQuery = async () => {
    if (!query.trim()) return;

    try {
      const res = await api.post("/querychat", { query });
      setResponses((prev) => [...prev, { query, answer: res.data.answer }]);
      setQuery("");
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [responses]);

  return (
    <div>
      <div className="chat-window">
        {responses.map((r, idx) => (
          <div key={idx} className="chat-message">
            <span className="chat-label-user">You:</span> {r.query} <br />
            <span className="chat-label-bot">Chatbot:</span> {r.answer}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="chat-controls">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          className="chat-input"
        />
        <button onClick={handleQuery} className="chat-send-button">
          Send
        </button>
      </div>
    </div>
  );
}