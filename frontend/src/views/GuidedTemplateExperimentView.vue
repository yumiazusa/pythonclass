<template>
  <section class="guided-page">
    <article class="panel head-panel">
      <div class="head-main">
        <h2>{{ experimentTitle }}</h2>
        <p>{{ experimentDescription }}</p>
      </div>
      <div class="head-actions">
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
    </article>

    <article v-if="pageError" class="panel error">{{ pageError }}</article>
    <article v-else-if="isAccessCheckLoading" class="panel state">正在验证实验访问权限...</article>
    <article v-else-if="isAccessRestricted" class="panel warn">
      <h3>{{ accessRestrictionTitle }}</h3>
      <p>{{ accessRestrictionMessage }}</p>
      <div class="inline-actions">
        <button class="btn gray" @click="goExperiments">返回实验列表</button>
        <button class="btn light" :disabled="!hasValidExperimentId" @click="goDocs">查看实验说明</button>
      </div>
    </article>
    <template v-else>
      <article class="panel params-panel">
        <h3>参数设置（guided template）</h3>
        <div class="params-grid">
          <label v-for="field in templateFields" :key="field.name" class="field">
            <span>{{ field.label }}（{{ field.name }}）</span>
            <select v-if="field.type === 'select'" v-model="templateForm[field.name]" :disabled="isBusy || !canTemplateActions">
              <option value="">{{ field.placeholder || "请选择" }}</option>
              <option v-for="item in field.options" :key="`${field.name}-${item.value}`" :value="item.value">{{ item.label }}</option>
            </select>
            <div v-else-if="field.type === 'password'" class="password-input-wrap">
              <input
                v-model="templateForm[field.name]"
                :type="isTemplatePasswordVisible(field.name) ? 'text' : 'password'"
                :placeholder="field.placeholder"
                :disabled="isBusy || !canTemplateActions"
              />
              <button
                type="button"
                class="password-toggle"
                :disabled="isBusy || !canTemplateActions"
                :aria-label="isTemplatePasswordVisible(field.name) ? '隐藏密码' : '显示密码'"
                :title="isTemplatePasswordVisible(field.name) ? '隐藏密码' : '显示密码'"
                @click.prevent="toggleTemplatePasswordVisibility(field.name)"
              >
                <svg v-if="isTemplatePasswordVisible(field.name)" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 5.5c5.7 0 9.8 3.6 11 8.3a1 1 0 0 1 0 .4c-1.2 4.7-5.3 8.3-11 8.3S2.2 19 1 14.2a1 1 0 0 1 0-.4C2.2 9.1 6.3 5.5 12 5.5Zm0 2c-4.6 0-7.8 3-8.9 6.5 1.1 3.5 4.3 6.5 8.9 6.5 4.6 0 7.8-3 8.9-6.5-1.1-3.5-4.3-6.5-8.9-6.5Zm0 2.5a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"
                  />
                </svg>
                <svg v-else viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M3 3.7 20.3 21l-1.4 1.4-3.1-3.1A12.9 12.9 0 0 1 12 20.5C6.3 20.5 2.2 17 1 12.2a1 1 0 0 1 0-.4 10.9 10.9 0 0 1 5.4-6.7L1.6 4.4 3 3.7Zm6.2 6.2a3.9 3.9 0 0 0 5 5l-5-5Zm2.8-6.4c5.7 0 9.8 3.6 11 8.3a1 1 0 0 1 0 .4 11 11 0 0 1-5.6 6.8l-1.5-1.5a9.1 9.1 0 0 0 5-5.5c-1.1-3.5-4.3-6.5-8.9-6.5a9 9 0 0 0-3.8.8L6.8 4.8a11 11 0 0 1 5.2-1.3Zm-.1 3.1a5.9 5.9 0 0 1 5.9 5.9c0 .8-.2 1.6-.5 2.3l-1.6-1.6a3.9 3.9 0 0 0-5.1-5.1L9 6.6c.7-.3 1.5-.5 2.8-.5Z"
                  />
                </svg>
              </button>
            </div>
            <textarea
              v-else-if="field.type === 'textarea'"
              v-model="templateForm[field.name]"
              rows="4"
              :placeholder="field.placeholder"
              :disabled="isBusy || !canTemplateActions"
            ></textarea>
            <input
              v-else
              v-model="templateForm[field.name]"
              :type="resolveInputType(field)"
              :min="field.type === 'number' && field.min !== null ? field.min : undefined"
              :max="field.type === 'number' && field.max !== null ? field.max : undefined"
              :step="field.type === 'number' && field.step !== null ? field.step : undefined"
              :placeholder="field.placeholder"
              :disabled="isBusy || !canTemplateActions"
            />
          </label>
          <label class="field">
            <span>模板类型（template_type）</span>
            <input :value="experiment?.template_type || '-'" type="text" disabled />
          </label>
        </div>

        <div class="imports-wrap">
          <article class="import-box">
            <h4>固定库（不可删除）</h4>
            <ul>
              <li v-for="item in fixedImports" :key="item">{{ item }}</li>
            </ul>
          </article>
          <article class="import-box">
            <h4>可选库（可勾选）</h4>
            <p v-if="optionalImports.length === 0" class="hint">暂无可选库</p>
            <label v-for="item in optionalImports" :key="item" class="option-item">
              <input
                v-model="selectedOptionalImports"
                type="checkbox"
                :value="item"
                :disabled="isBusy || !canTemplateActions"
              />
              <span>{{ item }}</span>
            </label>
          </article>
          <article v-if="allowCustomImport" class="import-box">
            <h4>自定义导入（多行）</h4>
            <textarea
              v-model="customImportText"
              rows="6"
              :disabled="isBusy || !canTemplateActions"
              placeholder="示例：&#10;import json&#10;import re&#10;from sklearn.model_selection import train_test_split"
            ></textarea>
            <p class="hint">仅支持 import / from ... import ...，并受白名单与危险库规则校验。</p>
          </article>
        </div>

        <div class="inline-actions">
          <button class="btn plain" :disabled="isBusy || !canTemplateActions" @click="loadTemplateSkeleton">加载骨架模板代码</button>
          <button class="btn plain" :disabled="isBusy || !canTemplateActions" @click="clearEditorCode">清空骨架模板代码</button>
          <button class="btn plain" :disabled="isBusy || !canTemplateActions" @click="restoreDefaultSkeleton">恢复默认骨架模板代码</button>
          <button class="btn primary" :disabled="isBusy || !canTemplateActions" @click="applyTemplateToCode">应用参数到代码</button>
        </div>
        <p v-if="templateError" class="tips error-text">{{ templateError }}</p>
        <p v-else-if="templateMessage" class="tips success-text">{{ templateMessage }}</p>
      </article>

      <article v-if="isOverdue" class="panel warn">
        <h3>本实验已截止，当前仅可查看内容</h3>
        <p>不可继续运行、保存或提交，历史记录仅支持查看。</p>
      </article>
      <article v-if="isWorkspaceLocked" class="panel info">{{ workspaceMessage }}</article>
      <article v-if="message && !showRunResultDrawer" class="panel info">{{ message }}</article>

      <article v-if="showHistory" class="panel history-panel">
        <div class="history-head">
          <h3>历史记录</h3>
          <span v-if="historyLoading" class="hint">加载中...</span>
        </div>
        <p class="hint">当前载入：{{ currentVersionText }}（{{ currentSubmissionStatusText }}）</p>
        <p v-if="historyError" class="error-text">{{ historyError }}</p>
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
            <div v-if="isHistoryItemActive(item)" class="mini-label">当前载入</div>
            <div v-if="historyDetailLoadingId === item.id">恢复中...</div>
          </button>
        </div>
      </article>

      <article class="panel editor-panel">
        <div class="status-line">
          <span class="status-item">工作区：{{ workspaceStateText }}</span>
          <span class="status-item">运行权限：{{ canRun ? "可运行" : "不可运行" }}</span>
          <span class="status-item">当前版本：{{ currentVersionText }}</span>
          <span class="status-item">最新版本：{{ latestSavedVersionText }}</span>
          <span class="status-item">最近运行：{{ latestRunStatus }}</span>
          <span class="status-item">运行耗时：{{ latestRunDuration }}</span>
        </div>
        <div class="status-hint">系统提示：{{ workspaceMessage }}</div>
        <div class="editor-shell">
          <div class="editor-mini-actions">
            <button
              v-if="canUseSubmissionFlow"
              class="mini-action mini-save"
              :disabled="isBusy || !hasValidExperimentId || !canSaveDraft"
              title="保存草稿"
              @click="handleSave"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M4 4h12l4 4v12H4V4zm3 0v6h8V4H7zm0 10v4h10v-4H7z"
                  fill="currentColor"
                />
              </svg>
              <span>保存</span>
            </button>
            <button
              v-if="hasEditorAccess"
              class="mini-action mini-run"
              :disabled="runActionDisabled"
              title="运行代码"
              @click="handleRunAction"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8 5v14l11-7z" fill="currentColor" />
              </svg>
              <span>{{ miniRunActionText }}</span>
            </button>
          </div>
          <div ref="editorContainer" class="editor-instance"></div>
          <div v-if="isPageLoading" class="editor-overlay">正在加载实验数据...</div>
        </div>
      </article>
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";
import * as monaco from "monaco-editor";
import "monaco-editor/min/vs/editor/editor.main.css";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";

