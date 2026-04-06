import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
const tokenKeys = ["token", "teacher_token", "student_token"];

function joinPath(basePath, requestPath) {
  const normalizedBase = (basePath || "").replace(/\/+$/, "");
  const normalizedPath = (requestPath || "").replace(/^\/+/, "");
  if (!normalizedBase) {
    return normalizedPath ? `/${normalizedPath}` : "/";
  }
  if (!normalizedPath) {
    return normalizedBase.startsWith("/") ? normalizedBase : `/${normalizedBase}`;
  }
  const withLeadingSlash = normalizedBase.startsWith("/") ? normalizedBase : `/${normalizedBase}`;
  return `${withLeadingSlash}/${normalizedPath}`;
}

function formatRequestUrl(config) {
  const requestPath = config?.url || "";
  const baseUrl = config?.baseURL || apiBaseUrl || "";
  if (!requestPath && !baseUrl) {
    return "";
  }

  const hasAbsoluteProtocol = (value) => /^https?:\/\//i.test(value || "");

  if (hasAbsoluteProtocol(requestPath)) {
    return requestPath;
  }

  if (hasAbsoluteProtocol(baseUrl)) {
    const normalizedBase = baseUrl.replace(/\/+$/, "");
    const normalizedPath = requestPath ? `/${requestPath.replace(/^\/+/, "")}` : "";
    return `${normalizedBase}${normalizedPath}`;
  }

  if (typeof window === "undefined") {
    return joinPath(baseUrl, requestPath);
  }

  const mergedPath = joinPath(baseUrl, requestPath);
  return `${window.location.origin}${mergedPath}`;
}

function isLoopbackHost(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
}

function buildNetworkErrorHint(config) {
  const requestUrl = formatRequestUrl(config);
  if (!requestUrl) {
    return "";
  }
  try {
    const parsed = new URL(requestUrl);
    if (typeof window !== "undefined" && isLoopbackHost(parsed.hostname) && !isLoopbackHost(window.location.hostname)) {
      return `（无法访问本机地址 ${parsed.hostname}，请改为服务器域名/IP 或反向代理 /api）`;
    }
  } catch {
    return "";
  }
  return `（${requestUrl}）`;
}

function getTokenFromStorage() {
  for (const key of tokenKeys) {
    const token = localStorage.getItem(key);
    if (token) {
      if (key !== "token") {
        localStorage.setItem("token", token);
      }
      return token;
    }
  }
  return "";
}

function clearAuthStorage() {
  localStorage.removeItem("token");
  localStorage.removeItem("teacher_token");
  localStorage.removeItem("student_token");
  localStorage.removeItem("current_user");
  localStorage.removeItem("role");
}

const request = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
});

request.interceptors.request.use(
  (config) => {
    const token = getTokenFromStorage();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

request.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const isNetworkError = !error?.response && (error?.code === "ERR_NETWORK" || error?.message === "Network Error");
    if (status === 401) {
      clearAuthStorage();
      const isLoginRoute = window.location.pathname === "/login";
      if (!isLoginRoute) {
        const redirectTarget = `${window.location.pathname}${window.location.search}`;
        window.location.href = `/login?redirect=${encodeURIComponent(redirectTarget)}`;
      }
    }
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      (isNetworkError ? `Network Error${buildNetworkErrorHint(error?.config)}` : "") ||
      error.message ||
      "请求失败";
    return Promise.reject(new Error(message));
  },
);

export default request;
