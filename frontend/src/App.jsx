import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("chat");

  const [token, setToken] = useState(localStorage.getItem("access_token") || "");
  const [user, setUser] = useState(null);

  const [authMode, setAuthMode] = useState("login");
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("123456");
  const [fullName, setFullName] = useState("Test User");

  const [question, setQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatSources, setChatSources] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);

  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const authHeaders = token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};

  useEffect(() => {
    if (token) {
      fetchMe();
      fetchDocuments();
      fetchChatHistory();
    }
  }, [token]);

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
      },
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = data?.detail || "Request failed";
      throw new Error(detail);
    }

    return data;
  }

  async function handleRegister() {
    setLoading(true);
    setMessage("");

    try {
      await request("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
        }),
      });

      setMessage("Register successful. You can login now.");
      setAuthMode("login");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin() {
    setLoading(true);
    setMessage("");

    try {
      const data = await request("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      setMessage("Login successful.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchMe() {
    try {
      const data = await request("/auth/me", {
        headers: {
          ...authHeaders,
        },
      });

      setUser(data);
    } catch {
      handleLogout();
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    setToken("");
    setUser(null);
    setChatAnswer("");
    setChatSources([]);
    setChatHistory([]);
    setDocuments([]);
    setMessage("Logged out.");
  }

  async function sendChat() {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    setLoading(true);
    setMessage("");
    setChatAnswer("");
    setChatSources([]);

    try {
      const data = await request("/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders,
        },
        body: JSON.stringify({
          question,
        }),
      });

      setChatAnswer(data.answer);
      setChatSources(data.sources || []);
      fetchChatHistory();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchChatHistory() {
    try {
      const data = await request("/chat/history", {
        headers: {
          ...authHeaders,
        },
      });

      setChatHistory(data.history || []);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function deleteChatHistory() {
    setLoading(true);
    setMessage("");

    try {
      const data = await request("/chat/history", {
        method: "DELETE",
        headers: {
          ...authHeaders,
        },
      });

      setMessage(data.message);
      setChatHistory([]);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function uploadDocument() {
    if (!selectedFile) {
      setMessage("Please choose a PDF or TXT file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setMessage("");

    try {
      const data = await request("/documents/upload", {
        method: "POST",
        headers: {
          ...authHeaders,
        },
        body: formData,
      });

      setMessage(`Uploaded: ${data.saved_filename}`);
      setSelectedFile(null);
      fetchDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function fetchDocuments() {
    try {
      const data = await request("/documents/", {
        headers: {
          ...authHeaders,
        },
      });

      setDocuments(data.documents || []);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function indexDocument(filename) {
    setLoading(true);
    setMessage("");

    try {
      const data = await request(`/documents/${filename}/index`, {
        method: "POST",
        headers: {
          ...authHeaders,
        },
      });

      setMessage(data.message);
      fetchDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function previewDocument(filename) {
    setLoading(true);
    setMessage("");
    setPreview("");

    try {
      const data = await request(`/documents/${filename}/preview`, {
        headers: {
          ...authHeaders,
        },
      });

      setPreview(data.preview);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteDocument(filename) {
    setLoading(true);
    setMessage("");

    try {
      const data = await request(`/documents/${filename}`, {
        method: "DELETE",
        headers: {
          ...authHeaders,
        },
      });

      setMessage(data.message);
      setPreview("");
      fetchDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="page">
        <div className="auth-card">
          <h1>AI Healthcare Assistant</h1>
          <p className="muted">Login or register to use your healthcare chatbot.</p>

          <div className="tabs">
            <button
              className={authMode === "login" ? "active" : ""}
              onClick={() => setAuthMode("login")}
            >
              Login
            </button>
            <button
              className={authMode === "register" ? "active" : ""}
              onClick={() => setAuthMode("register")}
            >
              Register
            </button>
          </div>

          {authMode === "register" && (
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              placeholder="Full name"
            />
          )}

          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
          />

          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            type="password"
          />

          {authMode === "login" ? (
            <button onClick={handleLogin} disabled={loading}>
              Login
            </button>
          ) : (
            <button onClick={handleRegister} disabled={loading}>
              Register
            </button>
          )}

          {message && <p className="message">{message}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>Healthcare AI</h2>

        <div className="user-box">
          <strong>{user?.full_name || "User"}</strong>
          <span>{user?.email}</span>
        </div>

        <button
          className={activeTab === "chat" ? "active" : ""}
          onClick={() => setActiveTab("chat")}
        >
          Chat
        </button>

        <button
          className={activeTab === "documents" ? "active" : ""}
          onClick={() => setActiveTab("documents")}
        >
          Documents
        </button>

        <button
          className={activeTab === "history" ? "active" : ""}
          onClick={() => setActiveTab("history")}
        >
          History
        </button>

        <button className="logout" onClick={handleLogout}>
          Logout
        </button>
      </aside>

      <main className="main">
        <div className="topbar">
          <h1>
            {activeTab === "chat" && "Chat"}
            {activeTab === "documents" && "Documents"}
            {activeTab === "history" && "Chat History"}
          </h1>

          {loading && <span className="loading">Loading...</span>}
        </div>

        {message && <div className="notice">{message}</div>}

        {activeTab === "chat" && (
          <section className="card">
            <label>Your question</label>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a general healthcare question..."
            />

            <button onClick={sendChat} disabled={loading}>
              Send
            </button>

            {chatAnswer && (
              <div className="answer">
                <h3>Answer</h3>
                <p>{chatAnswer}</p>

                {chatSources.length > 0 && (
                  <>
                    <h4>Sources</h4>
                    <ul>
                      {chatSources.map((source, index) => (
                        <li key={index}>
                          {source.filename} — chunk {source.chunk_index} — score{" "}
                          {source.score}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </section>
        )}

        {activeTab === "documents" && (
          <section className="card">
            <h3>Upload medical document</h3>

            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
            />

            <button onClick={uploadDocument} disabled={loading}>
              Upload
            </button>

            <div className="section-header">
              <h3>Your documents</h3>
              <button onClick={fetchDocuments}>Refresh</button>
            </div>

            <div className="doc-list">
              {documents.map((document) => (
                <div className="doc-item" key={document.id}>
                  <div>
                    <strong>{document.original_filename}</strong>
                    <p>{document.saved_filename}</p>
                    <span>Status: {document.status}</span>
                  </div>

                  <div className="doc-actions">
                    <button onClick={() => previewDocument(document.saved_filename)}>
                      Preview
                    </button>
                    <button onClick={() => indexDocument(document.saved_filename)}>
                      Index
                    </button>
                    <button
                      className="danger"
                      onClick={() => deleteDocument(document.saved_filename)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}

              {documents.length === 0 && <p className="muted">No documents yet.</p>}
            </div>

            {preview && (
              <div className="preview">
                <h3>Preview</h3>
                <pre>{preview}</pre>
              </div>
            )}
          </section>
        )}

        {activeTab === "history" && (
          <section className="card">
            <div className="section-header">
              <h3>Recent conversations</h3>
              <button className="danger" onClick={deleteChatHistory}>
                Clear history
              </button>
            </div>

            {chatHistory.map((item) => (
              <div className="history-item" key={item.id}>
                <strong>Q: {item.question}</strong>
                <p>A: {item.answer}</p>
                <small>{new Date(item.created_at).toLocaleString()}</small>
              </div>
            ))}

            {chatHistory.length === 0 && <p className="muted">No chat history yet.</p>}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;