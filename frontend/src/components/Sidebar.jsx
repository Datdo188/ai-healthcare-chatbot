function formatGroupLabel(dateString) {
  const date = new Date(dateString);
  const today = new Date();

  const startOfToday = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate()
  );

  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);

  if (date >= startOfToday) {
    return "Today";
  }

  if (date >= startOfYesterday) {
    return "Yesterday";
  }

  return "Older";
}

function groupSessions(sessions) {
  return sessions.reduce((groups, session) => {
    const label = formatGroupLabel(session.updatedAt || session.createdAt);

    if (!groups[label]) {
      groups[label] = [];
    }

    groups[label].push(session);

    return groups;
  }, {});
}

function Sidebar({
  user,
  sessions,
  activeSessionId,
  activeView,
  loadingUser,
  onNewChat,
  onSelectSession,
  onOpenDocuments,
  onClearHistory,
  onLogout,
}) {
  const groupedSessions = groupSessions(sessions);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <div className="brand-title">AI Healthcare</div>
            <div className="brand-subtitle">Chatbot</div>
          </div>
        </div>
      </div>

      <button className="new-chat-button" onClick={onNewChat}>
        <span>＋</span>
        New Chat
      </button>

      <button
        className={`sidebar-action ${activeView === "documents" ? "active" : ""}`}
        onClick={onOpenDocuments}
      >
        📄 Documents
      </button>

      <div className="history-header">
        <span>Chat history</span>
        <button onClick={onClearHistory}>Clear</button>
      </div>

      <div className="chat-history-list">
        {["Today", "Yesterday", "Older"].map((groupName) => {
          const group = groupedSessions[groupName];

          if (!group || group.length === 0) {
            return null;
          }

          return (
            <div className="history-group" key={groupName}>
              <div className="history-group-title">{groupName}</div>

              {group.map((session) => (
                <button
                  key={session.id}
                  className={`history-item ${
                    activeView === "chat" && session.id === activeSessionId
                      ? "active"
                      : ""
                  }`}
                  onClick={() => onSelectSession(session.id)}
                  title={session.title}
                >
                  <span className="history-icon">💬</span>
                  <span className="history-title">{session.title}</span>
                </button>
              ))}
            </div>
          );
        })}
      </div>

      <div className="sidebar-footer">
        <div className="user-avatar">
          {(user?.full_name || user?.email || "U").charAt(0).toUpperCase()}
        </div>

        <div className="user-info">
          <div className="user-name">
            {loadingUser ? "Loading..." : user?.full_name || "User"}
          </div>
          <div className="user-email">{user?.email || ""}</div>
        </div>

        <button className="logout-button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;