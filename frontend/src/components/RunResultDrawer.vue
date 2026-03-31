<template>
  <Teleport to="body">
    <div v-if="visible" class="drawer-root">
      <div class="drawer-backdrop" @click="emit('close')"></div>
      <aside class="drawer-panel" role="dialog" aria-modal="true" aria-label="运行结果">
        <header class="drawer-header">
          <div>
            <h3>运行结果</h3>
            <p>支持终端输出、表格数据、图表与错误信息查看。</p>
          </div>
          <div class="header-actions">
            <button class="btn rerun" :disabled="rerunDisabled || loading" @click="emit('rerun')">
              {{ loading ? "运行中..." : "重新运行" }}
            </button>
            <button v-if="saveVisible" class="btn save" :disabled="saveDisabled || loading || saveLoading" @click="emit('save')">
              {{ saveLoading ? "保存中..." : "保存草稿" }}
            </button>
            <button class="btn close" @click="emit('close')">关闭</button>
          </div>
        </header>

        <section class="drawer-body">
          <div class="summary-grid">
            <div :class="['summary-card', statusToneClass]">
              <div class="summary-label">状态</div>
              <div class="summary-value">{{ statusText }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">耗时</div>
              <div class="summary-value">{{ executionTimeText }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">超时</div>
              <div class="summary-value">{{ timedOutText }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">拦截</div>
              <div class="summary-value">{{ blockedText }}</div>
            </div>
          </div>

          <div v-if="loading" class="loading-panel">代码正在运行，请稍候...</div>

          <article class="content-card">
            <h4>终端输出（stdout）</h4>
            <pre>{{ stdoutText }}</pre>
          </article>

          <article class="content-card">
            <h4>表格数据（DataFrame）</h4>
            <div v-if="hasTableData" class="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th v-for="column in tableColumns" :key="column">{{ column }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in tableRows" :key="rowIndex">
                    <td v-for="column in tableColumns" :key="`${rowIndex}-${column}`">
                      {{ stringifyCell(row[column]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="empty-text">当前运行结果未返回可解析的表格数据。</p>
          </article>

          <article class="content-card">
            <h4>图表（image）</h4>
            <div v-if="chartImageSrc" class="chart-wrap">
              <img :src="chartImageSrc" alt="运行生成图表" />
            </div>
            <p v-else class="empty-text">当前运行结果未返回图表图片。</p>
          </article>

          <article class="content-card error-card">
            <h4>错误信息（stderr）</h4>
            <pre>{{ errorText }}</pre>
          </article>
        </section>
      </aside>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, watch } from "vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  result: {
    type: Object,
    default: null,
  },
  message: {
    type: String,
    default: "",
  },
  rerunDisabled: {
    type: Boolean,
    default: false,
  },
  saveVisible: {
    type: Boolean,
    default: false,
  },
  saveDisabled: {
    type: Boolean,
    default: false,
  },
  saveLoading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "rerun", "save"]);

const statusTextMap = {
  not_run: "未运行",
  completed: "运行完成",
  runtime_error: "运行报错",
  blocked: "已拦截",
  timed_out: "执行超时",
  internal_error: "内部错误",
};

const statusText = computed(() => statusTextMap[props.result?.status || "not_run"]);
const executionTimeText = computed(() =>
  typeof props.result?.execution_time_ms === "number" ? `${props.result.execution_time_ms} ms` : "-",
);
const timedOutText = computed(() => (typeof props.result?.timed_out === "boolean" ? (props.result.timed_out ? "是" : "否") : "-"));
const blockedText = computed(() => (typeof props.result?.blocked === "boolean" ? (props.result.blocked ? "是" : "否") : "-"));
const statusToneClass = computed(() => {
  if (props.result?.status === "completed") {
    return "ok";
  }
  if (props.result?.status === "runtime_error" || props.result?.status === "internal_error") {
    return "error";
  }
  if (props.result?.status === "blocked" || props.result?.status === "timed_out") {
    return "warn";
  }
  return "normal";
});

const rawStdout = computed(() => props.result?.stdout || "");
const stderrText = computed(() => props.result?.stderr || "（空）");

function tryParseJson(candidate) {
  try {
    return JSON.parse(candidate);
  } catch (error) {
    return null;
  }
}

function extractTaggedTablePayload(value) {
  if (typeof value !== "string") {
    return null;
  }
  const markerList = ["__TABLE_JSON__=", "__TABLE_JSON__:", "__TABLE_DATA__=", "__TABLE_DATA__:"];
  const lines = value.split(/\r?\n/);
  let offset = 0;
  const lineOffsets = lines.map((line) => {
    const start = offset;
    offset += line.length + 1;
    return start;
  });

  for (let i = lines.length - 1; i >= 0; i -= 1) {
    const line = lines[i];
    for (const marker of markerList) {
      const markerIndex = line.indexOf(marker);
      if (markerIndex < 0) {
        continue;
      }
      const jsonPart = line.slice(markerIndex + marker.length).trim();
      if (!jsonPart) {
        continue;
      }
      const parsed = tryParseJson(jsonPart);
      if (parsed === null) {
        continue;
      }
      const lineStart = lineOffsets[i];
      const absoluteStart = lineStart + markerIndex;
      const absoluteEnd = lineStart + line.length;
      return {
        parsed,
        start: absoluteStart,
        end: absoluteEnd,
        payload: jsonPart,
      };
    }
  }
  return null;
}

function extractLastJsonPayload(value) {
  if (typeof value !== "string") {
    return null;
  }
  const text = value;
  const trimmed = text.trim();
  if (!trimmed) {
    return null;
  }

  const direct = tryParseJson(trimmed);
  if (direct !== null) {
    const start = text.indexOf(trimmed);
    return {
      parsed: direct,
      start,
      end: start + trimmed.length,
      payload: trimmed,
    };
  }

  const lines = trimmed.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i -= 1) {
    const line = lines[i];
    if (!line.startsWith("{") && !line.startsWith("[")) {
      continue;
    }
    const parsedLine = tryParseJson(line);
    if (parsedLine !== null) {
      const start = text.lastIndexOf(line);
      if (start >= 0) {
        return {
          parsed: parsedLine,
          start,
          end: start + line.length,
          payload: line,
        };
      }
    }
  }

  const findLastJsonBlock = (source, openChar) => {
    const closeChar = openChar === "[" ? "]" : "}";
    for (let start = source.length - 1; start >= 0; start -= 1) {
      if (source[start] !== openChar) {
        continue;
      }
      let depth = 0;
      let inString = false;
      let escaped = false;
      for (let index = start; index < source.length; index += 1) {
        const char = source[index];
        if (inString) {
          if (escaped) {
            escaped = false;
            continue;
          }
          if (char === "\\") {
            escaped = true;
            continue;
          }
          if (char === "\"") {
            inString = false;
          }
          continue;
        }
        if (char === "\"") {
          inString = true;
          continue;
        }
        if (char === openChar) {
          depth += 1;
          continue;
        }
        if (char === closeChar) {
          depth -= 1;
          if (depth === 0) {
            const candidate = source.slice(start, index + 1).trim();
            const parsed = tryParseJson(candidate);
            if (parsed !== null) {
              const candidateStart = source.indexOf(candidate, start);
              if (candidateStart >= 0) {
                return {
                  parsed,
                  start: candidateStart,
                  end: candidateStart + candidate.length,
                  payload: candidate,
                };
              }
            }
            break;
          }
        }
      }
    }
    return null;
  };

  return findLastJsonBlock(text, "[") || findLastJsonBlock(text, "{");
}

function parseMaybeJson(value) {
  if (typeof value !== "string") {
    return null;
  }
  const text = value.trim();
  if (!text) {
    return null;
  }
  const tagged = extractTaggedTablePayload(value);
  if (tagged) {
    return tagged.parsed;
  }
  const extracted = extractLastJsonPayload(text);
  return extracted ? extracted.parsed : null;
}

function normalizeTableRows(raw) {
  if (Array.isArray(raw)) {
    return raw.filter((item) => item && typeof item === "object");
  }
  if (raw && typeof raw === "object") {
    return [raw];
  }
  const parsed = parseMaybeJson(raw);
  if (Array.isArray(parsed)) {
    return parsed.filter((item) => item && typeof item === "object");
  }
  if (parsed && typeof parsed === "object") {
    return [parsed];
  }
  return [];
}

function isTableLikeParsed(parsed) {
  if (Array.isArray(parsed)) {
    return parsed.some((item) => item && typeof item === "object");
  }
  return Boolean(parsed && typeof parsed === "object");
}

const stdoutText = computed(() => {
  const text = rawStdout.value;
  if (!text) {
    return "（空）";
  }
  const tagged = extractTaggedTablePayload(text);
  if (tagged && isTableLikeParsed(tagged.parsed)) {
    const before = text.slice(0, tagged.start).trimEnd();
    const after = text.slice(tagged.end).trim();
    const merged = [before, after].filter(Boolean).join("\n");
    return merged || "（空）";
  }
  const extracted = extractLastJsonPayload(text);
  if (!extracted || !isTableLikeParsed(extracted.parsed)) {
    return text || "（空）";
  }
  const isTailPayload = extracted.end >= text.trimEnd().length;
  if (!isTailPayload) {
    return text || "（空）";
  }
  const cleaned = text.slice(0, extracted.start).trimEnd();
  return cleaned || "（空）";
});

const tableRows = computed(() => {
  const directSource = props.result?.table_data ?? props.result?.dataframe ?? props.result?.df ?? null;
  const directRows = normalizeTableRows(directSource);
  if (directRows.length > 0) {
    return directRows;
  }
  return normalizeTableRows(props.result?.stdout);
});

const tableColumns = computed(() => {
  const columns = new Set();
  tableRows.value.forEach((row) => {
    Object.keys(row).forEach((key) => columns.add(key));
  });
  return Array.from(columns);
});

const hasTableData = computed(() => tableRows.value.length > 0 && tableColumns.value.length > 0);

const chartImageSrc = computed(() => {
  const raw = props.result?.image || props.result?.image_url || props.result?.image_base64 || props.result?.plot_image || "";
  if (!raw || typeof raw !== "string") {
    return "";
  }
  if (raw.startsWith("data:image")) {
    return raw;
  }
  if (raw.startsWith("http://") || raw.startsWith("https://") || raw.startsWith("/")) {
    return raw;
  }
  return `data:image/png;base64,${raw}`;
});

const errorText = computed(() => {
  const parts = [];
  if (props.result?.block_reason) {
    parts.push(`拦截原因：${props.result.block_reason}`);
  }
  if (stderrText.value && stderrText.value !== "（空）") {
    parts.push(stderrText.value);
  }
  const shouldShowMessage =
    props.message &&
    props.message !== "运行完成" &&
    (parts.length === 0 ||
      props.message.includes("失败") ||
      props.message.includes("错误") ||
      props.message.includes("不可") ||
      props.message.includes("缺少"));
  if (shouldShowMessage) {
    parts.push(`提示：${props.message}`);
  }
  return parts.join("\n\n") || "（空）";
});

function stringifyCell(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

watch(
  () => props.visible,
  (visible) => {
    if (typeof document === "undefined") {
      return;
    }
    document.body.style.overflow = visible ? "hidden" : "";
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.body.style.overflow = "";
  }
});
</script>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: 999;
}

