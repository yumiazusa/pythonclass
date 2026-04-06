<template>
  <section class="editor-page">
    <div class="panel toolbar-panel">
      <div class="title-wrap">
        <h2>{{ experimentTitle }}</h2>
        <p>{{ experimentDescription }}</p>
        <p v-if="isAdminViewer" class="admin-mode-tip">管理员测试模式：可运行与查看，不支持保存草稿和正式提交。</p>
      </div>
      <div class="actions">
        <button class="btn gray" @click="goExperiments">返回实验列表</button>
        <button class="btn light" :disabled="!hasValidExperimentId" @click="goDocs">查看实验说明</button>
        <button v-if="canUseSubmissionFlow" class="btn light" :disabled="!hasValidExperimentId" @click="toggleHistoryPanel">历史记录</button>
        <button v-if="hasEditorAccess" class="btn run" :disabled="runActionDisabled" @click="handleRunAction">
          {{ runActionText }}
        </button>
        <button v-if="canUseSubmissionFlow" class="btn save" :disabled="isBusy || !hasValidExperimentId || !canSaveDraft" @click="handleSave">
          {{ isSaving ? "保存中..." : "保存草稿" }}
        </button>
        <button
          v-if="canUseSubmissionFlow"
          class="btn submit"
          :disabled="isBusy || !hasValidExperimentId || !canSubmit"
          @click="handleSubmit"
        >
          {{ isSubmitting ? "提交中..." : "正式提交" }}
        </button>
      </div>
    </div>

    <div v-if="pageError" class="panel state-panel error">{{ pageError }}</div>
    <div v-else-if="isAccessCheckLoading" class="panel state-panel">正在验证实验访问权限...</div>
    <div v-else-if="isAccessRestricted" class="panel state-panel restricted">
      <h3>{{ accessRestrictionTitle }}</h3>
      <p>{{ accessRestrictionMessage }}</p>
      <div class="restricted-actions">
        <button class="btn gray" @click="goExperiments">返回实验列表</button>
        <button class="btn light" :disabled="!hasValidExperimentId" @click="goDocs">查看实验说明</button>
      </div>
    </div>
    <template v-else>
      <div v-if="isOverdue" class="panel state-panel overdue">
        <h3>本实验已截止，当前仅可查看内容</h3>
        <p>不可继续运行、保存或提交，历史记录仅支持查看。</p>
      </div>
      <div v-if="isWorkspaceLocked" class="panel state-panel locked">{{ workspaceMessage }}</div>
      <div v-if="reviewResultVisible" class="panel state-panel review">
        <div class="review-head">
          <span :class="['review-tag', reviewResultStatusCode]">批阅：{{ reviewResultStatusText }}</span>
          <span>批阅时间：{{ reviewResultTime }}</span>
        </div>
        <div class="review-comment">教师评语：{{ reviewResultComment }}</div>
      </div>

      <div v-if="showHistory" class="panel history-panel">
        <div class="history-header">
          <h3>历史记录</h3>
          <span v-if="historyLoading" class="hint">加载中...</span>
        </div>
        <p class="hint">当前载入：{{ currentVersionText }}（{{ currentSubmissionStatusText }}）</p>
        <p v-if="isWorkspaceLocked" class="hint">当前工作区已锁定，仅可查看历史，不可恢复到编辑器</p>
        <p v-if="historyError" class="history-error">{{ historyError }}</p>
        <p v-else-if="historyList.length === 0 && !historyLoading" class="hint">暂无历史记录</p>
        <div v-else class="history-list">
          <button
            v-for="item in historyList"
            :key="item.id"
            :class="['history-item', { active: isHistoryItemActive(item), locked: !canRestoreHistory }]"
            :disabled="historyDetailLoadingId === item.id || !canRestoreHistory"
            @click="loadHistoryDetail(item)"
          >
            <div>版本 v{{ item.version }}</div>
            <div>状态 {{ item.status }}</div>
            <div>{{ formatTime(item.created_at) }}</div>
            <div v-if="isHistoryItemActive(item)" class="history-current">当前载入</div>
            <div v-if="!canRestoreHistory" class="history-current">锁定，不可恢复</div>
            <div v-if="historyDetailLoadingId === item.id">恢复中...</div>
          </button>
        </div>
      </div>

      <div class="panel editor-panel">
        <div class="editor-status-bar">
          <div class="status-title">当前实验：{{ experimentTitle }}</div>
          <div class="status-line">
            <span :class="['draft-tag', autoSaveStatusClass]">{{ autoSaveStatusText }}</span>
            <span class="status-item">当前版本：{{ currentVersionText }}</span>
            <span class="status-item">当前记录：{{ currentSubmissionStatusText }}</span>
            <span class="status-item">最新版本：{{ latestSavedVersionText }}</span>
            <span class="status-item">工作区：{{ workspaceStateText }}</span>
            <span class="status-item">运行权限：{{ canRun ? "可运行" : "不可运行" }}</span>
            <span class="status-item">内容状态：{{ isDirty ? "未保存修改" : "未修改" }}</span>
            <span class="status-item">最近运行：{{ latestRunStatus }}</span>
            <span class="status-item">运行耗时：{{ latestRunDuration }}</span>
            <span class="status-item">最近保存：{{ displaySavedTime }}</span>
            <span class="status-item">最近提交：{{ displaySubmittedTime }}</span>
            <span class="status-item">开放时间：{{ openAtText }}</span>
            <span class="status-item">截止时间：{{ dueAtText }}</span>
          </div>
          <div class="status-hint status-hint-workspace">系统提示：{{ workspaceMessage }}</div>
          <div v-if="historyVersionHint" class="status-hint">{{ historyVersionHint }}</div>
        </div>
        <div class="editor-shell">
          <div v-if="hasEditorAccess" class="editor-mini-actions">
            <button class="mini-action mini-run" :disabled="runActionDisabled" @click="handleRunAction">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M8 5.5v13l10-6.5-10-6.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
              </svg>
              {{ miniRunActionText }}
            </button>
            <button
              v-if="canUseSubmissionFlow"
              class="mini-action mini-save"
              :disabled="isBusy || !hasValidExperimentId || !canSaveDraft"
              @click="handleSave"
            >
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M5 4.75h10.2l3.05 3.05V19.25H5V4.75Zm3.5 0v5.2h6.4v-5.2m-6.4 14.5v-5.3h6.9v5.3"
                  stroke="currentColor"
                  stroke-width="1.6"
                  stroke-linejoin="round"
                />
              </svg>
              {{ isSaving ? "保存中" : "保存" }}
            </button>
          </div>
          <div ref="editorContainer" class="editor-instance"></div>
          <div v-if="isPageLoading" class="editor-overlay">正在加载实验数据...</div>
        </div>
      </div>
      <div v-if="message && !showRunResultDrawer" class="panel state-panel info">{{ message }}</div>
    </template>

    <RunResultDrawer
      :visible="showRunResultDrawer"
      :loading="isRunning"
      :result="runResult"
      :message="message"
      :run-owner-label="runOwnerLabel"
      :rerun-disabled="rerunDisabled"
      :save-visible="canUseSubmissionFlow"
      :save-disabled="saveInDrawerDisabled"
      :save-loading="isSaving"
      @close="showRunResultDrawer = false"
      @rerun="handleRun"
      @save="handleSave"
    />
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";
import * as monaco from "monaco-editor";
import "monaco-editor/min/vs/editor/editor.main.css";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";

