<template>
  <section class="docs-page">
    <article class="card top-card">
      <div class="top-row">
        <div>
          <h2>技术文档中心</h2>
          <p>支持分类浏览、关键词搜索与 Markdown 展示。</p>
        </div>
        <div class="actions">
          <RouterLink class="btn list" :to="backListPath">返回实验列表</RouterLink>
          <RouterLink v-if="hasValidExperimentId && canEnterEditor" class="btn editor" :to="enterTargetPath">
            返回编辑页
          </RouterLink>
          <span v-else-if="hasValidExperimentId" class="hint">{{ editorAccessHint }}</span>
        </div>
      </div>

      <form class="search-row" @submit.prevent="handleSearch">
        <input v-model.trim="keyword" type="text" placeholder="搜索文档标题/摘要/正文" />
        <select v-model="categoryFilter">
          <option value="all">全部分类</option>
          <option v-for="item in categories" :key="item" :value="item">{{ item }}</option>
        </select>
        <button type="submit" :disabled="isLoadingList">搜索</button>
      </form>
    </article>

    <article class="card docs-layout">
      <aside class="doc-sidebar">
        <h3>文档目录</h3>
        <p v-if="isLoadingList" class="side-hint">正在加载文档列表...</p>
        <p v-else-if="listError" class="side-hint error">{{ listError }}</p>
        <p v-else-if="catalogGroups.length === 0" class="side-hint">暂无文档</p>

        <div v-else class="tree-wrap">
          <section v-for="group in catalogGroups" :key="group.title" class="tree-group">
            <h4>{{ group.title }}</h4>
            <ul>
              <li v-for="item in group.items" :key="item.key">
                <button
                  type="button"
                  :class="['tree-item', selectedKey === item.key ? 'active' : '']"
                  @click="selectItem(item)"
                >
                  {{ item.title }}
                </button>
              </li>
            </ul>
          </section>
        </div>
      </aside>

      <main class="doc-content">
        <header class="doc-head">
          <h3>{{ currentTitle }}</h3>
          <span class="doc-meta">{{ currentMeta }}</span>
        </header>

        <p v-if="detailError" class="content-error">{{ detailError }}</p>
        <p v-else-if="isLoadingDetail" class="content-hint">正在加载文档内容...</p>
        <article v-else class="markdown-body" v-html="renderedHtml"></article>
      </main>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js/lib/core";
import pythonLang from "highlight.js/lib/languages/python";
import javascriptLang from "highlight.js/lib/languages/javascript";
import sqlLang from "highlight.js/lib/languages/sql";
import "highlight.js/styles/github.css";

import { getStoredCurrentUser } from "../api/auth";
import { getDocBySlug, getDocCategories, getDocs } from "../api/docs";
import { getExperimentById } from "../api/experiment";
import { formatApiDateTime, parseApiDateTime } from "../utils/datetime";

hljs.registerLanguage("python", pythonLang);
hljs.registerLanguage("javascript", javascriptLang);
hljs.registerLanguage("sql", sqlLang);

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(code, { language: lang }).value}</code></pre>`;
      } catch (error) {
        return `<pre class="hljs"><code>${md.utils.escapeHtml(code)}</code></pre>`;
      }
    }
    return `<pre class="hljs"><code>${hljs.highlightAuto(code).value}</code></pre>`;
  },
});

const route = useRoute();
const fallbackExperimentId = Number(import.meta.env.VITE_EXPERIMENT_ID);
const viewerRole = ref(getStoredCurrentUser()?.role || localStorage.getItem("role") || "");

const keyword = ref("");
const categoryFilter = ref("all");
const categories = ref([]);

const docs = ref([]);
const isLoadingList = ref(false);
const listError = ref("");

const selectedKey = ref("");
const selectedSlug = ref("");
const isExperimentSelected = ref(false);

const docDetail = ref(null);
const isLoadingDetail = ref(false);
const detailError = ref("");

const experiment = ref(null);
const isExperimentLoading = ref(false);
const experimentError = ref("");

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
const isAdminViewer = computed(() => viewerRole.value === "admin");
const backListPath = computed(() => (isAdminViewer.value ? "/admin/experiments" : "/experiments"));

const catalogGroups = computed(() => {
  const groups = [];

  if (hasValidExperimentId.value) {
    groups.push({
      title: "当前实验",
      items: [{ key: "experiment-current", title: experiment.value?.title ? `实验说明：${experiment.value.title}` : "当前实验说明" }],
    });
  }

  const bucket = new Map();
  docs.value.forEach((item) => {
    const category = item.category || "未分类";
    if (!bucket.has(category)) {
      bucket.set(category, []);
    }
    bucket.get(category).push({ key: `doc:${item.slug}`, title: item.title, slug: item.slug });
  });

  Array.from(bucket.keys()).forEach((category) => {
    groups.push({ title: category, items: bucket.get(category) || [] });
  });

  return groups;
});

const renderedHtml = computed(() => {
  if (isExperimentSelected.value) {
    if (experimentError.value) {
      return md.render(`# 实验说明加载失败\n\n${experimentError.value}`);
    }
    if (isExperimentLoading.value) {
      return md.render("# 正在加载实验说明\n\n请稍候...");
    }
    const title = experiment.value?.title || "当前实验说明";
    const body = experiment.value?.instruction_content || experiment.value?.description || "暂无说明内容";
    return md.render(`# ${title}\n\n${body}`);
  }

  if (detailError.value) {
    return md.render(`# 文档加载失败\n\n${detailError.value}`);
  }
  if (isLoadingDetail.value) {
    return md.render("# 正在加载文档内容\n\n请稍候...");
  }
  if (!docDetail.value) {
    return md.render("# 欢迎使用技术文档中心\n\n请从左侧选择文档。\n");
  }
  return md.render(docDetail.value.content || "暂无文档内容");
});