import RunResultDrawer from "../components/RunResultDrawer.vue";
import { getStoredCurrentUser } from "../api/auth";
import { runCode } from "../api/code";
import { getExperimentById, validateGuidedTemplateImports } from "../api/experiment";
import {
  getLatestSubmission,
  getSubmissionDetail,
  getSubmissionHistory,
  getWorkspaceStatus,
  saveSubmission,
  submitSubmission,
} from "../api/submission";
import { formatApiDateTime, parseApiDateTime } from "../utils/datetime";
import { buildRunResultFromSubmission, hasRunnableResult, normalizeRunResult } from "../utils/run-result";

const route = useRoute();
const router = useRouter();
const currentViewer = getStoredCurrentUser() || {};
const viewerRole = ref(currentViewer?.role || localStorage.getItem("role") || "");
const runResultOwnerKey = String(currentViewer?.id || currentViewer?.username || "anonymous");
const templateStateStorageNamespace = "edu:guided-template:state";
const runOwnerLabel = computed(() => {
  const roleText = viewerRole.value === "admin" ? "管理员" : viewerRole.value === "teacher" ? "教师" : "学生";
  const name = currentViewer?.full_name || currentViewer?.username || "当前用户";
  return `${name}（${roleText}）`;
});
const fallbackExperimentId = Number(import.meta.env.VITE_EXPERIMENT_ID);
const runResultStorageNamespace = "edu:last-run-result:guided-template";

const experiment = ref(null);
const currentCode = ref("");
const lastSavedCode = ref("");
const runResult = ref(null);
const message = ref("");
const pageError = ref("");
const templateError = ref("");
const templateMessage = ref("");
const isRunning = ref(false);
const isSaving = ref(false);
const isSubmitting = ref(false);
const isPageLoading = ref(false);
const isAccessCheckLoading = ref(false);
const showRunResultDrawer = ref(false);
const showHistory = ref(false);
const historyList = ref([]);
const historyLoading = ref(false);
const historyError = ref("");
const historyDetailLoadingId = ref(null);
const editorContainer = ref(null);
const hasUnsavedChanges = ref(false);
const currentLoadedVersion = ref(null);
const latestSavedVersion = ref(null);
const currentSubmissionStatus = ref("unknown");

const accessRestriction = ref({
  blocked: false,
  reason: "",
  message: "",
});

const templateForm = reactive({});
const templateFields = ref([]);
const originalTemplateCode = ref("");
const fixedImports = ref([]);
const optionalImports = ref([]);
const selectedOptionalImports = ref([]);
const allowCustomImport = ref(false);
const customImportText = ref("");
const templatePasswordVisibleMap = reactive({});

const workspaceStatus = ref({
  experiment_id: null,
  is_locked: false,
  is_published: true,
  is_open: true,
  is_overdue: false,
  latest_submission_id: null,
  latest_version: null,
  latest_status: null,
  can_edit: true,
  can_run: true,
  can_save_draft: true,
  can_submit: true,
  message: "当前可继续编辑和保存草稿",
});

let editorInstance = null;
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
const templateStateStorageKey = computed(() =>
  hasValidExperimentId.value ? `${templateStateStorageNamespace}:${runResultOwnerKey}:${experimentId.value}` : "",
);
const isAdminViewer = computed(() => viewerRole.value === "admin");
const experimentTitle = computed(() => experiment.value?.title || "引导式模板实验");
const experimentDescription = computed(
  () => experiment.value?.description || "先配置参数与导入库，再应用到代码模板并继续运行/保存/提交。",
);
const isBusy = computed(() => isRunning.value || isSaving.value || isSubmitting.value || isPageLoading.value);