import { runCode } from "../api/code";
import { getStoredCurrentUser } from "../api/auth";
import { getExperimentById } from "../api/experiment";
import {
  getLatestSubmission,
  getSubmissionDetail,
  getSubmissionHistory,
  getWorkspaceStatus,
  saveSubmission,
  submitSubmission,
} from "../api/submission";
import { formatApiDateTime, parseApiDateTime } from "../utils/datetime";
import RunResultDrawer from "../components/RunResultDrawer.vue";

const defaultCode = 'print("hello world")';
const fallbackExperimentId = Number(import.meta.env.VITE_EXPERIMENT_ID);
const autoSaveDelayMs = 90000;
const runResultStorageNamespace = "edu:last-run-result:code-editor";

const route = useRoute();
const router = useRouter();
const currentViewer = getStoredCurrentUser() || {};
const viewerRole = ref(currentViewer?.role || localStorage.getItem("role") || "");
const runResultOwnerKey = String(currentViewer?.id || currentViewer?.username || "anonymous");
const runOwnerLabel = computed(() => {
  const roleText = viewerRole.value === "admin" ? "管理员" : viewerRole.value === "teacher" ? "教师" : "学生";
  const name = currentViewer?.full_name || currentViewer?.username || "当前用户";
  return `${name}（${roleText}）`;
});

const experiment = ref(null);
const currentCode = ref(defaultCode);
const lastSavedCode = ref(defaultCode);
const runResult = ref(null);
const isRunning = ref(false);
const isSaving = ref(false);
const isSubmitting = ref(false);
const isPageLoading = ref(false);
const pageError = ref("");
const message = ref("");
const showRunResultDrawer = ref(false);
const editorContainer = ref(null);
const isAccessCheckLoading = ref(false);
const accessRestriction = ref({
  blocked: false,
  reason: "",
  message: "",
});
const showHistory = ref(false);
const historyList = ref([]);
const historyLoading = ref(false);
const historyError = ref("");
const historyDetailLoadingId = ref(null);
const hasUnsavedChanges = ref(false);
const autoSaveStatus = ref("clean");
const autoSaveError = ref("");
const lastAutoSavedAt = ref(null);
const lastSavedAt = ref(null);
const lastSubmittedAt = ref(null);
const latestSavedVersion = ref(null);
const currentLoadedVersion = ref(null);
const currentSubmissionStatus = ref("unknown");
const latestSubmissionReview = ref({
  status: "pending",
  comment: "",
  reviewed_at: null,
});
const workspaceStatus = ref({
  experiment_id: null,
  is_locked: false,
  is_published: true,
  is_open: true,
  is_overdue: false,
  open_at: null,
  due_at: null,
  latest_submission_id: null,
  latest_version: null,
  latest_status: null,
  can_edit: true,
  can_save_draft: true,
  can_submit: true,
  can_run: true,
  message: "当前可继续编辑和保存草稿",
});
let editorInstance = null;
let autoSaveTimer = null;
let isSyncingEditorValue = false;

function parseExperimentId(rawValue) {
  const queryId = Number(rawValue);
  if (Number.isInteger(queryId) && queryId > 0) {
    return queryId;
  }
  if (Number.isInteger(fallbackExperimentId) && fallbackExperimentId > 0) {
    return fallbackExperimentId;
  }
  return 0;
}

const experimentId = computed(() => parseExperimentId(route.query.experiment_id));
const hasValidExperimentId = computed(() => experimentId.value > 0);
const runResultStorageKey = computed(() =>
  hasValidExperimentId.value ? `${runResultStorageNamespace}:${runResultOwnerKey}:${experimentId.value}` : "",
);
const experimentTitle = computed(() => experiment.value?.title || `实验${experimentId.value || "-"}：在线代码练习`);
const experimentDescription = computed(() => experiment.value?.description || "编辑代码后可直接运行并保存草稿");
const isBusy = computed(() => isRunning.value || isSaving.value || isSubmitting.value || isPageLoading.value);