const currentTitle = computed(() => {
  if (isExperimentSelected.value) {
    return experiment.value?.title ? `当前实验：${experiment.value.title}` : "当前实验说明";
  }
  return docDetail.value?.title || "技术文档";
});

const currentMeta = computed(() => {
  const value = isExperimentSelected.value ? experiment.value?.updated_at : docDetail.value?.updated_at;
  return value ? `更新时间：${formatTime(value)}` : "";
});

const canEnterEditor = computed(() => {
  if (!experiment.value) {
    return false;
  }
  if (isAdminViewer.value) {
    return true;
  }
  if (!experiment.value.is_published) {
    return false;
  }
  if (experiment.value.open_at) {
    const openAtDate = parseApiDateTime(experiment.value.open_at);
    const openAtTime = openAtDate ? openAtDate.getTime() : Number.NaN;
    if (!Number.isNaN(openAtTime) && Date.now() < openAtTime) {
      return false;
    }
  }
  return true;
});

const editorAccessHint = computed(() => {
  if (!experiment.value) {
    return "实验信息加载后可判断编辑入口";
  }
  if (isAdminViewer.value) {
    return "";
  }
  if (!experiment.value.is_published) {
    return "当前实验未发布，暂不可返回编辑页";
  }
  if (experiment.value.open_at) {
    const openAtDate = parseApiDateTime(experiment.value.open_at);
    const openAtTime = openAtDate ? openAtDate.getTime() : Number.NaN;
    if (!Number.isNaN(openAtTime) && Date.now() < openAtTime) {
      return "当前实验尚未开放，请在开放时间后进入编辑页";
    }
  }
  return "";
});

const enterTargetPath = computed(() => {
  if (!hasValidExperimentId.value) {
    return "/experiments";
  }
  if (experiment.value?.interaction_mode === "guided_template") {
    return `/guided-experiment?experiment_id=${experimentId.value}`;
  }
  return `/editor?experiment_id=${experimentId.value}`;
});

function formatTime(value) {
  return formatApiDateTime(value);
}

function selectItem(item) {
  selectedKey.value = item.key;
  if (item.key === "experiment-current") {
    isExperimentSelected.value = true;
    selectedSlug.value = "";
    return;
  }
  isExperimentSelected.value = false;
  selectedSlug.value = item.slug || "";
  loadDocDetail();
}

async function loadCategories() {
  try {
    categories.value = await getDocCategories();
  } catch (error) {
    categories.value = [];
  }
}

async function loadDocsList() {
  isLoadingList.value = true;
  listError.value = "";
  try {
    const params = {
      keyword: keyword.value,
      category: categoryFilter.value === "all" ? "" : categoryFilter.value,
    };
    docs.value = await getDocs(params);

    const hasCurrentSelected = docs.value.some((item) => `doc:${item.slug}` === selectedKey.value);
    if (!selectedKey.value) {
      if (hasValidExperimentId.value) {
        selectedKey.value = "experiment-current";
        isExperimentSelected.value = true;
      } else if (docs.value.length > 0) {
        selectedKey.value = `doc:${docs.value[0].slug}`;
        selectedSlug.value = docs.value[0].slug;
        isExperimentSelected.value = false;
      }
    } else if (!isExperimentSelected.value && !hasCurrentSelected) {
      if (docs.value.length > 0) {
        selectedKey.value = `doc:${docs.value[0].slug}`;
        selectedSlug.value = docs.value[0].slug;
      } else {
        selectedKey.value = hasValidExperimentId.value ? "experiment-current" : "";
        selectedSlug.value = "";
        isExperimentSelected.value = hasValidExperimentId.value;
      }
    }

    if (!isExperimentSelected.value && selectedSlug.value) {
      await loadDocDetail();
    }
  } catch (error) {
    listError.value = error.message || "文档列表加载失败";
    docs.value = [];
  } finally {
    isLoadingList.value = false;
  }
}