const isWorkspaceLocked = computed(() => Boolean(workspaceStatus.value?.is_locked));
const isOverdue = computed(() => Boolean(workspaceStatus.value?.is_overdue));
const allowEditGeneratedCode = computed(() => Boolean(experiment.value?.allow_edit_generated_code ?? true));
const canEdit = computed(() => Boolean(workspaceStatus.value?.can_edit ?? true) && !isOverdue.value && allowEditGeneratedCode.value);
const canSaveDraft = computed(() => Boolean(workspaceStatus.value?.can_save_draft ?? true) && !isOverdue.value);
const canSubmit = computed(() => Boolean(workspaceStatus.value?.can_submit ?? true) && !isOverdue.value);
const canRun = computed(() => Boolean(workspaceStatus.value?.can_run ?? true) && !isOverdue.value);
const canRestoreHistory = computed(() => canEdit.value && !isWorkspaceLocked.value && !isOverdue.value);
const isAccessRestricted = computed(() => Boolean(accessRestriction.value.blocked));
const hasEditorAccess = computed(() => !isAccessCheckLoading.value && !isAccessRestricted.value);
const canUseSubmissionFlow = computed(() => hasEditorAccess.value && !isAdminViewer.value);
const canTemplateActions = computed(() => hasEditorAccess.value && canEdit.value);
const hasEditorContent = computed(() => Boolean((currentCode.value || "").trim()));

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

const latestRunStatus = computed(() => runResult.value?.status || "-");
const latestRunDuration = computed(() =>
  typeof runResult.value?.execution_time_ms === "number" ? `${runResult.value.execution_time_ms} ms` : "-",
);
const currentVersionText = computed(() => (currentLoadedVersion.value ? `v${currentLoadedVersion.value}` : "-"));
const latestSavedVersionText = computed(() => (latestSavedVersion.value ? `v${latestSavedVersion.value}` : "-"));
const currentSubmissionStatusText = computed(() => {
  if (currentSubmissionStatus.value === "draft") return "draft";
  if (currentSubmissionStatus.value === "submitted") return "submitted";
  if (currentSubmissionStatus.value === "history") return "历史版本";
  return "unknown";
});
const accessRestrictionMessage = computed(() => accessRestriction.value.message || "当前实验暂不可访问");
const accessRestrictionTitle = computed(() => {
  if (accessRestriction.value.reason === "unpublished") return "当前实验未发布";
  if (accessRestriction.value.reason === "not-open") return "当前实验尚未开放";
  if (accessRestriction.value.reason === "mode-mismatch") return "实验模式不匹配";
  if (accessRestriction.value.reason === "template-config") return "该实验模板尚未配置完整";
  return "当前实验暂不可访问";
});
const workspaceMessage = computed(() => workspaceStatus.value?.message || "当前可继续编辑和保存草稿");
const workspaceStateText = computed(() => {
  if (!workspaceStatus.value?.is_published) return "未发布";
  if (!workspaceStatus.value?.is_open) return "未开放";
  if (workspaceStatus.value?.is_overdue) return "已截止";
  if (isWorkspaceLocked.value) return "已锁定";
  if (!allowEditGeneratedCode.value) return "只读";
  return "可编辑";
});

self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === "json") return new jsonWorker();
    if (label === "css" || label === "scss" || label === "less") return new cssWorker();
    if (label === "html" || label === "handlebars" || label === "razor") return new htmlWorker();
    if (label === "typescript" || label === "javascript") return new tsWorker();
    return new editorWorker();
  },
};

function createEditor() {
  if (!editorContainer.value || editorInstance) return;
  editorInstance = monaco.editor.create(editorContainer.value, {
    value: currentCode.value || "",
    language: "python",
    theme: "vs-dark",
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 15,
    lineNumbersMinChars: 3,
    scrollBeyondLastLine: false,
    padding: { top: 12, bottom: 12 },
  });
  editorInstance.onDidChangeModelContent(() => {
    if (isSyncingEditorValue) return;
    currentCode.value = editorInstance.getValue();
    hasUnsavedChanges.value = currentCode.value !== lastSavedCode.value;
  });
  syncEditorReadonly();
}

async function ensureEditorInitialized() {
  await nextTick();
  createEditor();
  if (!editorInstance) return;
  setEditorValue(currentCode.value || "");
  syncEditorReadonly();
}

function destroyEditor() {
  if (!editorInstance) return;
  editorInstance.dispose();
  editorInstance = null;
}

function syncEditorReadonly() {
  if (!editorInstance) return;
  editorInstance.updateOptions({ readOnly: !canEdit.value });
}

function setEditorValue(nextCode, options = {}) {
  const { markAsSaved = true } = options;
  const finalCode = nextCode || "";
  currentCode.value = finalCode;
  if (editorInstance && editorInstance.getValue() !== finalCode) {
    isSyncingEditorValue = true;
    editorInstance.setValue(finalCode);
    isSyncingEditorValue = false;
  }
  if (markAsSaved) {
    lastSavedCode.value = finalCode;
    hasUnsavedChanges.value = false;
  } else {
    hasUnsavedChanges.value = true;
  }
}

function formatTime(value) {
  return formatApiDateTime(value);
}

function parseVersion(value) {
  const version = Number(value);
  return Number.isInteger(version) && version > 0 ? version : null;
}

function updateWorkspaceStatus(payload) {
  workspaceStatus.value = {
    ...workspaceStatus.value,
    ...payload,
  };
  syncEditorReadonly();
}

function updateLoadedSubmissionMeta(record, fallbackStatus = "unknown") {
  const status = record?.status || fallbackStatus;
  const version = parseVersion(record?.version);
  currentSubmissionStatus.value = status;
  if (version) currentLoadedVersion.value = version;
}

function updateLatestSubmissionMeta(record) {
  const version = parseVersion(record?.version);
  if (version) latestSavedVersion.value = version;
}

function resolveAccessRestriction(experimentDetail, workspace, isAdminMode = false) {
  if (experimentDetail?.interaction_mode !== "guided_template") {
    return {
      blocked: true,
      reason: "mode-mismatch",
      message: "当前实验不是引导式模板模式",
    };
  }
  if (isAdminMode) {
    return { blocked: false, reason: "", message: "" };
  }
  if (workspace?.is_published === false || experimentDetail?.is_published === false) {
    return {
      blocked: true,
      reason: "unpublished",
      message: "当前实验未发布，请稍后再进入",
    };
  }
  if (workspace?.is_open === false) {
    return {
      blocked: true,
      reason: "not-open",
      message: "当前实验尚未开放，请在开放时间后进入",
    };
  }
  const openAtRaw = workspace?.open_at || experimentDetail?.open_at;
  if (openAtRaw) {
    const openAtDate = parseApiDateTime(openAtRaw);
    const openAt = openAtDate ? openAtDate.getTime() : Number.NaN;
    if (!Number.isNaN(openAt) && Date.now() < openAt) {
      return {
        blocked: true,
        reason: "not-open",
        message: "当前实验尚未开放，请在开放时间后进入",
      };
    }
  }
  return { blocked: false, reason: "", message: "" };
}