self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === "json") {
      return new jsonWorker();
    }
    if (label === "css" || label === "scss" || label === "less") {
      return new cssWorker();
    }
    if (label === "html" || label === "handlebars" || label === "razor") {
      return new htmlWorker();
    }
    if (label === "typescript" || label === "javascript") {
      return new tsWorker();
    }
    return new editorWorker();
  },
};

const editorOptions = {
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 15,
  lineNumbersMinChars: 3,
  scrollBeyondLastLine: false,
  padding: { top: 12, bottom: 12 },
};

const autoSaveStatusText = computed(() => {
  if (autoSaveStatus.value === "saving") return "保存中";
  if (autoSaveStatus.value === "dirty") return "未保存";
  if (autoSaveStatus.value === "submitted") return "已提交";
  if (autoSaveStatus.value === "saved") return "已保存";
  if (autoSaveStatus.value === "auto_saved") {
    if (!lastAutoSavedAt.value) return "自动保存完成";
    return `自动保存完成（${formatTime(lastAutoSavedAt.value)}）`;
  }
  if (autoSaveStatus.value === "error") {
    return autoSaveError.value ? `保存失败：${autoSaveError.value}` : "保存失败";
  }
  return "未修改";
});

const autoSaveStatusClass = computed(() => {
  if (autoSaveStatus.value === "saving") return "saving";
  if (autoSaveStatus.value === "dirty") return "dirty";
  if (autoSaveStatus.value === "saved") return "saved";
  if (autoSaveStatus.value === "auto_saved") return "saved";
  if (autoSaveStatus.value === "submitted") return "submitted";
  if (autoSaveStatus.value === "error") return "error";
  return "clean";
});

const latestRunStatus = computed(() => runResult.value?.status || "-");
const latestRunDuration = computed(() =>
  typeof runResult.value?.execution_time_ms === "number" ? `${runResult.value.execution_time_ms} ms` : "-",
);
const isWorkspaceLocked = computed(() => Boolean(workspaceStatus.value?.is_locked));
const isOverdue = computed(() => Boolean(workspaceStatus.value?.is_overdue));
const canEdit = computed(() => Boolean(workspaceStatus.value?.can_edit ?? true) && !isOverdue.value);
const canSaveDraft = computed(() => Boolean(workspaceStatus.value?.can_save_draft ?? true) && !isOverdue.value);
const canSubmit = computed(() => Boolean(workspaceStatus.value?.can_submit ?? true) && !isOverdue.value);
const canRun = computed(() => Boolean(workspaceStatus.value?.can_run ?? true) && !isOverdue.value);
const canRestoreHistory = computed(() => canEdit.value && !isWorkspaceLocked.value && !isOverdue.value);
const isAccessRestricted = computed(() => Boolean(accessRestriction.value.blocked));
const hasEditorAccess = computed(() => !isAccessCheckLoading.value && !isAccessRestricted.value);
const isAdminViewer = computed(() => viewerRole.value === "admin");
const canUseSubmissionFlow = computed(() => hasEditorAccess.value && !isAdminViewer.value);
const rerunDisabled = computed(() => !hasEditorAccess.value || !hasValidExperimentId.value || !canRun.value || isBusy.value);
const saveInDrawerDisabled = computed(
  () => !hasEditorAccess.value || !hasValidExperimentId.value || !canSaveDraft.value || isBusy.value,
);
const hasRunResult = computed(() => Boolean(runResult.value));
const runActionDisabled = computed(
  () => isBusy.value || !hasValidExperimentId.value || (!canRun.value && !hasRunResult.value),
);
const runActionText = computed(() => {
  if (isRunning.value) return "运行中...";
  if (!canRun.value && hasRunResult.value) return "查看运行结果";
  return "运行";
});
const miniRunActionText = computed(() => {
  if (isRunning.value) return "运行中";
  if (!canRun.value && hasRunResult.value) return "查看结果";
  return "运行";
});
const accessRestrictionMessage = computed(() => accessRestriction.value.message || "当前实验暂不可访问");
const accessRestrictionTitle = computed(() => {
  if (accessRestriction.value.reason === "unpublished") {
    return "当前实验未发布";
  }
  if (accessRestriction.value.reason === "not-open") {
    return "当前实验尚未开放";
  }
  if (accessRestriction.value.reason === "guided-template-unavailable") {
    return "引导式模板模式尚未开放";
  }
  return "当前实验暂不可访问";
});
const workspaceMessage = computed(() => {
  const backendMessage = workspaceStatus.value?.message;
  if (backendMessage) {
    return backendMessage;
  }
  if (isOverdue.value) {
    return "本实验已截止，当前仅可查看内容";
  }
  return "当前可继续编辑和保存草稿";
});
const workspaceStateText = computed(() => {
  if (!workspaceStatus.value?.is_published) {
    return "未发布";
  }
  if (!workspaceStatus.value?.is_open) {
    return "未开放";
  }
  if (workspaceStatus.value?.is_overdue) {
    return "已截止";
  }
  if (isWorkspaceLocked.value) {
    return "已锁定";
  }
  return "可编辑";
});
const isDirty = computed(() => hasUnsavedChanges.value);
const currentVersionText = computed(() => (currentLoadedVersion.value ? `v${currentLoadedVersion.value}` : "-"));
const latestSavedVersionText = computed(() => (latestSavedVersion.value ? `v${latestSavedVersion.value}` : "-"));
const currentSubmissionStatusText = computed(() => {
  if (currentSubmissionStatus.value === "draft") return "draft";
  if (currentSubmissionStatus.value === "submitted") return "submitted";
  if (currentSubmissionStatus.value === "history") return "历史版本";
  return "unknown";
});
const historyVersionHint = computed(() => {
  if (currentSubmissionStatus.value === "history" && isDirty.value) {
    return `载入版本：${currentVersionText.value}（历史版本），保存或提交后将生成新版本`;
  }
  return "";
});
const displaySavedTime = computed(() => {
  if (lastSavedAt.value) {
    return formatTime(lastSavedAt.value);
  }
  if (lastAutoSavedAt.value) {
    return formatTime(lastAutoSavedAt.value);
  }
  return "-";
});
const displaySubmittedTime = computed(() => (lastSubmittedAt.value ? formatTime(lastSubmittedAt.value) : "-"));
const openAtText = computed(() => formatTime(workspaceStatus.value?.open_at));
const dueAtText = computed(() => formatTime(workspaceStatus.value?.due_at));
const reviewResultStatusCode = computed(() => latestSubmissionReview.value.status || "pending");
const reviewResultStatusText = computed(() => {
  if (reviewResultStatusCode.value === "passed") {
    return "通过";
  }
  if (reviewResultStatusCode.value === "failed") {
    return "未通过";
  }
  return "待批阅";
});
const reviewResultComment = computed(() => latestSubmissionReview.value.comment || "（无）");
const reviewResultTime = computed(() => formatTime(latestSubmissionReview.value.reviewed_at));
const reviewResultVisible = computed(
  () =>
    workspaceStatus.value?.latest_status === "submitted" &&
    (latestSubmissionReview.value.status === "passed" || latestSubmissionReview.value.status === "failed"),
);

