import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import { sendChatMessage } from "../api/client";

function createMessage(role, content, sources = []) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    sources,
    createdAt: new Date().toISOString(),
  };
}

function getSessionTitle(question) {
  const cleaned = question.trim();

  if (cleaned.length <= 42) {
    return cleaned;
  }

  return `${cleaned.slice(0, 42)}...`;
}

function ChatPanel({ session, onUpdateSession }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  const messages = session?.messages || [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading || !session) {
      return;
    }

    const userMessage = createMessage("user", trimmedQuestion);

    setQuestion("");
    setLoading(true);
    setErrorMessage("");

    onUpdateSession((currentSession) => {
      const shouldRename =
        currentSession.title === "New Chat" ||
        currentSession.messages.length === 0;

      return {
        ...currentSession,
        title: shouldRename
          ? getSessionTitle(trimmedQuestion)
          : currentSession.title,
        updatedAt: new Date().toISOString(),
        messages: [...currentSession.messages, userMessage],
      };
    });

    try {
      const data = await sendChatMessage(trimmedQuestion);
      const assistantMessage = createMessage(
        "assistant",
        data.answer || "No answer returned.",
        data.sources || []
      );

      onUpdateSession((currentSession) => ({
        ...currentSession,
        updatedAt: new Date().toISOString(),
        messages: [...currentSession.messages, assistantMessage],
      }));
    } catch (error) {
      const failedMessage = createMessage(
        "assistant",
        `Sorry, something went wrong: ${error.message}`
      );

      setErrorMessage(error.message);

      onUpdateSession((currentSession) => ({
        ...currentSession,
        updatedAt: new Date().toISOString(),
        messages: [...currentSession.messages, failedMessage],
      }));
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <section className="chat-shell">
      <div className="chat-topbar">
        <div>
          <h1>{session?.title || "New Chat"}</h1>
          <p>Ask general healthcare questions and review the conversation here.</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-chat">
            <div className="empty-icon">✦</div>
            <h2>How can I help with your health question?</h2>
            <p>
              Ask about symptoms, general care advice, uploaded documents, or
              when to seek medical help.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-row ${
              message.role === "user" ? "user-row" : "assistant-row"
            }`}
          >
            {message.role === "assistant" && (
              <div className="message-avatar assistant-avatar">AI</div>
            )}

            <div
              className={`message-bubble ${
                message.role === "user" ? "user-bubble" : "assistant-bubble"
              }`}
            >
              {message.role === "assistant" ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                <p>{message.content}</p>
              )}

              {message.sources && message.sources.length > 0 && (
                <div className="source-box">
                  <div className="source-title">Sources</div>

                  <ul>
                    {message.sources.map((source, index) => (
                      <li key={index}>
                        {source.filename} — chunk {source.chunk_index} — score{" "}
                        {Number(source.score).toFixed(3)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="message-time">
                {new Date(message.createdAt).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            </div>

            {message.role === "user" && (
              <div className="message-avatar user-avatar-small">You</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message-row assistant-row">
            <div className="message-avatar assistant-avatar">AI</div>

            <div className="message-bubble assistant-bubble">
              <div className="typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {errorMessage && <div className="chat-error">{errorMessage}</div>}

      <div className="chat-input-area">
        <div className="chat-input-box">
          <textarea
            ref={textareaRef}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message AI Healthcare Chatbot..."
            rows={1}
          />

          <button onClick={handleSend} disabled={loading || !question.trim()}>
            ➤
          </button>
        </div>

        <div className="input-hint">Press Enter to send • Shift + Enter for new line</div>
      </div>
    </section>
  );
}

export default ChatPanel;