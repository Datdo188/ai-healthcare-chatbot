import { useState } from "react";
import { sendChatMessage } from "../api/client";

function ChatPanel({ onChatSaved }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSend() {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    setLoading(true);
    setMessage("");
    setAnswer("");
    setSources([]);

    try {
      const data = await sendChatMessage(question);

      setAnswer(data.answer);
      setSources(data.sources || []);

      if (onChatSaved) {
        onChatSaved();
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <label>Your question</label>

      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask a general healthcare question..."
      />

      <button onClick={handleSend} disabled={loading}>
        {loading ? "Thinking..." : "Send"}
      </button>

      {message && <div className="notice">{message}</div>}

      {answer && (
        <div className="answer">
          <h3>Answer</h3>
          <p>{answer}</p>

          {sources.length > 0 && (
            <>
              <h4>Sources</h4>
              <ul>
                {sources.map((source, index) => (
                  <li key={index}>
                    {source.filename} — chunk {source.chunk_index} — score{" "}
                    {Number(source.score).toFixed(3)}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </section>
  );
}

export default ChatPanel;