function createEditor() {
  if (!editorContainer.value || editorInstance) {
    return;
  }
  editorInstance = monaco.editor.create(editorContainer.value, {
    value: currentCode.value,
    language: "python",
    theme: "vs-dark",
    ...editorOptions,
  });
  editorInstance.onDidChangeModelContent(() => {
    if (isSyncingEditorValue) {
      return;
    }
    currentCode.value = editorInstance.getValue();
    syncUnsavedState();
    scheduleAutoSave();
  });
  syncEditorReadonly();
}

async function ensureEditorInitialized() {
  await nextTick();
  createEditor();
  if (!editorInstance) {
    setTimeout(() => {
      createEditor();
      if (editorInstance) {
        setEditorValue(currentCode.value);
        syncEditorReadonly();
      }
    }, 0);
    return;
  }
  setEditorValue(currentCode.value);
  syncEditorReadonly();
}

function destroyEditor() {
  if (!editorInstance) {
    return;
  }
  editorInstance.dispose();
  editorInstance = null;
}

function clearAutoSaveTimer() {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = null;
  }
}

function parseVersion(value) {
  const version = Number(value);
  if (Number.isInteger(version) && version > 0) {
    return version;
  }
  return null;
}

function normalizeSubmissionStatus(rawStatus, fallback = "unknown") {
  if (rawStatus === "draft") return "draft";
  if (rawStatus === "submitted") return "submitted";
  if (rawStatus === "history") return "history";
  return fallback;
}

function updateLoadedSubmissionMeta(record, fallbackStatus = "unknown") {
  const status = normalizeSubmissionStatus(record?.status, fallbackStatus);
  const version = parseVersion(record?.version);
  currentSubmissionStatus.value = status;
  if (version) {
    currentLoadedVersion.value = version;
  }
}

function updateLatestSubmissionMeta(record) {
  const version = parseVersion(record?.version);
  if (version) {
    latestSavedVersion.value = version;
  }
  latestSubmissionReview.value = {
    status: record?.review_status || "pending",
    comment: record?.review_comment || "",
    reviewed_at: record?.reviewed_at || null,
  };
}

function updateWorkspaceStatus(payload) {
  workspaceStatus.value = {
    ...workspaceStatus.value,
    ...payload,
  };
  if (workspaceStatus.value.is_locked || workspaceStatus.value.is_overdue) {
    clearAutoSaveTimer();
    hasUnsavedChanges.value = false;
    autoSaveStatus.value = workspaceStatus.value.is_locked ? "submitted" : "clean";
  }
  syncEditorReadonly();
}

function isHistoryItemActive(item) {
  return parseVersion(item?.version) === currentLoadedVersion.value;
}

function syncEditorReadonly() {
  if (!editorInstance) {
    return;
  }
  editorInstance.updateOptions({ readOnly: !canEdit.value });
}

function buildSubmissionPayload(codeValue = currentCode.value) {
  const stdout = runResult.value?.stdout || "";
  const stderr = runResult.value?.stderr || "";
  const runOutput = stdout || stderr || runResult.value?.status || "not_run";
  const isPassed = typeof runResult.value?.success === "boolean" ? runResult.value.success : null;
  return {
    experiment_id: experimentId.value,
    code: codeValue,
    run_output: runOutput,
    is_passed: isPassed,
  };
}

function syncUnsavedState() {
  hasUnsavedChanges.value = currentCode.value !== lastSavedCode.value;
  if (hasUnsavedChanges.value) {
    if (autoSaveStatus.value !== "saving") {
      autoSaveStatus.value = "dirty";
    }
  } else if (!["saving", "saved", "auto_saved", "submitted", "error"].includes(autoSaveStatus.value)) {
    autoSaveStatus.value = "clean";
  }
}

function setEditorValue(nextCode, options = {}) {
  const { markAsSaved = true } = options;
  const finalCode = nextCode || defaultCode;
  currentCode.value = finalCode;
  if (editorInstance && editorInstance.getValue() !== finalCode) {
    isSyncingEditorValue = true;
    editorInstance.setValue(finalCode);
    isSyncingEditorValue = false;
  }
  if (markAsSaved) {
    lastSavedCode.value = finalCode;
    hasUnsavedChanges.value = false;
    autoSaveStatus.value = "clean";
    autoSaveError.value = "";
    clearAutoSaveTimer();
  } else {
    hasUnsavedChanges.value = true;
    if (autoSaveStatus.value !== "saving") {
      autoSaveStatus.value = "dirty";
    }
  }
}