.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
}

.drawer-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: min(1080px, 100vw);
  height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: -16px 0 32px rgba(15, 23, 42, 0.2);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid #e5e8f0;
}

.drawer-header h3 {
  margin: 0;
  font-size: 20px;
}

.drawer-header p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn.rerun {
  background: #2563eb;
  color: #fff;
}

.btn.close {
  background: #e5e7eb;
  color: #111827;
}

.btn.save {
  background: #059669;
  color: #fff;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px;
  display: grid;
  gap: 12px;
  background: #f8fafc;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.summary-card {
  border: 1px solid #dbeafe;
  background: #eff6ff;
  border-radius: 10px;
  padding: 10px 12px;
  display: grid;
  gap: 4px;
  min-height: 68px;
}

.summary-card.ok {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.summary-card.warn {
  border-color: #fed7aa;
  background: #fff7ed;
}

.summary-card.error {
  border-color: #fecaca;
  background: #fef2f2;
}

.summary-card.ok .summary-value {
  color: #166534;
}

.summary-card.warn .summary-value {
  color: #9a3412;
}

.summary-card.error .summary-value {
  color: #b91c1c;
}

.summary-label {
  color: #64748b;
  font-size: 12px;
  line-height: 1;
}

.summary-value {
  color: #1e3a8a;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
  word-break: break-word;
}

.loading-panel {
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 10px;
  padding: 10px 12px;
  font-weight: 600;
}

.content-card {
  border: 1px solid #e5e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 12px;
}

.content-card h4 {
  margin: 0 0 8px;
  font-size: 15px;
}

.content-card pre {
  margin: 0;
  border-radius: 8px;
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px 12px;
  max-height: 240px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.5;
}

.empty-text {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.table-scroll {
  max-height: 320px;
  overflow: auto;
  border: 1px solid #e5e8f0;
  border-radius: 8px;
}

.table-scroll table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table-scroll th,
.table-scroll td {
  border-bottom: 1px solid #e5e8f0;
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}

.table-scroll th {
  background: #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 1;
}

.chart-wrap {
  border: 1px solid #e5e8f0;
  border-radius: 8px;
  background: #fff;
  padding: 10px;
  text-align: center;
}

.chart-wrap img {
  max-width: 100%;
  height: auto;
}

.error-card {
  border-color: #fecaca;
  background: #fff7f7;
}

.error-card pre {
  background: #7f1d1d;
  color: #fee2e2;
}

@media (max-width: 900px) {
  .drawer-panel {
    width: 100vw;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
