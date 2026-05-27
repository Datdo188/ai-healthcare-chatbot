const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const TOKEN_KEY = "access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function getAuthHeaders() {
  const token = getToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function apiRequest(path, options = {}) {
  const headers = {
    ...(options.headers || {}),
  };

  if (options.auth !== false) {
    Object.assign(headers, getAuthHeaders());
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail || "Request failed";
    throw new Error(detail);
  }

  return data;
}

export async function registerUser(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    auth: false,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload) {
  return apiRequest("/auth/login", {
    method: "POST",
    auth: false,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser() {
  return apiRequest("/auth/me");
}

export async function sendChatMessage(question) {
  return apiRequest("/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
    }),
  });
}

export async function getChatHistory(limit = 20) {
  return apiRequest(`/chat/history?limit=${limit}`);
}

export async function deleteAllChatHistory() {
  return apiRequest("/chat/history", {
    method: "DELETE",
  });
}

export async function deleteChatMessage(messageId) {
  return apiRequest(`/chat/history/${messageId}`, {
    method: "DELETE",
  });
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function getDocuments() {
  return apiRequest("/documents/");
}

export async function previewDocument(filename) {
  return apiRequest(`/documents/${filename}/preview`);
}

export async function getDocumentChunks(filename) {
  return apiRequest(`/documents/${filename}/chunks`);
}

export async function indexDocument(filename) {
  return apiRequest(`/documents/${filename}/index`, {
    method: "POST",
  });
}

export async function deleteDocument(filename) {
  return apiRequest(`/documents/${filename}`, {
    method: "DELETE",
  });
}

export async function searchDocuments(query, topK = 3) {
  const params = new URLSearchParams({
    query,
    top_k: String(topK),
  });

  return apiRequest(`/documents/search/?${params.toString()}`);
}