async function loadDocDetail() {
  docDetail.value = null;
  detailError.value = "";
  if (!selectedSlug.value) {
    return;
  }
  isLoadingDetail.value = true;
  try {
    docDetail.value = await getDocBySlug(selectedSlug.value);
  } catch (error) {
    detailError.value = error.message || "文档详情加载失败";
  } finally {
    isLoadingDetail.value = false;
  }
}

async function loadExperiment() {
  experiment.value = null;
  experimentError.value = "";
  if (!hasValidExperimentId.value) {
    return;
  }
  isExperimentLoading.value = true;
  try {
    experiment.value = await getExperimentById(experimentId.value);
  } catch (error) {
    experimentError.value = error.message || "实验信息加载失败";
  } finally {
    isExperimentLoading.value = false;
  }
}

async function handleSearch() {
  await loadDocsList();
}

watch(
  () => experimentId.value,
  async () => {
    if (hasValidExperimentId.value) {
      selectedKey.value = "experiment-current";
      isExperimentSelected.value = true;
      selectedSlug.value = "";
    } else if (selectedKey.value === "experiment-current") {
      selectedKey.value = "";
      isExperimentSelected.value = false;
    }
    await loadExperiment();
    await loadDocsList();
  },
  { immediate: true },
);

onMounted(async () => {
  viewerRole.value = getStoredCurrentUser()?.role || localStorage.getItem("role") || "";
  await loadCategories();
});
</script>

<style scoped>
.docs-page {
  display: grid;
  gap: 14px;
}

.card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 16px;
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.top-row h2 {
  margin: 0;
}

.top-row p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.btn {
  text-decoration: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-weight: 600;
  font-size: 14px;
}

.btn.list {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

.btn.editor {
  background: var(--success-soft);
  color: var(--success-strong);
}

.hint {
  color: var(--warn-strong);
  font-size: 14px;
}

.search-row {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 180px 120px;
  gap: 10px;
}

.search-row input,
.search-row select,
.search-row button {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
}

.search-row button {
  background: var(--brand-600);
  color: var(--surface-1);
  font-weight: 600;
  cursor: pointer;
}

.docs-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 14px;
  min-height: 65vh;
  max-height: 75vh;
}

.doc-sidebar {
  overflow-y: auto;
  border-right: 1px solid var(--border-soft);
  padding-right: 10px;
}

.doc-sidebar h3 {
  margin: 0 0 10px;
}

.side-hint {
  color: var(--text-subtle);
  font-size: 14px;
}

.side-hint.error {
  color: var(--danger-strong);
}

.tree-wrap {
  display: grid;
  gap: 12px;
}

.tree-group h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--text-body);
}

.tree-group ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 6px;
}

.tree-item {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  background: var(--surface-1);
  color: var(--text-body);
  padding: 8px 10px;
  cursor: pointer;
  font-size: 14px;
  line-height: 1.4;
}

.tree-item:hover {
  border-color: var(--brand-border-strong);
  background: var(--brand-soft);
}

.tree-item.active {
  border-color: var(--brand-600);
  background: var(--brand-soft);
  color: var(--brand-700);
  font-weight: 600;
}

.doc-content {
  overflow-y: auto;
  padding-right: 8px;
}

.doc-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  border-bottom: 1px solid var(--border-soft);
  padding-bottom: 10px;
  margin-bottom: 12px;
}

.doc-head h3 {
  margin: 0;
}

.doc-meta {
  color: var(--text-subtle);
  font-size: 14px;
}

.content-error {
  color: var(--danger-strong);
}

.content-hint {
  color: var(--text-subtle);
}

.markdown-body {
  color: var(--text-strong);
  line-height: 1.75;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  line-height: 1.35;
  margin: 1em 0 0.5em;
}

.markdown-body :deep(p) {
  margin: 0.7em 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
}

.markdown-body :deep(pre) {
  border-radius: 10px;
  padding: 12px;
  overflow-x: auto;
  border: 1px solid var(--border-soft);
}

.markdown-body :deep(code) {
  font-family: var(--font-mono);
  font-size: 14px;
}

@media (max-width: 980px) {
  .search-row {
    grid-template-columns: 1fr;
  }

  .docs-layout {
    grid-template-columns: 1fr;
    min-height: auto;
    max-height: none;
  }

  .doc-sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--border-soft);
    padding-right: 0;
    padding-bottom: 10px;
    max-height: none;
    overflow-y: visible;
  }

  .doc-content {
    max-height: none;
    overflow-y: visible;
  }
}
</style>