function formatTime(value) {
  return formatApiDateTime(value);
}

function restoreRunResultSnapshot() {
  if (!runResultStorageKey.value || typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(runResultStorageKey.value);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    const snapshot = parsed?.result;
    if (!snapshot || typeof snapshot !== "object") {
      return null;
    }
    return snapshot;
  } catch (_error) {
    return null;
  }
}

function saveRunResultSnapshot(nextResult) {
  if (!runResultStorageKey.value || typeof window === "undefined" || !nextResult || typeof nextResult !== "object") {
    return;
  }
  try {
    window.localStorage.setItem(
      runResultStorageKey.value,
      JSON.stringify({
        saved_at: new Date().toISOString(),
        result: nextResult,
      }),
    );
  } catch (_error) {
    // ignore storage write errors
  }
}

function resolveAccessRestriction(experimentDetail, workspace, isAdminMode = false) {
  if (experimentDetail?.interaction_mode === "guided_template") {
    return {
      blocked: true,
      reason: "guided-template-unavailable",
      message: "该实验将采用引导式模板模式，当前尚未开放",
    };
  }
  if (isAdminMode) {
    return {
      blocked: false,
      reason: "",
      message: "",
    };
  }
  const workspacePublished = workspace?.is_published;
  if (workspacePublished === false) {
    return {
      blocked: true,
      reason: "unpublished",
      message: "当前实验未发布，请稍后再进入",
    };
  }
  const experimentPublished = experimentDetail?.is_published;
  if (workspacePublished !== true && experimentPublished === false) {
    return {
      blocked: true,
      reason: "unpublished",
      message: "当前实验未发布，请稍后再进入",
    };
  }
  const workspaceOpen = workspace?.is_open;
  if (workspaceOpen === false) {
    return {
      blocked: true,
      reason: "not-open",
      message: "当前实验尚未开放，请在开放时间后进入",
    };
  }
  const openAtRaw = workspace?.open_at || experimentDetail?.open_at;
  if (openAtRaw) {
    const openAtDate = parseApiDateTime(openAtRaw);
    const openAtTime = openAtDate ? openAtDate.getTime() : Number.NaN;
    if (!Number.isNaN(openAtTime) && Date.now() < openAtTime) {
      return {
        blocked: true,
        reason: "not-open",
        message: "当前实验尚未开放，请在开放时间后进入",
      };
    }
  }
  return {
    blocked: false,
    reason: "",
    message: "",
  };
}

async function refreshLatestAndHistory(options = {}) {
  const { updateLoadedFromLatest = false } = options;
  try {
    const workspace = await getWorkspaceStatus(experimentId.value);
    updateWorkspaceStatus(workspace);
  } catch (error) {
    message.value = `工作区状态同步失败：${error.message}`;
  }
  let latest = null;
  try {
    latest = await getLatestSubmission(experimentId.value);
    updateLatestSubmissionMeta(latest);
    if (latest?.status === "submitted") {
      lastSubmittedAt.value = latest.updated_at || latest.created_at || new Date().toISOString();
    } else if (latest?.status === "draft" || latest?.code) {
      lastSavedAt.value = latest.updated_at || latest.created_at || new Date().toISOString();
    }
    if (updateLoadedFromLatest) {
      updateLoadedSubmissionMeta(latest, latest?.status ? "unknown" : "draft");
    }
  } catch (error) {
    if (error.message.includes("暂无提交记录")) {
      latestSavedVersion.value = null;
      if (updateLoadedFromLatest) {
        currentLoadedVersion.value = null;
        currentSubmissionStatus.value = "unknown";
      }
    }
    if (showHistory.value) {
      historyError.value = `最新版本同步失败：${error.message}`;
    }
  }

  try {
    historyList.value = await getSubmissionHistory(experimentId.value);
    historyError.value = "";
  } catch (error) {
    if (showHistory.value) {
      historyError.value = `历史记录加载失败：${error.message}`;
    }
  }

  return latest;
}

