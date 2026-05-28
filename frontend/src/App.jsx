import { useEffect, useState } from "react";

import { clearToken, getCurrentUser, getToken } from "./api/client";

import AuthForm from "./components/AuthForm";
import ChatPanel from "./components/ChatPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import Sidebar from "./components/Sidebar";

import "./App.css";

const CHAT_STORAGE_KEY = "ai_healthcare_chat_sessions";

function createNewSession() {
  const now = new Date().toISOString();

  return {
    id: crypto.randomUUID(),
    title: "New Chat",
    createdAt: now,
    updatedAt: now,
    messages: [],
  };
}

function loadSessionsFromStorage() {
  try {
    const raw = localStorage.getItem(CHAT_STORAGE_KEY);

    if (!raw) {
      return [createNewSession()];
    }

    const parsed = JSON.parse(raw);

    if (!Array.isArray(parsed) || parsed.length === 0) {
      return [createNewSession()];
    }

    return parsed;
  } catch {
    return [createNewSession()];
  }
}

function App() {
  const [token, setTokenState] = useState(getToken());
  const [user, setUser] = useState(null);

  const [sessions, setSessions] = useState(loadSessionsFromStorage);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeView, setActiveView] = useState("chat");

  const [loadingUser, setLoadingUser] = useState(false);
  const [message, setMessage] = useState("");

  const activeSession =
    sessions.find((session) => session.id === activeSessionId) || sessions[0];

  useEffect(() => {
    if (!activeSessionId && sessions.length > 0) {
      setActiveSessionId(sessions[0].id);
    }
  }, [activeSessionId, sessions]);

  useEffect(() => {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(sessions));
  }, [sessions]);

  async function loadCurrentUser() {
    if (!getToken()) {
      return;
    }

    setLoadingUser(true);
    setMessage("");

    try {
      const data = await getCurrentUser();
      setUser(data);
    } catch {
      handleLogout();
    } finally {
      setLoadingUser(false);
    }
  }

  useEffect(() => {
    loadCurrentUser();
  }, [token]);

  function handleAuthenticated(userData) {
    setUser(userData);
    setTokenState(getToken());
    setActiveView("chat");
  }

  function handleLogout() {
    clearToken();

    setTokenState("");
    setUser(null);
    setMessage("Logged out.");
  }

  function handleNewChat() {
    const newSession = createNewSession();

    setSessions((previousSessions) => [newSession, ...previousSessions]);
    setActiveSessionId(newSession.id);
    setActiveView("chat");
  }

  function handleSelectSession(sessionId) {
    setActiveSessionId(sessionId);
    setActiveView("chat");
  }

  function handleUpdateActiveSession(updater) {
    if (!activeSession) {
      return;
    }

    setSessions((previousSessions) =>
      previousSessions.map((session) => {
        if (session.id !== activeSession.id) {
          return session;
        }

        return updater(session);
      })
    );
  }

  function handleClearHistory() {
    const newSession = createNewSession();

    setSessions([newSession]);
    setActiveSessionId(newSession.id);
    setActiveView("chat");
  }

  if (!token) {
    return <AuthForm onAuthenticated={handleAuthenticated} />;
  }

  return (
    <div className="chatgpt-layout">
      <Sidebar
        user={user}
        sessions={sessions}
        activeSessionId={activeSession?.id}
        activeView={activeView}
        loadingUser={loadingUser}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onOpenDocuments={() => setActiveView("documents")}
        onClearHistory={handleClearHistory}
        onLogout={handleLogout}
      />

      <main className="chatgpt-main">
        {message && <div className="notice app-notice">{message}</div>}

        {activeView === "chat" && (
          <ChatPanel
            session={activeSession}
            onUpdateSession={handleUpdateActiveSession}
          />
        )}

        {activeView === "documents" && (
          <div className="documents-view">
            <DocumentsPanel />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;