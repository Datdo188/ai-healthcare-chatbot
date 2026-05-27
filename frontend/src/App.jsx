import { useEffect, useState } from "react";

import { clearToken, getCurrentUser, getToken } from "./api/client";

import AuthForm from "./components/AuthForm";
import ChatPanel from "./components/ChatPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import HistoryPanel from "./components/HistoryPanel";
import Sidebar from "./components/Sidebar";

import "./App.css";

function App() {
  const [token, setTokenState] = useState(getToken());
  const [user, setUser] = useState(null);

  const [activeTab, setActiveTab] = useState("chat");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadCurrentUser() {
    if (!getToken()) {
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const data = await getCurrentUser();
      setUser(data);
    } catch {
      handleLogout();
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCurrentUser();
  }, [token]);

  function handleAuthenticated(userData) {
    setUser(userData);
    setTokenState(getToken());
    setActiveTab("chat");
  }

  function handleLogout() {
    clearToken();

    setTokenState("");
    setUser(null);
    setActiveTab("chat");
    setMessage("Logged out.");
  }

  if (!token) {
    return <AuthForm onAuthenticated={handleAuthenticated} />;
  }

  return (
    <div className="app">
      <Sidebar
        user={user}
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        onLogout={handleLogout}
      />

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

        {activeTab === "chat" && <ChatPanel />}
        {activeTab === "documents" && <DocumentsPanel />}
        {activeTab === "history" && <HistoryPanel />}
      </main>
    </div>
  );
}

export default App;