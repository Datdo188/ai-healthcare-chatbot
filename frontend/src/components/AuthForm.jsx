import { useState } from "react";
import { loginUser, registerUser, setToken } from "../api/client";

function AuthForm({ onAuthenticated }) {
  const [mode, setMode] = useState("login");

  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("123456");
  const [fullName, setFullName] = useState("Test User");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleRegister() {
    setLoading(true);
    setMessage("");

    try {
      await registerUser({
        email,
        password,
        full_name: fullName,
      });

      setMessage("Register successful. You can login now.");
      setMode("login");
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
      const data = await loginUser({
        email,
        password,
      });

      setToken(data.access_token);
      onAuthenticated(data.user);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="auth-card">
        <h1>AI Healthcare Assistant</h1>
        <p className="muted">
          Login or register to use your healthcare chatbot.
        </p>

        <div className="tabs">
          <button
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>

          <button
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        {mode === "register" && (
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

        {mode === "login" ? (
          <button onClick={handleLogin} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        ) : (
          <button onClick={handleRegister} disabled={loading}>
            {loading ? "Registering..." : "Register"}
          </button>
        )}

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}

export default AuthForm;