function Sidebar({ user, activeTab, onChangeTab, onLogout }) {
  return (
    <aside className="sidebar">
      <h2>Healthcare AI</h2>

      <div className="user-box">
        <strong>{user?.full_name || "User"}</strong>
        <span>{user?.email}</span>
      </div>

      <button
        className={activeTab === "chat" ? "active" : ""}
        onClick={() => onChangeTab("chat")}
      >
        Chat
      </button>

      <button
        className={activeTab === "documents" ? "active" : ""}
        onClick={() => onChangeTab("documents")}
      >
        Documents
      </button>

      <button
        className={activeTab === "history" ? "active" : ""}
        onClick={() => onChangeTab("history")}
      >
        History
      </button>

      <button className="logout" onClick={onLogout}>
        Logout
      </button>
    </aside>
  );
}

export default Sidebar;