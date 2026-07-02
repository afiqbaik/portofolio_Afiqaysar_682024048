const API_BASE = '/api';

function getAuthToken() {
  return sessionStorage.getItem('token');
}

function buildHeaders(includeAuth = true) {
  const headers = { 'Content-Type': 'application/json' };
  if (includeAuth) {
    const token = getAuthToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: buildHeaders(options.auth !== false),
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.message || 'Request gagal');
  }
  return data;
}

async function login(username, password) {
  return requestJson(`${API_BASE}/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    auth: false,
  });
}

async function logout() {
  return requestJson(`${API_BASE}/logout`, { method: 'POST' });
}

async function checkAuth() {
  return requestJson(`${API_BASE}/auth/check`);
}

async function loadDashboardStats() {
  return requestJson(`${API_BASE}/dashboard/stats`);
}

async function loadRecentActivity() {
  return requestJson(`${API_BASE}/dashboard/recent`);
}

async function loadProfiles() {
  return requestJson(`${API_BASE}/profiles`);
}

async function saveProfile(payload) {
  return requestJson(`${API_BASE}/profiles`, { method: 'POST', body: JSON.stringify(payload) });
}

async function loadExperiences() {
  return requestJson(`${API_BASE}/experiences`);
}

async function saveExperience(payload) {
  return requestJson(`${API_BASE}/experiences`, { method: 'POST', body: JSON.stringify(payload) });
}

async function updateExperience(id, payload) {
  return requestJson(`${API_BASE}/experiences/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

async function deleteExperience(id) {
  return requestJson(`${API_BASE}/experiences/${id}`, { method: 'DELETE' });
}

async function loadProjects() {
  return requestJson(`${API_BASE}/projects`);
}

async function saveProject(payload) {
  return requestJson(`${API_BASE}/projects`, { method: 'POST', body: JSON.stringify(payload) });
}

async function updateProject(id, payload) {
  return requestJson(`${API_BASE}/projects/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

async function deleteProject(id) {
  return requestJson(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
}

async function uploadImage(file) {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append('file', file);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`${API_BASE}/upload/image`, {
    method: 'POST',
    body: formData,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || 'Upload failed');
  }
  return data;
}

async function loadSkills() {
  return requestJson(`${API_BASE}/skills`);
}

async function saveSkill(payload) {
  return requestJson(`${API_BASE}/skills`, { method: 'POST', body: JSON.stringify(payload) });
}

async function updateSkill(id, payload) {
  return requestJson(`${API_BASE}/skills/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

async function deleteSkill(id) {
  return requestJson(`${API_BASE}/skills/${id}`, { method: 'DELETE' });
}