function normalizeOptionalImportToStatement(moduleName) {
  const raw = String(moduleName || "").trim();
  if (!raw) return "";
  if (raw.startsWith("import ") || raw.startsWith("from ")) return raw;
  const moduleNameNormalized = raw;
  if (moduleNameNormalized === "requests") return "import requests";
  if (moduleNameNormalized === "bs4") return "from bs4 import BeautifulSoup";
  if (moduleNameNormalized === "pandas") return "import pandas as pd";
  if (moduleNameNormalized === "numpy") return "import numpy as np";
  if (moduleNameNormalized === "matplotlib") return "import matplotlib.pyplot as plt";
  if (moduleNameNormalized === "seaborn") return "import seaborn as sns";
  return `import ${moduleNameNormalized}`;
}

function normalizeImportOption(item) {
  const raw = String(item || "").trim();
  if (!raw) return "";
  if (raw.startsWith("import ") || raw.startsWith("from ")) return raw;
  if (raw.startsWith("from bs4 import")) return "bs4";
  if (raw.startsWith("import requests")) return "requests";
  if (raw.startsWith("import pandas")) return "pandas";
  if (raw.startsWith("import numpy")) return "numpy";
  if (raw.startsWith("import matplotlib")) return "matplotlib";
  if (raw.startsWith("import seaborn")) return "seaborn";
  if (raw.startsWith("import ")) {
    return raw.replace(/^import\s+/, "").split(/\s+/)[0].split(".")[0];
  }
  if (raw.startsWith("from ")) {
    return raw.replace(/^from\s+/, "").split(/\s+/)[0].split(".")[0];
  }
  return raw;
}

function normalizeFixedImportEntry(item) {
  return normalizeOptionalImportToStatement(item);
}

function normalizeOptionalImportOption(item) {
  return normalizeImportOption(item);
}