async function loadExperimentAndCode() {
  runResult.value = null;
  historyList.value = [];
  historyError.value = "";
  showHistory.value = false;
  pageError.value = "";
  message.value = "";
  lastSavedAt.value = null;
  lastSubmittedAt.value = null;
  lastAutoSavedAt.value = null;
  latestSavedVersion.value = null;
  currentLoadedVersion.value = null;
  currentSubmissionStatus.value = "unknown";
  latestSubmissionReview.value = {
    status: "pending",
    comment: "",
    reviewed_at: null,
  };
  updateWorkspaceStatus({
    experiment_id: experimentId.value,
    is_locked: false,
    is_published: true,
    is_open: true,
    is_overdue: false,
    open_at: null,
    due_at: null,
    latest_submission_id: null,
    latest_version: null,
    latest_status: null,
    can_edit: true,
    can_save_draft: true,
    can_submit: true,
    can_run: true,
    message: "当前可继续编辑和保存草稿",
  });
  accessRestriction.value = {
    blocked: false,
    reason: "",
    message: "",
  };

  if (!hasValidExperimentId.value) {
    pageError.value = "请先在实验列表中选择实验后再进入代码编辑";
    setEditorValue(defaultCode);
    return;
  }

  isAccessCheckLoading.value = true;
  isPageLoading.value = true;
  try {
    const detail = await getExperimentById(experimentId.value);
    experiment.value = detail;
    const workspace = await getWorkspaceStatus(experimentId.value);
    updateWorkspaceStatus(workspace);
    accessRestriction.value = resolveAccessRestriction(detail, workspace, isAdminViewer.value);

    const starterCode = detail?.starter_code || defaultCode;
    if (accessRestriction.value.blocked) {
      clearAutoSaveTimer();
      hasUnsavedChanges.value = false;
      autoSaveStatus.value = "clean";
      runResult.value = null;
      showHistory.value = false;
      historyList.value = [];
      setEditorValue(starterCode);
      message.value = accessRestriction.value.message;
      return;
    }

    let nextCode = starterCode;
    let loadedStatus = "clean";

    try {
      const latest = await getLatestSubmission(experimentId.value);
      if (latest?.code) {
        nextCode = latest.code;
        updateLatestSubmissionMeta(latest);
        updateLoadedSubmissionMeta(latest, latest?.status ? "unknown" : "draft");
        const latestTime = latest.updated_at || latest.created_at || null;
        if (latest?.status === "submitted") {
          loadedStatus = "submitted";
          lastSubmittedAt.value = latestTime;
        } else {
          loadedStatus = "saved";
          if (latestTime) {
            lastSavedAt.value = latestTime;
          }
        }
        message.value = "已加载最新保存代码";
      } else {
        message.value = detail?.starter_code ? "已加载实验初始代码" : "已加载默认模板代码";
      }
    } catch (error) {
      message.value = error.message.includes("暂无提交记录")
        ? detail?.starter_code
          ? "暂无历史提交，已加载实验初始代码"
          : "暂无历史提交，已加载默认模板代码"
        : `最新代码加载失败：${error.message}，已加载实验模板`;
    }

    setEditorValue(nextCode);
    const restoredRunResult = restoreRunResultSnapshot();
    if (restoredRunResult) {
      runResult.value = restoredRunResult;
      if (!canRun.value) {
        message.value = `${message.value ? `${message.value}；` : ""}已恢复最近一次运行结果，可点击“查看运行结果”`;
      }
    }
    autoSaveStatus.value = loadedStatus;
    if (isWorkspaceLocked.value) {
      autoSaveStatus.value = "submitted";
      message.value = hasRunResult.value
        ? `${workspaceMessage.value}，可点击“查看运行结果”查看最近一次运行输出`
        : workspaceMessage.value;
    }
  } catch (error) {
    experiment.value = null;
    setEditorValue(defaultCode);
    pageError.value = `实验加载失败：${error.message}`;
  } finally {
    isAccessCheckLoading.value = false;
    isPageLoading.value = false;
  }
}

async function triggerAutoSave() {
  if (
    !hasEditorAccess.value ||
    !hasValidExperimentId.value ||
    !hasUnsavedChanges.value ||
    !currentCode.value.trim() ||
    !canSaveDraft.value ||
    !canEdit.value
  ) {
    return;
  }
  if (isSaving.value || isRunning.value || isSubmitting.value || isPageLoading.value) {
    scheduleAutoSave();
    return;
  }

  autoSaveStatus.value = "saving";
  autoSaveError.value = "";
  try {
    const saved = await saveSubmission(buildSubmissionPayload());
    lastSavedCode.value = currentCode.value;
    hasUnsavedChanges.value = false;
    lastAutoSavedAt.value = new Date().toISOString();
    updateLoadedSubmissionMeta(saved, "draft");
    updateLatestSubmissionMeta(saved);
    await refreshLatestAndHistory({ updateLoadedFromLatest: true });
    autoSaveStatus.value = "auto_saved";
    autoSaveError.value = "";
  } catch (error) {
    autoSaveStatus.value = "error";
    autoSaveError.value = error.message || "自动保存失败";
  }
}

function scheduleAutoSave() {
  clearAutoSaveTimer();
  if (!hasUnsavedChanges.value || !hasValidExperimentId.value || !canSaveDraft.value || !canEdit.value) {
    return;
  }
  autoSaveStatus.value = "dirty";
  autoSaveTimer = setTimeout(() => {
    autoSaveTimer = null;
    triggerAutoSave();
  }, autoSaveDelayMs);
}

async function handleRun() {
  showRunResultDrawer.value = true;
  if (!hasEditorAccess.value) {
    message.value = accessRestrictionMessage.value;
    return;
  }
  if (!hasValidExperimentId.value) {
    message.value = "缺少有效实验编号，无法运行";
    return;
  }
  if (!canRun.value) {
    message.value = isOverdue.value ? "本实验已截止，当前不可运行代码" : workspaceMessage.value;
    return;
  }
  if (!currentCode.value.trim()) {
    message.value = "代码不能为空";
    return;
  }
  isRunning.value = true;
  message.value = "";
  try {
    runResult.value = await runCode(currentCode.value, experimentId.value);
    saveRunResultSnapshot(runResult.value);
    message.value = "运行完成";
  } catch (error) {
    message.value = `运行失败：${error.message}`;
  } finally {
    isRunning.value = false;
  }
}

function handleRunAction() {
  if (!canRun.value && hasRunResult.value) {
    showRunResultDrawer.value = true;
    message.value = isOverdue.value
      ? "本实验已截止，当前不可重新运行代码，已为你打开最近一次运行结果。"
      : "当前运行权限已关闭，已为你打开最近一次运行结果。";
    return;
  }
  handleRun();
}

