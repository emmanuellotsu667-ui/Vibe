/**
 * api.js — Client API global pour IFRI MentorLink
 * Expose window.API avec toutes les méthodes REST + gestion JWT.
 */

const API_BASE = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:5000/api"
  : "https://ifri-mentorlink-api.onrender.com/api";

const API = (() => {
  // ─── Auth helpers ───────────────────────────────────────────
  function getToken() {
    return localStorage.getItem("ml_token");
  }

  function setToken(token) {
    localStorage.setItem("ml_token", token);
  }

  function clearToken() {
    localStorage.removeItem("ml_token");
    localStorage.removeItem("ml_user");
  }

  function setUser(user) {
    localStorage.setItem("ml_user", JSON.stringify(user));
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem("ml_user"));
    } catch {
      return null;
    }
  }

  function isLoggedIn() {
    return !!getToken();
  }

  // ─── HTTP helpers ───────────────────────────────────────────
  async function request(method, path, body = null, auth = true) {
    const headers = { "Content-Type": "application/json" };
    if (auth) {
      const token = getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, options);

    if (res.status === 401) {
      clearToken();
      const base = window.location.hostname === "localhost" ? "/Frontend/pages" : "";
      window.location.href = `${base}/signin.html`;
      return;
    }

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw Object.assign(new Error(data.error || "Erreur API"), { status: res.status, data });
    return data;
  }

  const get    = (path, auth = true) => request("GET", path, null, auth);
  const post   = (path, body, auth = true) => request("POST", path, body, auth);
  const put    = (path, body, auth = true) => request("PUT", path, body, auth);
  const del    = (path, auth = true) => request("DELETE", path, null, auth);

  // ─── Auth ───────────────────────────────────────────────────
  async function register(nom, prenom, email, password, telephone = "") {
    const data = await post("/auth/register", { nom, prenom, email, password, telephone }, false);
    setToken(data.token);
    setUser(data.user);
    return data;
  }

  async function login(identifier, password) {
    const data = await post("/auth/login", { identifier, password }, false);
    setToken(data.token);
    setUser(data.user);
    return data;
  }

  function logout() {
    clearToken();
    const base = window.location.hostname === "localhost" ? "/Frontend/pages" : "";
    window.location.href = `${base}/signin.html`;
  }

  async function me() {
    return get("/auth/me");
  }

  // ─── Profil ─────────────────────────────────────────────────
  const profile = {
    get: ()             => get("/profile/"),
    getById: (id)       => get(`/profile/${id}`),
    update: (data)      => put("/profile/", data),
    addCompetence: (d)  => post("/profile/competences", d),
    updateCompetence: (id, d) => put(`/profile/competences/${id}`, d),
    deleteCompetence: (id)    => del(`/profile/competences/${id}`),
    addLacune: (d)       => post("/profile/lacunes", d),
    deleteLacune: (id)   => del(`/profile/lacunes/${id}`),
    addDispo: (d)        => post("/profile/disponibilites", d),
    deleteDispo: (id)    => del(`/profile/disponibilites/${id}`),
  };

  // ─── Offres & Demandes ──────────────────────────────────────
  const offers = {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return get(`/offers${qs ? "?" + qs : ""}`);
    },
    create: (d)      => post("/offers", d),
    get: (id)        => get(`/offers/${id}`),
    update: (id, d)  => put(`/offers/${id}`, d),
    delete: (id)     => del(`/offers/${id}`),
  };

  const demands = {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return get(`/demands${qs ? "?" + qs : ""}`);
    },
    create: (d)      => post("/demands", d),
    get: (id)        => get(`/demands/${id}`),
    update: (id, d)  => put(`/demands/${id}`, d),
    delete: (id)     => del(`/demands/${id}`),
  };

  // ─── Matching ───────────────────────────────────────────────
  const matching = {
    suggest: ()            => get("/matching/suggest"),
    run: (demand_id)       => post("/matching/run", { demand_id }),
    updateStatus: (id, s)  => put(`/matching/${id}/status`, { status: s }),
  };

  // ─── Messages ───────────────────────────────────────────────
  const messages = {
    conversations: ()          => get("/messages/conversations"),
    createConv: (user_id)      => post("/messages/conversations", { user_id }),
    getConv: (id)              => get(`/messages/conversations/${id}`),
    send: (conv_id, content)   => post(`/messages/conversations/${conv_id}/send`, { content }),
  };

  // ─── Notifications ──────────────────────────────────────────
  const notifications = {
    list: ()      => get("/notifications/"),
    readAll: ()   => put("/notifications/read-all"),
    read: (id)    => put(`/notifications/${id}/read`),
  };

  // ─── Exposition publique ────────────────────────────────────
  return {
    getToken, setToken, clearToken, getUser, setUser, isLoggedIn,
    register, login, logout, me,
    profile, offers, demands, matching, messages, notifications,
  };
})();

window.API = API;