function escapePyString(value) {
  const text = String(value ?? "");
  return text.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function escapePySingleQuoted(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

function toPythonDictLiteral(payload) {
  if (!payload || typeof payload !== "object") {
    return "{}";
  }
  const entries = Object.entries(payload);
  if (entries.length === 0) {
    return "{}";
  }
  const lines = ["{"];
  entries.forEach(([key, value], index) => {
    const suffix = index === entries.length - 1 ? "" : ",";
    lines.push(`    '${escapePySingleQuoted(key)}': '${escapePySingleQuoted(value)}'${suffix}`);
  });
  lines.push("}");
  return lines.join("\n");
}

function normalizeTemplateFieldOption(option) {
  if (option && typeof option === "object") {
    const value = String(option.value ?? "").trim();
    if (!value) {
      return null;
    }
    const label = String(option.label ?? value);
    const headers = option.headers && typeof option.headers === "object" ? option.headers : null;
    return { value, label, headers };
  }
  const value = String(option ?? "").trim();
  if (!value) {
    return null;
  }
  return { value, label: value, headers: null };
}

function normalizeTemplateField(field) {
  if (!field || typeof field !== "object") {
    return null;
  }
  const name = String(field.name ?? "").trim();
  if (!name) {
    return null;
  }
  const rawType = String(field.type ?? "text").trim().toLowerCase();
  const type = ["text", "number", "select", "password", "textarea"].includes(rawType) ? rawType : "text";
  const label = String(field.label ?? name).trim() || name;
  const placeholder = typeof field.placeholder === "string" ? field.placeholder.trim() : "";
  const options = type === "select" && Array.isArray(field.options) ? field.options.map(normalizeTemplateFieldOption).filter(Boolean) : [];
  const hasDefault = Object.prototype.hasOwnProperty.call(field, "default") && field.default !== null && field.default !== undefined;
  const numberMin = Number(field.min);
  const numberMax = Number(field.max);
  const numberStep = Number(field.step);
  let resolvedStep = Number.isFinite(numberStep) && numberStep > 0 ? numberStep : null;
  if (rawType === "number" && resolvedStep === null) {
    const candidates = [field.min, field.max, field.default];
    let maxDecimalPlaces = 0;
    for (const item of candidates) {
      if (item === null || item === undefined || item === "") {
        continue;
      }
      const text = String(item).trim();
      if (!text || /e/i.test(text)) {
        continue;
      }
      const dotIndex = text.indexOf(".");
      if (dotIndex < 0) {
        continue;
      }
      const decimalPart = text.slice(dotIndex + 1).replace(/0+$/, "");
      if (decimalPart.length > maxDecimalPlaces) {
        maxDecimalPlaces = decimalPart.length;
      }
    }
    resolvedStep = maxDecimalPlaces > 0 ? 10 ** -Math.min(maxDecimalPlaces, 6) : 1;
  }
  return {
    name,
    label,
    type,
    required: field.required === true,
    placeholder: placeholder || (type === "select" ? "请选择" : ""),
    options,
    hasDefault,
    defaultValue: hasDefault ? field.default : "",
    min: Number.isFinite(numberMin) ? numberMin : null,
    max: Number.isFinite(numberMax) ? numberMax : null,
    step: resolvedStep,
  };
}

function extractTemplateFields(schemaValue) {
  const schema = schemaValue && typeof schemaValue === "object" ? schemaValue : {};
  const rawFields = Array.isArray(schema.fields) ? schema.fields : [];
  return rawFields.map(normalizeTemplateField).filter(Boolean);
}

function resolveInputType(field) {
  if (field?.type === "number") return "number";
  return "text";
}

function isTemplatePasswordVisible(fieldName) {
  return Boolean(templatePasswordVisibleMap[String(fieldName || "")]);
}

function toggleTemplatePasswordVisibility(fieldName) {
  const key = String(fieldName || "");
  if (!key) return;
  templatePasswordVisibleMap[key] = !templatePasswordVisibleMap[key];
}

function resolveTemplateFieldDefaultValue(field) {
  if (!field?.hasDefault) {
    return "";
  }
  if (field.type === "number") {
    const defaultNumber = Number(field.defaultValue);
    return Number.isFinite(defaultNumber) ? String(defaultNumber) : "";
  }
  return String(field.defaultValue ?? "");
}

function resolveTemplateFieldRawValue(field) {
  if (!field?.name) {
    return "";
  }
  return templateForm[field.name];
}

function resolveTemplateFieldTextValue(field) {
  const rawValue = resolveTemplateFieldRawValue(field);
  return String(rawValue ?? "").trim();
}

function resolveHeadersBlock() {
  const userAgentField = templateFields.value.find((field) => field.name === "user_agent" && field.type === "select");
  if (!userAgentField) {
    return "{}";
  }
  const selectedValue = resolveTemplateFieldTextValue(userAgentField);
  const selected = userAgentField.options.find((item) => item.value === selectedValue);
  if (!selected || !selected.headers) {
    return "{}";
  }
  return toPythonDictLiteral(selected.headers);
}

function resolveSelectedUserAgentValue() {
  const userAgentField = templateFields.value.find((field) => field.name === "user_agent" && field.type === "select");
  if (!userAgentField) {
    return "";
  }
  const selectedValue = resolveTemplateFieldTextValue(userAgentField);
  const selected = userAgentField.options.find((item) => item.value === selectedValue);
  if (!selected || !selected.headers) {
    return selectedValue;
  }
  return String(selected.headers["User-Agent"] || selectedValue || "");
}

function getTemplateContent() {
  return originalTemplateCode.value || "";
}

function validateTemplateConfiguration(experimentDetail) {
  const schema = experimentDetail?.template_schema;
  if (!schema || typeof schema !== "object") {
    return { valid: false, message: "该实验模板尚未配置完整：缺少 template_schema" };
  }
  const fields = extractTemplateFields(schema);
  if (fields.length === 0) {
    return { valid: false, message: "该实验模板尚未配置完整：template_schema.fields 为空" };
  }
  const fieldNameSet = new Set();
  for (const field of fields) {
    if (fieldNameSet.has(field.name)) {
      return { valid: false, message: `该实验模板尚未配置完整：字段名重复（${field.name}）` };
    }
    fieldNameSet.add(field.name);
    if (field.type === "select" && field.options.length === 0) {
      return { valid: false, message: `该实验模板尚未配置完整：下拉字段 ${field.name} 缺少 options` };
    }
  }

  const codeTemplate = experimentDetail?.code_template;
  if (typeof codeTemplate !== "string" || !codeTemplate.trim()) {
    return { valid: false, message: "该实验模板尚未配置完整：缺少 code_template" };
  }
  if (/\{\{\s*headers_block\s*\}\}/.test(codeTemplate)) {
    const userAgentField = fields.find((field) => field.name === "user_agent" && field.type === "select");
    if (!userAgentField) {
      return { valid: false, message: "该实验模板尚未配置完整：headers_block 依赖 user_agent 下拉字段" };
    }
    if (!userAgentField.options.some((option) => option.headers && Object.keys(option.headers).length > 0)) {
      return { valid: false, message: "该实验模板尚未配置完整：user_agent 选项缺少 headers 映射" };
    }
  }

  const importConfig = experimentDetail?.import_config;
  if (!importConfig || typeof importConfig !== "object") {
    return { valid: false, message: "该实验模板尚未配置完整：缺少 import_config" };
  }
  if (!Array.isArray(importConfig.fixed_imports) || !Array.isArray(importConfig.optional_imports)) {
    return { valid: false, message: "该实验模板尚未配置完整：import_config 结构不正确" };
  }
  if (typeof importConfig.allow_custom_import !== "boolean") {
    return { valid: false, message: "该实验模板尚未配置完整：import_config.allow_custom_import 缺失" };
  }
  return { valid: true, message: "" };
}

function applyTemplateSchemaDefaults(schemaValue) {
  const fields = extractTemplateFields(schemaValue);
  templateFields.value = fields;
  Object.keys(templateForm).forEach((key) => {
    delete templateForm[key];
  });
  Object.keys(templatePasswordVisibleMap).forEach((key) => {
    delete templatePasswordVisibleMap[key];
  });
  for (const field of fields) {
    templateForm[field.name] = resolveTemplateFieldDefaultValue(field);
  }
}

function applyImportConfig(configValue) {
  const config = configValue && typeof configValue === "object" ? configValue : {};
  const fixed = Array.isArray(config.fixed_imports) ? config.fixed_imports.filter((item) => typeof item === "string" && item.trim()) : [];
  const optional = Array.isArray(config.optional_imports)
    ? config.optional_imports.filter((item) => typeof item === "string" && item.trim())
    : [];
  fixedImports.value = fixed.map(normalizeFixedImportEntry).filter(Boolean);
  optionalImports.value = optional.map(normalizeOptionalImportOption).filter(Boolean);
  allowCustomImport.value = config.allow_custom_import === true;
  selectedOptionalImports.value = [];
  customImportText.value = "";
}

async function buildImportStatements() {
  const merged = [];
  const seen = new Set();
  const pushUnique = (item) => {
    const value = (item || "").trim();
    if (!value || seen.has(value)) return;
    seen.add(value);
    merged.push(value);
  };
  fixedImports.value.forEach(pushUnique);
  selectedOptionalImports.value.forEach((name) => pushUnique(normalizeOptionalImportToStatement(name)));

  if (allowCustomImport.value && customImportText.value.trim()) {
    const lines = customImportText.value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    for (const line of lines) {
      if (!/^import\s+[a-zA-Z_][\w.]*([\s]+as[\s]+[a-zA-Z_]\w*)?$/.test(line) && !/^from\s+[a-zA-Z_][\w.]*\s+import\s+[\w*,\s]+$/.test(line)) {
        throw new Error(`自定义导入格式错误：${line}`);
      }
    }
    const validateResult = await validateGuidedTemplateImports(lines.join("\n"));
    if (!validateResult.valid) {
      throw new Error(validateResult.errors.join("；"));
    }
    validateResult.normalized_imports.forEach(pushUnique);
  }

  const allValidation = await validateGuidedTemplateImports(merged.join("\n"));
  if (!allValidation.valid) {
    throw new Error(allValidation.errors.join("；"));
  }
  return allValidation.normalized_imports;
}

function normalizeLegacyHeadersTemplate(templateCode) {
  let code = templateCode;
  const legacyPatterns = [
    /headers\s*=\s*\{\s*["']User-Agent["']\s*:\s*["']\{\{\s*headers_block\s*\}\}["']\s*,?\s*\}/g,
    /headers\s*=\s*\{\s*["']User-Agent["']\s*:\s*["']\{\{\s*user_agent\s*\}\}["']\s*,?\s*\}/g,
  ];
  for (const pattern of legacyPatterns) {
    code = code.replace(pattern, "headers = {{headers_block}}");
  }
  return code;
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
    return normalizeRunResult(snapshot);
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

function buildTemplateStateSnapshot() {
  const form = {};
  for (const field of templateFields.value) {
    form[field.name] = String(templateForm[field.name] ?? "");
  }
  return {
    form,
    selected_optional_imports: [...selectedOptionalImports.value],
    custom_import_text: allowCustomImport.value ? String(customImportText.value || "") : "",
  };
}

function applyTemplateStateSnapshot(snapshot) {
  if (!snapshot || typeof snapshot !== "object") {
    return;
  }
  const form = snapshot.form && typeof snapshot.form === "object" ? snapshot.form : {};
  for (const field of templateFields.value) {
    if (!Object.prototype.hasOwnProperty.call(form, field.name)) {
      continue;
    }
    const value = String(form[field.name] ?? "").trim();
    if (field.type === "select") {
      if (!value || field.options.some((item) => item.value === value)) {
        templateForm[field.name] = value;
      }
      continue;
    }
    templateForm[field.name] = value;
  }
  const nextOptional = Array.isArray(snapshot.selected_optional_imports) ? snapshot.selected_optional_imports : [];
  const optionalSet = new Set(optionalImports.value);
  selectedOptionalImports.value = nextOptional
    .map((item) => String(item || "").trim())
    .filter((item) => item && optionalSet.has(item));
  if (allowCustomImport.value) {
    customImportText.value = String(snapshot.custom_import_text || "");
  }
}

function restoreTemplateStateSnapshot() {
  if (!templateStateStorageKey.value || typeof window === "undefined") {
    return;
  }
  try {
    const raw = window.localStorage.getItem(templateStateStorageKey.value);
    if (!raw) {
      return;
    }
    const parsed = JSON.parse(raw);
    applyTemplateStateSnapshot(parsed?.state);
  } catch (_error) {
    // ignore storage parse errors
  }
}

function saveTemplateStateSnapshot(snapshot = buildTemplateStateSnapshot()) {
  if (!templateStateStorageKey.value || typeof window === "undefined" || !snapshot || typeof snapshot !== "object") {
    return;
  }
  try {
    window.localStorage.setItem(
      templateStateStorageKey.value,
      JSON.stringify({
        saved_at: new Date().toISOString(),
        state: snapshot,
      }),
    );
  } catch (_error) {
    // ignore storage write errors
  }
}

function ensureTemplateActionsAllowed() {
  if (canTemplateActions.value) {
    return true;
  }
  if (isOverdue.value) {
    templateError.value = "本实验已截止，当前不可再应用模板或修改代码。";
    return false;
  }
  if (isWorkspaceLocked.value) {
    templateError.value = "该实验已正式提交，当前代码已锁定，不能再加载/清空/恢复模板或应用参数。";
    return false;
  }
  templateError.value = "当前不可修改模板代码。";
  return false;
}

function escapeRegExp(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function replaceTemplateToken(sourceCode, key, value) {
  if (!key) {
    return sourceCode;
  }
  const pattern = new RegExp(`\\{\\{\\s*${escapeRegExp(key)}\\s*\\}\\}`, "g");
  return sourceCode.replace(pattern, value);
}

function hasAnyTemplateToken(sourceCode) {
  const text = String(sourceCode || "");
  if (!text) {
    return false;
  }
  const tokenKeys = ["imports", "headers_block", "user_agent", ...templateFields.value.map((field) => field.name)];
  return tokenKeys.some((key) => {
    const pattern = new RegExp(`\\{\\{\\s*${escapeRegExp(key)}\\s*\\}\\}`);
    return pattern.test(text);
  });
}

function serializeTemplateFieldValue(field, rawValue) {
  const textValue = String(rawValue ?? "").trim();
  if (!textValue) {
    return "";
  }
  if (field.type === "number") {
    const numericValue = Number(textValue);
    return Number.isFinite(numericValue) ? String(numericValue) : "";
  }
  return escapePyString(textValue);
}

function validateTemplateFormValues() {
  for (const field of templateFields.value) {
    const textValue = resolveTemplateFieldTextValue(field);
    if (field.required && !textValue) {
      throw new Error(`${field.label}不能为空`);
    }
    if (field.type === "number" && textValue) {
      const numericValue = Number(textValue);
      if (!Number.isFinite(numericValue)) {
        throw new Error(`${field.label}必须是数字`);
      }
      if (field.min !== null && numericValue < field.min) {
        throw new Error(`${field.label}不能小于 ${field.min}`);
      }
      if (field.max !== null && numericValue > field.max) {
        throw new Error(`${field.label}不能大于 ${field.max}`);
      }
    }
    if (field.type === "select" && textValue && field.options.length > 0 && !field.options.some((item) => item.value === textValue)) {
      throw new Error(`${field.label}选择值无效，请重新选择`);
    }
  }
}

function applyTemplateValue(templateCode, importStatements) {
  const importBlock = importStatements.join("\n");
  let code = normalizeLegacyHeadersTemplate(templateCode);
  for (const field of templateFields.value) {
    code = replaceTemplateToken(code, field.name, serializeTemplateFieldValue(field, resolveTemplateFieldRawValue(field)));
  }
  code = replaceTemplateToken(code, "headers_block", resolveHeadersBlock());
  code = replaceTemplateToken(code, "user_agent", escapePyString(resolveSelectedUserAgentValue()));
  if (/\{\{\s*imports\s*\}\}/.test(code)) {
    code = replaceTemplateToken(code, "imports", importBlock);
  } else {
    code = `${importBlock}\n\n${code}`;
  }
  return code;
}

async function applyTemplateToCode() {
  templateError.value = "";
  templateMessage.value = "";
  try {
    if (!ensureTemplateActionsAllowed()) {
      return;
    }
    validateTemplateFormValues();
    if (!hasEditorContent.value) {
      throw new Error("请先点击“加载骨架模板代码”或“恢复默认骨架模板代码”");
    }
    const imports = await buildImportStatements();
    let baseCode = currentCode.value;
    let useSkeletonFallback = false;
    if (!hasAnyTemplateToken(baseCode)) {
      const skeletonCode = getTemplateContent();
      if (!skeletonCode.trim()) {
        throw new Error("当前代码缺少模板占位符，且未找到可用骨架模板代码");
      }
      baseCode = skeletonCode;
      useSkeletonFallback = true;
    }
    const generatedCode = applyTemplateValue(baseCode, imports);
    setEditorValue(generatedCode, { markAsSaved: false });
    templateMessage.value = useSkeletonFallback
      ? "当前代码中未检测到模板占位符，已基于骨架模板重新应用参数。"
      : "参数与导入库已应用到代码，可继续手动修改后运行/保存/提交。";
  } catch (error) {
    templateError.value = error.message || "应用参数失败";
  }
}

function confirmBeforeTemplateOverride(confirmText) {
  if (!hasEditorContent.value) {
    return true;
  }
  return window.confirm(confirmText);
}

async function loadTemplateSkeleton() {
  templateError.value = "";
  templateMessage.value = "";
  if (!ensureTemplateActionsAllowed()) {
    return;
  }
  const nextCode = getTemplateContent();
  if (!nextCode.trim()) {
    templateError.value = "该实验模板尚未配置完整：未配置 code_template";
    return;
  }
  const shouldContinue = confirmBeforeTemplateOverride("当前编辑器已有代码，加载骨架模板会覆盖现有内容，是否继续？");
  if (!shouldContinue) {
    return;
  }
  setEditorValue(nextCode, { markAsSaved: false });
  templateMessage.value = "已加载骨架模板代码。";
}

async function clearEditorCode() {
  templateError.value = "";
  templateMessage.value = "";
  if (!ensureTemplateActionsAllowed()) {
    return;
  }
  const shouldContinue = confirmBeforeTemplateOverride("确认清空当前编辑器代码吗？此操作会覆盖现有内容。");
  if (!shouldContinue) {
    return;
  }
  setEditorValue("", { markAsSaved: false });
  templateMessage.value = "已清空编辑器代码。";
}

async function restoreDefaultSkeleton() {
  templateError.value = "";
  templateMessage.value = "";
  if (!ensureTemplateActionsAllowed()) {
    return;
  }
  const nextCode = getTemplateContent();
  if (!nextCode.trim()) {
    templateError.value = "该实验模板尚未配置完整：未配置 code_template";
    return;
  }
  const shouldContinue = confirmBeforeTemplateOverride("恢复默认骨架模板会覆盖当前编辑器内容，是否继续？");
  if (!shouldContinue) {
    return;
  }
  setEditorValue(nextCode, { markAsSaved: false });
  templateMessage.value = "已恢复默认骨架模板代码。";
}

async function refreshLatestAndHistory(options = {}) {
  const { updateLoadedFromLatest = false } = options;
  try {
    const workspace = await getWorkspaceStatus(experimentId.value);
    updateWorkspaceStatus(workspace);
  } catch (error) {
    message.value = `工作区状态同步失败：${error.message}`;
  }
  try {
    const latest = await getLatestSubmission(experimentId.value);
    updateLatestSubmissionMeta(latest);
    if (updateLoadedFromLatest) {
      updateLoadedSubmissionMeta(latest, latest?.status ? "unknown" : "draft");
    }
    const submissionRunResult = buildRunResultFromSubmission(latest);
    if (submissionRunResult && !hasRunnableResult(runResult.value)) {
      runResult.value = submissionRunResult;
      saveRunResultSnapshot(submissionRunResult);
    }
  } catch (error) {
    if (error.message.includes("暂无提交记录")) {
      latestSavedVersion.value = null;
      if (updateLoadedFromLatest) {
        currentLoadedVersion.value = null;
        currentSubmissionStatus.value = "unknown";
      }
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
}

async function loadExperimentAndCode() {
  runResult.value = null;
  historyList.value = [];
  historyError.value = "";
  showHistory.value = false;
  pageError.value = "";
  message.value = "";
  templateError.value = "";
  templateMessage.value = "";
  Object.keys(templateForm).forEach((key) => {
    delete templateForm[key];
  });
  templateFields.value = [];
  originalTemplateCode.value = "";
  fixedImports.value = [];
  optionalImports.value = [];
  allowCustomImport.value = false;
  selectedOptionalImports.value = [];
  customImportText.value = "";
  currentLoadedVersion.value = null;
  latestSavedVersion.value = null;
  currentSubmissionStatus.value = "unknown";
  accessRestriction.value = { blocked: false, reason: "", message: "" };
  updateWorkspaceStatus({
    experiment_id: experimentId.value,
    is_locked: false,
    is_published: true,
    is_open: true,
    is_overdue: false,
    latest_submission_id: null,
    latest_version: null,
    latest_status: null,
    can_edit: true,
    can_run: true,
    can_save_draft: true,
    can_submit: true,
    message: "当前可继续编辑和保存草稿",
  });

  if (!hasValidExperimentId.value) {
    pageError.value = "请先在实验列表中选择实验后再进入引导式模板实验";
    setEditorValue("");
    return;
  }

  isAccessCheckLoading.value = true;
  isPageLoading.value = true;
  try {
    const detail = await getExperimentById(experimentId.value);
    experiment.value = detail;
    if (detail.interaction_mode !== "guided_template") {
      router.replace(`/editor?experiment_id=${experimentId.value}`);
      return;
    }

    const templateConfigCheck = validateTemplateConfiguration(detail);
    if (!templateConfigCheck.valid) {
      accessRestriction.value = {
        blocked: true,
        reason: "template-config",
        message: templateConfigCheck.message || "该实验模板尚未配置完整",
      };
      setEditorValue("", { markAsSaved: true });
      message.value = accessRestriction.value.message;
      return;
    }

    originalTemplateCode.value = detail.code_template || "";
    applyTemplateSchemaDefaults(detail.template_schema);
    applyImportConfig(detail.import_config);
    restoreTemplateStateSnapshot();

    const workspace = await getWorkspaceStatus(experimentId.value);
    updateWorkspaceStatus(workspace);
    accessRestriction.value = resolveAccessRestriction(detail, workspace, isAdminViewer.value);

    if (accessRestriction.value.blocked) {
      setEditorValue("", { markAsSaved: true });
      message.value = accessRestriction.value.message;
      return;
    }

    let nextCode = "";
    let latestSubmission = null;
    try {
      const latest = await getLatestSubmission(experimentId.value);
      latestSubmission = latest;
      if (latest?.code) {
        nextCode = latest.code;
        updateLatestSubmissionMeta(latest);
        updateLoadedSubmissionMeta(latest, latest?.status ? "unknown" : "draft");
        message.value = "已加载最新保存代码";
      }
    } catch (error) {
      if (!error.message.includes("暂无提交记录")) {
        message.value = `最新代码加载失败：${error.message}，编辑器保持为空，请手动加载骨架模板`;
      }
    }

    if (!nextCode) {
      nextCode = "";
      message.value = "未检测到历史代码，请先点击“加载骨架模板代码”或“恢复默认骨架模板代码”。";
    }
    setEditorValue(nextCode, { markAsSaved: true });
    const restoredRunResult = restoreRunResultSnapshot();
    if (restoredRunResult) {
      runResult.value = restoredRunResult;
    } else if (latestSubmission) {
      const submissionRunResult = buildRunResultFromSubmission(latestSubmission);
      if (submissionRunResult) {
        runResult.value = submissionRunResult;
        saveRunResultSnapshot(submissionRunResult);
      }
    }
    if (hasRunnableResult(runResult.value) && !canRun.value) {
      message.value = `${message.value ? `${message.value}；` : ""}已恢复最近一次运行结果，可点击“查看运行结果”`;
    }
    if (isWorkspaceLocked.value && hasRunResult.value) {
      message.value = `${workspaceMessage.value}，可点击“查看运行结果”查看最近一次运行输出`;
    }
  } catch (error) {
    experiment.value = null;
    setEditorValue("");
    pageError.value = `实验加载失败：${error.message}`;
  } finally {
    isAccessCheckLoading.value = false;
    isPageLoading.value = false;
  }
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
  isSaving.value = true;
  message.value = "";
  const templateStateBeforeSave = buildTemplateStateSnapshot();
  try {
    const saved = await saveSubmission(buildSubmissionPayload());
    lastSavedCode.value = currentCode.value;
    hasUnsavedChanges.value = false;
    updateLoadedSubmissionMeta(saved, "draft");
    updateLatestSubmissionMeta(saved);
    await refreshLatestAndHistory({ updateLoadedFromLatest: true });
    applyTemplateStateSnapshot(templateStateBeforeSave);
    saveTemplateStateSnapshot(templateStateBeforeSave);
    message.value = `草稿保存成功，当前版本 ${currentVersionText.value}`;
  } catch (error) {
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
  isSubmitting.value = true;
  message.value = "";
  const templateStateBeforeSubmit = buildTemplateStateSnapshot();
  try {
    const submission = await submitSubmission(buildSubmissionPayload());
    lastSavedCode.value = currentCode.value;
    hasUnsavedChanges.value = false;
    updateLoadedSubmissionMeta(submission, "submitted");
    updateLatestSubmissionMeta(submission);
    await refreshLatestAndHistory({ updateLoadedFromLatest: true });
    applyTemplateStateSnapshot(templateStateBeforeSubmit);
    saveTemplateStateSnapshot(templateStateBeforeSubmit);
    message.value = `已正式提交，当前版本 ${currentVersionText.value}`;
  } catch (error) {
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

function isHistoryItemActive(item) {
  return parseVersion(item?.version) === currentLoadedVersion.value;
}

async function loadHistoryDetail(item) {
  if (!canRestoreHistory.value) {
    message.value = isOverdue.value ? "本实验已截止，当前不可恢复历史版本" : "当前不可恢复历史版本";
    return;
  }
  if (hasUnsavedChanges.value) {
    const confirmed = window.confirm("当前有未保存修改，恢复历史版本会覆盖当前代码，是否继续？");
    if (!confirmed) return;
  }
  historyDetailLoadingId.value = item.id;
  try {
    const detail = await getSubmissionDetail(item.id);
    if (typeof detail?.code === "string") {
      setEditorValue(detail.code, { markAsSaved: false });
      const submissionRunResult = buildRunResultFromSubmission(detail);
      if (submissionRunResult) {
        runResult.value = submissionRunResult;
        saveRunResultSnapshot(submissionRunResult);
      }
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
  if (!hasValidExperimentId.value) return;
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
    showHistory.value = false;
    destroyEditor();
  },
  { immediate: true },
);

watch(
  () => canEdit.value,
  () => {
    syncEditorReadonly();
  },
  { immediate: true },
);

const handleBeforeUnload = (event) => {
  if (!hasEditorAccess.value) return;
  if (!hasUnsavedChanges.value) return;
  event.preventDefault();
  event.returnValue = "";
};

onBeforeRouteLeave(() => {
  if (!hasEditorAccess.value) return true;
  if (!hasUnsavedChanges.value) return true;
  return window.confirm("当前有未保存修改，离开页面将丢失最新改动，是否继续离开？");
});

onMounted(() => {
  viewerRole.value = getStoredCurrentUser()?.role || localStorage.getItem("role") || "";
  ensureEditorInitialized();
  window.addEventListener("beforeunload", handleBeforeUnload);
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeunload", handleBeforeUnload);
  destroyEditor();
});
</script>

<style scoped>
.guided-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 16px;
}

.head-panel {
  display: grid;
  gap: 12px;
}

.head-main h2 {
  margin: 0;
  font-size: 24px;
}

.head-main p {
  margin: 8px 0 0;
  color: var(--text-subtle);
}

.head-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  border-top: 1px solid var(--border-soft);
  padding-top: 12px;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 9px 14px;
  font-weight: 700;
  cursor: pointer;
  color: var(--surface-1);
}

.btn.primary {
  background: var(--brand-600);
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

.btn.plain {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.state,
.info {
  color: var(--brand-800);
  background: var(--brand-soft);
  border-color: var(--brand-border);
}

.warn {
  color: var(--warn-strong);
  background: var(--warn-soft);
  border-color: var(--warn-border);
}

.error {
  color: var(--danger-strong);
  background: var(--danger-soft);
  border-color: var(--danger-border);
}

.params-panel h3 {
  margin: 0;
}

.params-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
  align-items: start;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
  font-family: inherit;
}

.field input:not([type="checkbox"]):not([type="radio"]),
.field select {
  height: 42px;
  min-height: 42px;
  padding: 0 10px;
  font-size: 15px;
  line-height: 1.2;
}

.field textarea {
  min-height: 120px;
  padding: 10px 12px;
  line-height: 1.5;
}

.password-input-wrap {
  position: relative;
  width: 100%;
}

.password-input-wrap input {
  padding-right: 44px;
}

.password-toggle {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  min-width: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-strong);
  border-radius: 6px;
  background: var(--surface-1);
  color: var(--text-strong);
  cursor: pointer;
  padding: 0;
  transition: none !important;
}

.password-toggle svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.password-toggle:hover,
.password-toggle:focus,
.password-toggle:active {
  transform: translateY(-50%) !important;
  transition: none !important;
}

.password-toggle:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.imports-wrap {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.import-box {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  background: var(--surface-3);
  padding: 10px;
}

.import-box h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.import-box ul {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 4px;
  font-size: 14px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  margin-bottom: 6px;
}

.hint {
  margin: 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.inline-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tips {
  margin: 8px 0 0;
  font-size: 14px;
}

.success-text {
  color: var(--success-strong);
}

.error-text {
  color: var(--danger-strong);
}

.history-panel {
  display: grid;
  gap: 10px;
}

.history-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-head h3 {
  margin: 0;
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
  opacity: 0.8;
}

.mini-label {
  color: var(--accent-indigo-strong);
  font-size: 13px;
  font-weight: 700;
}

.editor-panel {
  padding: 0 0 14px;
  overflow: hidden;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 14px 6px;
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
  margin: 0 14px 10px;
  color: var(--brand-800);
  background: var(--brand-soft-2);
  border: 1px solid var(--brand-border-strong);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  font-weight: 600;
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
  height: 520px;
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

@media (max-width: 980px) {
  .params-grid {
    grid-template-columns: 1fr;
  }

  .imports-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
