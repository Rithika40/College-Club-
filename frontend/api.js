const API = "/api";
const IDLE_MS = 15 * 60 * 1000;

function token() {
  return sessionStorage.getItem("ccms_token");
}

function setSession(data) {
  sessionStorage.setItem("ccms_token", data.token);
  sessionStorage.setItem("ccms_user", JSON.stringify(data.user));
  sessionStorage.setItem("ccms_active", String(Date.now()));
}

function clearSession() {
  sessionStorage.removeItem("ccms_token");
  sessionStorage.removeItem("ccms_user");
  sessionStorage.removeItem("ccms_active");
}

function currentUser() {
  try {
    return JSON.parse(sessionStorage.getItem("ccms_user") || "null");
  } catch {
    return null;
  }
}

function touchActivity() {
  if (token()) sessionStorage.setItem("ccms_active", String(Date.now()));
}

function idleExpired() {
  const last = Number(sessionStorage.getItem("ccms_active") || 0);
  return Date.now() - last > IDLE_MS;
}

async function api(path, options = {}) {
  if (token() && idleExpired()) {
    clearSession();
    throw new Error("Session expired after 15 minutes of inactivity. Please log in again.");
  }
  touchActivity();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token()) headers.Authorization = `Bearer ${token()}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  let body = null;
  const text = await res.text();
  if (text) {
    try { body = JSON.parse(text); } catch { body = { detail: text }; }
  }
  if (!res.ok) {
    const detail = body && body.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
      : (detail || res.statusText || "Request failed");
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return body;
}

window.CCMS = { API, token, setSession, clearSession, currentUser, api, idleExpired, touchActivity };
