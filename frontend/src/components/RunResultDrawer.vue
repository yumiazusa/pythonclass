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
            <button
              v-if="displayRunOwnerLabel"
              type="button"
              class="btn viewer-info"
              disabled
              :title="`当前运行结果：${displayRunOwnerLabel}`"
              aria-label="当前运行结果所属用户"
            >
              {{ displayRunOwnerLabel }}
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
            <div v-if="chartImageList.length" class="chart-list">
              <figure v-for="(src, idx) in chartImageList" :key="`${idx}-${src.slice(0, 24)}`" class="chart-wrap">
                <img :src="src" :alt="`运行生成图表 ${idx + 1}`" />
                <figcaption>图 {{ idx + 1 }}</figcaption>
              </figure>
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
  runOwnerLabel: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["close", "rerun", "save"]);
const displayRunOwnerLabel = computed(() => props.runOwnerLabel?.trim() || "");

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

function stripTaggedTableLines(value) {
  if (typeof value !== "string" || !value) {
    return "";
  }
  const markerList = ["__TABLE_JSON__=", "__TABLE_JSON__:", "__TABLE_DATA__=", "__TABLE_DATA__:"];
  const cleaned = value
    .split(/\r?\n/)
    .filter((line) => !markerList.some((marker) => line.includes(marker)))
    .join("\n")
    .trimEnd();
  return cleaned;
}

const stdoutText = computed(() => {
  const text = rawStdout.value;
  if (!text) {
    return "（空）";
  }
  const textWithoutTaggedRows = stripTaggedTableLines(text);
  if (!textWithoutTaggedRows) {
    return "（空）";
  }
  const extracted = extractLastJsonPayload(textWithoutTaggedRows);
  if (!extracted || !isTableLikeParsed(extracted.parsed)) {
    return textWithoutTaggedRows || "（空）";
  }
  const isTailPayload = extracted.end >= textWithoutTaggedRows.trimEnd().length;
  if (!isTailPayload) {
    return textWithoutTaggedRows || "（空）";
  }
  const cleaned = textWithoutTaggedRows.slice(0, extracted.start).trimEnd();
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

function normalizeImageSrc(raw) {
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
}

const chartImageList = computed(() => {
  const imageListRaw = props.result?.images_base64;
  if (Array.isArray(imageListRaw)) {
    const normalizedList = imageListRaw.map(normalizeImageSrc).filter(Boolean);
    if (normalizedList.length > 0) {
      return normalizedList;
    }
  }
  const singleRaw = props.result?.image || props.result?.image_url || props.result?.image_base64 || props.result?.plot_image || "";
  const singleSrc = normalizeImageSrc(singleRaw);
  return singleSrc ? [singleSrc] : [];
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
    document.body.classList.toggle("run-result-open", visible);
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.body.classList.remove("run-result-open");
  }
});
</script>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: var(--z-drawer);
}

.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: var(--overlay-soft);
}

.drawer-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: min(1080px, 100vw);
  height: 100dvh;
  background: var(--surface-1);
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border-soft);
  box-shadow: var(--shadow-elevated);
  overflow: hidden;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border-soft);
}

.drawer-header h3 {
  margin: 0;
  font-size: 20px;
}

.drawer-header p {
  margin: 6px 0 0;
  color: var(--text-subtle);
  font-size: 14px;
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
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.close {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn.save {
  background: var(--accent-teal-strong);
  color: var(--surface-1);
}

.btn.viewer-info {
  background: color-mix(in srgb, var(--surface-1) 68%, var(--brand-soft) 32%);
  border: 1px solid color-mix(in srgb, var(--brand-border) 68%, var(--border-soft) 32%);
  color: var(--brand-800);
  cursor: default;
  pointer-events: none;
  max-width: min(34vw, 300px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn.viewer-info:disabled {
  opacity: 1;
  cursor: default;
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
  background: color-mix(in srgb, var(--surface-3) 86%, var(--surface-2) 14%);
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.summary-card {
  border: 1px solid var(--brand-soft-2);
  background: var(--brand-soft);
  border-radius: 10px;
  padding: 10px 12px;
  display: grid;
  gap: 4px;
  min-height: 68px;
}

.summary-card.ok {
  border-color: var(--success-border);
  background: var(--success-soft);
}

.summary-card.warn {
  border-color: var(--warn-border);
  background: var(--warn-soft);
}

.summary-card.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
}

.summary-card.ok .summary-value {
  color: var(--success-strong);
}

.summary-card.warn .summary-value {
  color: var(--warn-strong);
}

.summary-card.error .summary-value {
  color: var(--danger-strong);
}

.summary-label {
  color: var(--text-subtle);
  font-size: 14px;
  line-height: 1.2;
}

.summary-value {
  color: var(--brand-800);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
  word-break: break-word;
}

.loading-panel {
  border: 1px solid var(--brand-border);
  background: var(--brand-soft);
  color: var(--brand-700);
  border-radius: 10px;
  padding: 10px 12px;
  font-weight: 600;
}

.content-card {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  background: var(--surface-1);
  padding: 12px;
}

.content-card h4 {
  margin: 0 0 8px;
  font-size: 15px;
}

.content-card pre {
  margin: 0;
  border-radius: 8px;
  background: var(--code-bg);
  color: var(--code-text);
  padding: 10px 12px;
  max-height: 240px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.5;
}

.empty-text {
  margin: 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.table-scroll {
  max-height: 320px;
  overflow: auto;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
}

.table-scroll table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.table-scroll th,
.table-scroll td {
  border-bottom: 1px solid var(--border-soft);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}

.table-scroll th {
  background: var(--surface-3);
  position: sticky;
  top: 0;
  z-index: 1;
}

.chart-wrap {
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  background: var(--surface-1);
  padding: 10px;
  text-align: center;
}

.chart-list {
  display: grid;
  gap: 10px;
}

.chart-wrap img {
  max-width: 100%;
  height: auto;
}

.chart-wrap figcaption {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-subtle);
}

.error-card {
  border-color: var(--danger-border);
  background: var(--danger-soft);
}

.error-card pre {
  background: var(--danger-strong);
  color: var(--danger-soft);
}

@media (max-width: 900px) {
  .drawer-panel {
    width: 100vw;
  }

  .drawer-header {
    padding: 14px;
  }

  .header-actions {
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-card pre,
  .table-scroll {
    max-height: none;
    overflow: visible;
  }
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .drawer-header {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .header-actions {
    justify-content: stretch;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  }

  .btn {
    width: 100%;
    padding: 9px 8px;
    font-size: 14px;
  }

  .btn.viewer-info {
    max-width: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .btn,
  .drawer-backdrop {
    transition: none !important;
    animation: none !important;
  }
}

:global(body.run-result-open) {
  overflow: hidden;
}
</style>