async function handleSave() {
  if (isAdminViewer.value) {
    message.value = "管理员测试模式不支持保存草稿";
    return;
  }
  if (!hasEditorAccess.value) {
    message.value = accessRestrictionMessage.value;
    return;
  }
  if (!hasValidExperimentId.value) {
    message.value = "缺少有效实验编号，无法保存";
    return;
  }
  if (!currentCode.value.trim()) {
    message.value = "代码不能为空";
    return;
  }
  if (!canSaveDraft.value) {
    message.value = isOverdue.value ? "本实验已截止，当前不可保存草稿" : workspaceMessage.value;
    return;
  }
  clearAutoSaveTimer();
  isSaving.value = true;
  autoSaveStatus.value = "saving";
  message.value = "";
  try {
    const saved = await saveSubmission(buildSubmissionPayload());
    lastSavedCode.value = currentCode.value;
    hasUnsavedChanges.value = false;
    lastSavedAt.value = new Date().toISOString();
    updateLoadedSubmissionMeta(saved, "draft");
    updateLatestSubmissionMeta(saved);
    await refreshLatestAndHistory({ updateLoadedFromLatest: true });
    autoSaveStatus.value = "saved";
    autoSaveError.value = "";
    message.value = `草稿保存成功，当前版本 ${currentVersionText.value}`;
  } catch (error) {
    autoSaveStatus.value = "error";
    autoSaveError.value = error.message || "保存失败";
    message.value = `保存失败：${error.message}`;
  } finally {
    isSaving.value = false;
  }
}

async function handleSubmit() {
  if (isAdminViewer.value) {
    message.value = "管理员测试模式不支持正式提交";
    return;
  }
  if (!hasEditorAccess.value) {
    message.value = accessRestrictionMessage.value;
    return;
  }
  if (!hasValidExperimentId.value) {
    message.value = "缺少有效实验编号，无法提交";
    return;
  }
  if (!currentCode.value.trim()) {
    message.value = "代码不能为空";
    return;
  }
  if (!canSubmit.value) {
    message.value = isOverdue.value ? "本实验已截止，当前不可正式提交" : workspaceMessage.value;
    return;
  }
  clearAutoSaveTimer();
  isSubmitting.value = true;
  autoSaveStatus.value = "saving";
  message.value = "";
  try {
    const submission = await submitSubmission(buildSubmissionPayload());
    lastSavedCode.value = currentCode.value;
    hasUnsavedChanges.value = false;
    lastSubmittedAt.value = new Date().toISOString();
    updateLoadedSubmissionMeta(submission, "submitted");
    updateLatestSubmissionMeta(submission);
    await refreshLatestAndHistory({ updateLoadedFromLatest: true });
    autoSaveStatus.value = "submitted";
    autoSaveError.value = "";
    message.value = `已正式提交，当前版本 ${currentVersionText.value}`;
  } catch (error) {
    autoSaveStatus.value = "error";
    autoSaveError.value = error.message || "提交失败";
    message.value = `提交失败：${error.message}`;
  } finally {
    isSubmitting.value = false;
  }
}

async function loadHistory() {
  historyLoading.value = true;
  historyError.value = "";
  historyList.value = [];
  try {
    historyList.value = await getSubmissionHistory(experimentId.value);
  } catch (error) {
    historyError.value = `历史记录加载失败：${error.message}`;
  } finally {
    historyLoading.value = false;
  }
}

async function toggleHistoryPanel() {
  if (!hasEditorAccess.value) {
    message.value = accessRestrictionMessage.value;
    return;
  }
  if (!hasValidExperimentId.value) {
    message.value = "缺少有效实验编号，无法查看历史";
    return;
  }
  showHistory.value = !showHistory.value;
  if (showHistory.value) {
    await loadHistory();
  }
}

async function loadHistoryDetail(item) {
  if (!canRestoreHistory.value) {
    if (isOverdue.value) {
      message.value = "本实验已截止，当前不可恢复历史版本进行修改";
      return;
    }
    message.value = "该实验已提交最终版，不能再恢复历史版本进行修改";
    return;
  }
  if (hasUnsavedChanges.value) {
    const confirmed = window.confirm("当前有未保存修改，恢复历史版本会覆盖当前代码，是否继续？");
    if (!confirmed) {
      return;
    }
  }
  historyDetailLoadingId.value = item.id;
  try {
    const detail = await getSubmissionDetail(item.id);
    if (typeof detail?.code === "string") {
      clearAutoSaveTimer();
      setEditorValue(detail.code, { markAsSaved: false });
      currentLoadedVersion.value = parseVersion(item?.version);
      currentSubmissionStatus.value = "history";
      message.value = `已加载历史版本 v${item.version}，请保存或提交`;
    } else {
      message.value = "该版本无可用代码";
    }
  } catch (error) {
    message.value = `版本恢复失败：${error.message}`;
  } finally {
    historyDetailLoadingId.value = null;
  }
}

function goDocs() {
  if (!hasValidExperimentId.value) {
    return;
  }
  router.push(`/docs?experiment_id=${experimentId.value}`);
}

function goExperiments() {
  if (isAdminViewer.value) {
    router.push("/admin/experiments");
    return;
  }
  router.push("/experiments");
}

watch(
  () => experimentId.value,
  () => {
    clearAutoSaveTimer();
    loadExperimentAndCode();
  },
  { immediate: true },
);

watch(
  () => hasEditorAccess.value,
  async (allowed) => {
    if (allowed) {
      await ensureEditorInitialized();
      return;
    }
    clearAutoSaveTimer();
    showHistory.value = false;
    destroyEditor();
  },
  { immediate: true },
);

watch(
  () => canEdit.value,
  () => {
    syncEditorReadonly();
    if (!canEdit.value) {
      clearAutoSaveTimer();
    }
  },
  { immediate: true },
);

watch(
  () => isOverdue.value,
  (overdue) => {
    if (!overdue) {
      return;
    }
    clearAutoSaveTimer();
    hasUnsavedChanges.value = false;
    autoSaveStatus.value = "clean";
    syncEditorReadonly();
  },
  { immediate: true },
);

const handleBeforeUnload = (event) => {
  if (!hasEditorAccess.value) {
    return;
  }
  if (!hasUnsavedChanges.value) {
    return;
  }
  event.preventDefault();
  event.returnValue = "";
};

