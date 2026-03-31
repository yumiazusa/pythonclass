import request from "./request";

const TOKEN_STORAGE_KEY = "token";
const LEGACY_TOKEN_KEYS = ["teacher_token", "student_token"];
const USER_STORAGE_KEY = "current_user";
const ROLE_STORAGE_KEY = "role";

let currentUserCache = null;
let currentUserPromise = null;

function parseStoredUser(rawValue) {
  if (!rawValue) {
    return null;
  }
  try {
    return JSON.parse(rawValue);
  } catch (error) {
    return null;
  }
}

function setCurrentUser(user) {
  if (!user) {
    currentUserCache = null;
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(ROLE_STORAGE_KEY);
    return;
  }
  currentUserCache = user;
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  localStorage.setItem(ROLE_STORAGE_KEY, user.role || "");
}

export function setStoredCurrentUser(user) {
  setCurrentUser(user);
}

function migrateLegacyTokenIfNeeded() {
  const existingToken = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (existingToken) {
    return existingToken;
  }
  for (const key of LEGACY_TOKEN_KEYS) {
    const legacyToken = localStorage.getItem(key);
    if (legacyToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, legacyToken);
      return legacyToken;
    }
  }
  return "";
}

export function getAccessToken() {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    return token;
  }
  return migrateLegacyTokenIfNeeded();
}

export function getStoredCurrentUser() {
  if (currentUserCache) {
    return currentUserCache;
  }
  const stored = parseStoredUser(localStorage.getItem(USER_STORAGE_KEY));
  if (stored) {
    currentUserCache = stored;
    return stored;
  }
  return null;
}

export function clearCurrentUserCache() {
  currentUserCache = null;
  currentUserPromise = null;
  localStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem(ROLE_STORAGE_KEY);
}

export function clearAuthStorage() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  for (const key of LEGACY_TOKEN_KEYS) {
    localStorage.removeItem(key);
  }
  clearCurrentUserCache();
}

export async function login(payload) {
  const { data } = await request.post("/auth/login", payload);
  const accessToken = data?.access_token;
  if (!accessToken) {
    throw new Error("登录失败：响应缺少 access_token");
  }
  localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
  for (const key of LEGACY_TOKEN_KEYS) {
    localStorage.removeItem(key);
  }
  setCurrentUser(data?.user || null);
  return data;
}

export async function changePassword(payload) {
  const { data } = await request.post("/auth/change-password", payload);
  if (data?.user) {
    setCurrentUser(data.user);
  }
  return data;
}

export async function updateProfile(payload) {
  const { data } = await request.post("/auth/update-profile", payload);
  if (data?.user) {
    setCurrentUser(data.user);
  }
  return data;
}

export async function getCurrentUser(options = {}) {
  const token = getAccessToken();
  if (!token) {
    clearAuthStorage();
    throw new Error("未登录");
  }

  const forceRefresh = Boolean(options.forceRefresh);
  if (!forceRefresh) {
    const cachedUser = getStoredCurrentUser();
    if (cachedUser) {
      return cachedUser;
    }
    if (currentUserPromise) {
      return currentUserPromise;
    }
  }

  currentUserPromise = request
    .get("/auth/me")
    .then(({ data }) => {
      setCurrentUser(data);
      return data;
    })
    .catch((error) => {
      const status = error?.response?.status;
      if (status === 401 || status === 403) {
        clearAuthStorage();
      }
      throw error;
    })
    .finally(() => {
      currentUserPromise = null;
    });

  return currentUserPromise;
}

export async function restoreSession() {
  const token = getAccessToken();
  if (!token) {
    clearAuthStorage();
    return null;
  }
  try {
    return await getCurrentUser({ forceRefresh: true });
  } catch (error) {
    clearAuthStorage();
    return null;
  }
}

export function logout() {
  clearAuthStorage();
}

export async function getCurrentUserProfile(options = {}) {
  return getCurrentUser(options);
}
