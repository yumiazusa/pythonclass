function hasExplicitTimezone(value) {
  return /(?:Z|[+-]\d{2}:\d{2})$/i.test(value);
}

export function parseApiDateTime(value) {
  if (!value) {
    return null;
  }
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  if (typeof value !== "string") {
    return null;
  }
  const text = value.trim();
  if (!text) {
    return null;
  }
  const normalizedBase = text.includes(" ") && !text.includes("T") ? text.replace(" ", "T") : text;
  const normalized = hasExplicitTimezone(normalizedBase) ? normalizedBase : `${normalizedBase}Z`;
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatApiDateTime(value, locale = "zh-CN") {
  const date = parseApiDateTime(value);
  if (!date) {
    return "-";
  }
  return date.toLocaleString(locale, { hour12: false });
}

export function toDateTimeLocalInput(value) {
  const date = parseApiDateTime(value);
  if (!date) {
    return "";
  }
  const pad = (num) => `${num}`.padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function toUtcIsoStringFromLocalInput(value) {
  if (!value) {
    return null;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return date.toISOString();
}