onBeforeRouteLeave(() => {
  if (!hasEditorAccess.value) {
    return true;
  }
  if (!hasUnsavedChanges.value) {
    return true;
  }
  return window.confirm("当前有未保存修改，离开页面将丢失最新改动，是否继续离开？");
});

onMounted(() => {
  viewerRole.value = getStoredCurrentUser()?.role || localStorage.getItem("role") || "";
  ensureEditorInitialized();
  window.addEventListener("beforeunload", handleBeforeUnload);
});

onBeforeUnmount(() => {
  clearAutoSaveTimer();
  window.removeEventListener("beforeunload", handleBeforeUnload);
  destroyEditor();
});
</script>

<style scoped>
.editor-page {
  display: grid;
  gap: 16px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.toolbar-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title-wrap h2 {
  margin: 0;
  font-size: 20px;
}

.title-wrap p {
  margin: 6px 0 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.admin-mode-tip {
  margin: 8px 0 0;
  color: var(--warn-strong);
  background: var(--warn-soft);
  border: 1px solid var(--warn-border);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  font-weight: 600;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid var(--border-soft);
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
  color: var(--surface-1);
}

.btn.run {
  background: var(--brand-600);
}

.btn.save {
  background: var(--accent-teal-strong);
}

.btn.submit {
  background: var(--accent-indigo-strong);
}

.btn.light {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

.btn.gray {
  background: var(--text-muted);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.state-panel {
  color: var(--text-body);
}

.state-panel.error {
  border-color: var(--danger-border);
  color: var(--danger-strong);
  background: var(--danger-soft);
}

.state-panel.info {
  border-color: var(--brand-border);
  color: var(--brand-700);
  background: var(--brand-soft);
}

.state-panel.locked {
  border-color: var(--accent-indigo-border);
  color: var(--accent-indigo-strong);
  background: var(--accent-indigo-soft);
  font-weight: 600;
}

.state-panel.review {
  border-color: var(--accent-cyan-border);
  background: var(--accent-cyan-soft);
  color: var(--accent-cyan-strong);
  display: grid;
  gap: 8px;
}

.state-panel.restricted {
  border-color: var(--warn-border);
  background: var(--warn-soft);
  color: var(--warn-strong);
}

.state-panel.restricted h3 {
  margin: 0 0 8px;
}

.state-panel.restricted p {
  margin: 0;
}

.state-panel.overdue {
  border-color: var(--warn-border);
  color: var(--warn-strong);
  background: var(--warn-soft);
}

.state-panel.overdue h3 {
  margin: 0 0 8px;
}

.state-panel.overdue p {
  margin: 0;
}

.restricted-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.review-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 14px;
}

.review-comment {
  font-size: 14px;
  color: var(--code-bg);
  white-space: pre-wrap;
}

.review-tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 13px;
  font-weight: 700;
}

.review-tag.passed {
  background: var(--success-soft);
  color: var(--success-strong);
}

.review-tag.failed {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.history-panel {
  display: grid;
  gap: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h3 {
  margin: 0;
}

.hint {
  margin: 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.history-error {
  margin: 0;
  color: var(--danger-strong);
}

.history-list {
  display: grid;
  gap: 8px;
  max-height: 220px;
  overflow-y: auto;
}

.history-item {
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  background: var(--surface-3);
  text-align: left;
  padding: 10px 12px;
  display: grid;
  gap: 4px;
  cursor: pointer;
}

.history-item.active {
  border-color: var(--accent-indigo-border);
  background: var(--accent-indigo-soft);
}

.history-item.locked {
  opacity: 0.85;
}

.history-current {
  color: var(--accent-indigo-strong);
  font-size: 13px;
  font-weight: 700;
}

.history-item:disabled {
  opacity: 0.7;
  cursor: wait;
}

.editor-panel {
  min-height: 460px;
  padding: 0 0 14px;
  overflow: hidden;
}

.editor-status-bar {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-soft);
}

.status-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-strong);
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.status-item {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 600;
  background: var(--accent-indigo-soft);
  color: var(--accent-indigo-strong);
}

.status-hint {
  margin: 0;
  color: var(--warn-strong);
  background: var(--warn-soft);
  border: 1px solid var(--warn-border);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  font-weight: 600;
}

.status-hint-workspace {
  color: var(--brand-800);
  background: var(--brand-soft-2);
  border-color: var(--brand-border-strong);
}

.draft-tag {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 700;
}

.draft-tag.clean {
  background: var(--neutral-btn);
  color: var(--text-body);
}

.draft-tag.dirty {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.draft-tag.saving {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

.draft-tag.saved {
  background: var(--success-soft);
  color: var(--success-strong);
}

.draft-tag.submitted {
  background: var(--accent-indigo-soft);
  color: var(--accent-indigo-strong);
}

.draft-tag.error {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.editor-shell {
  position: relative;
}

.editor-mini-actions {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 6;
  display: flex;
  gap: 8px;
}

.mini-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  background: var(--surface-1);
  color: var(--text-strong);
  box-shadow: var(--shadow-soft);
}

.mini-action svg {
  width: 14px;
  height: 14px;
}

.mini-run {
  border-color: var(--brand-border-strong);
  color: var(--brand-700);
}

.mini-save {
  border-color: var(--success-border);
  color: var(--success-strong);
}

.mini-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.editor-instance {
  height: 460px;
}

.editor-overlay {
  position: absolute;
  inset: 0;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--overlay-panel);
  color: var(--text-strong);
  font-weight: 600;
  pointer-events: all;
}

@media (max-width: 680px) {
  .editor-mini-actions {
    top: 8px;
    right: 8px;
    gap: 6px;
  }

  .mini-action {
    height: 30px;
    padding: 0 8px;
    font-size: 13px;
  }
}
</style>
