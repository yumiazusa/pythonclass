<template>
  <section class="admin-page">
    <article class="panel head-panel">
      <div class="head-row">
        <div>
          <h2>实验管理</h2>
          <p>管理原生模式实验，并为引导式模板模式预留占位配置。</p>
        </div>
        <RouterLink class="btn primary" to="/admin/experiments/new">新建实验</RouterLink>
      </div>
    </article>

    <article class="panel filter-panel">
      <div class="filters-grid">
        <label class="field">
          <span>关键词</span>
          <input v-model.trim="filters.keyword" type="text" placeholder="标题 / slug" />
        </label>
        <label class="field">
          <span>实验模式</span>
          <select v-model="filters.interaction_mode">
            <option value="all">全部</option>
            <option value="native_editor">原生模式</option>
            <option value="guided_template">引导式模板模式</option>
          </select>
        </label>
        <label class="field">
          <span>启用状态</span>
          <select v-model="filters.is_active">
            <option value="all">全部</option>
            <option value="enabled">启用</option>
            <option value="disabled">停用</option>
          </select>
        </label>
        <label class="field">
          <span>发布状态</span>
          <select v-model="filters.is_published">
            <option value="all">全部</option>
            <option value="published">已发布</option>
            <option value="unpublished">未发布</option>
          </select>
        </label>
        <label class="field">
          <span>排序字段</span>
          <select v-model="filters.sort_by">
            <option value="sort_order">排序号</option>
            <option value="updated_at">更新时间</option>
            <option value="created_at">创建时间</option>
            <option value="title">标题</option>
            <option value="slug">slug</option>
            <option value="open_at">开放时间</option>
            <option value="due_at">截止时间</option>
          </select>
        </label>
        <label class="field">
          <span>排序方向</span>
          <select v-model="filters.sort_order">
            <option value="asc">升序</option>
            <option value="desc">降序</option>
          </select>
        </label>
      </div>
      <div class="actions-row">
        <button type="button" class="btn primary" :disabled="isLoading" @click="handleSearch">查询</button>
        <button type="button" class="btn plain" :disabled="isLoading" @click="handleReset">重置</button>
      </div>
    </article>

    <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>
    <article v-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <article class="panel table-panel">
      <div class="table-meta">共 {{ pagination.total }} 条，当前第 {{ pagination.page }} / {{ totalPagesText }} 页</div>
      <p v-if="isLoading" class="hint">正在加载实验列表...</p>
      <p v-else-if="experiments.length === 0" class="hint">当前筛选条件下无实验数据</p>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="col-title">标题</th>
              <th>模式</th>
              <th>排序号</th>
              <th>启用</th>
              <th>发布</th>
              <th>开放时间</th>
              <th>截止时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in experiments" :key="item.experiment_id">
              <td class="title-cell">
                <span class="title-text">{{ item.title }}</span>
              </td>
              <td>{{ modeText(item.interaction_mode) }}</td>
              <td>{{ item.sort_order }}</td>
              <td>
                <span :class="['status-pill', item.is_active ? 'enabled' : 'disabled']">
                  {{ item.is_active ? "启用" : "停用" }}
                </span>
              </td>
              <td>
                <span :class="['status-pill', item.is_published ? 'published' : 'draft']">
                  {{ item.is_published ? "已发布" : "未发布" }}
                </span>
              </td>
              <td>{{ formatTime(item.open_at) }}</td>
              <td>{{ formatTime(item.due_at) }}</td>
              <td>
                <div class="row-actions">
                  <RouterLink class="btn mini plain" :to="`/admin/experiments/${item.experiment_id}/edit`">编辑</RouterLink>
                  <button type="button" class="btn mini copy" :disabled="isLoading" @click="handleCopyExperiment(item)">
                    复制
                  </button>
                  <button
                    v-if="!item.is_active"
                    type="button"
                    class="btn mini success"
                    :disabled="isLoading"
                    @click="handleToggleActive(item, true)"
                  >
                    启用
                  </button>
                  <button
                    v-else
                    type="button"
                    class="btn mini danger"
                    :disabled="isLoading"
                    @click="handleToggleActive(item, false)"
                  >
                    停用
                  </button>
                  <button type="button" class="btn mini danger" :disabled="isLoading" @click="handleDeleteExperiment(item)">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <div class="page-size">
          <span>每页</span>
          <select v-model.number="pagination.page_size" :disabled="isLoading" @change="handlePageSizeChange">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
        <div class="page-actions">
          <button type="button" class="btn plain" :disabled="isLoading || pagination.page <= 1" @click="goPrevPage">上一页</button>
          <span>第 {{ pagination.page }} / {{ totalPagesText }} 页</span>
          <button
            type="button"
            class="btn plain"
            :disabled="isLoading || pagination.page >= pagination.total_pages || pagination.total_pages === 0"
            @click="goNextPage"
          >
            下一页
          </button>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import {
  copyAdminExperiment,
  deleteAdminExperiment,
  disableAdminExperiment,
  enableAdminExperiment,
  getAdminExperiments,
} from "../api/admin";
import { formatApiDateTime } from "../utils/datetime";

const experiments = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);

const filters = reactive({
  keyword: "",
  interaction_mode: "all",
  is_active: "all",
  is_published: "all",
  sort_by: "sort_order",
  sort_order: "asc",
});

const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
});

const totalPagesText = computed(() => (pagination.value.total_pages > 0 ? pagination.value.total_pages : 1));

function modeText(mode) {
  return mode === "guided_template" ? "引导式模板模式" : "原生模式";
}

function formatTime(value) {
  return formatApiDateTime(value);
}

function buildQueryParams() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.page_size,
    keyword: filters.keyword,
    interaction_mode: filters.interaction_mode,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
  };
  if (filters.is_active === "enabled") {
    params.is_active = true;
  } else if (filters.is_active === "disabled") {
    params.is_active = false;
  }
  if (filters.is_published === "published") {
    params.is_published = true;
  } else if (filters.is_published === "unpublished") {
    params.is_published = false;
  }
  return params;
}

async function loadExperiments() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await getAdminExperiments(buildQueryParams());
    experiments.value = data.items || [];
    pagination.value.total = data.total || 0;
    pagination.value.total_pages = data.total_pages || 0;
    pagination.value.page = data.page || pagination.value.page;
    pagination.value.page_size = data.page_size || pagination.value.page_size;
  } catch (error) {
    errorMessage.value = `实验列表加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

function handleSearch() {
  pagination.value.page = 1;
  loadExperiments();
}

function handleReset() {
  filters.keyword = "";
  filters.interaction_mode = "all";
  filters.is_active = "all";
  filters.is_published = "all";
  filters.sort_by = "sort_order";
  filters.sort_order = "asc";
  pagination.value.page = 1;
  loadExperiments();
}

function handlePageSizeChange() {
  pagination.value.page = 1;
  loadExperiments();
}

function goPrevPage() {
  if (pagination.value.page <= 1) {
    return;
  }
  pagination.value.page -= 1;
  loadExperiments();
}

function goNextPage() {
  if (pagination.value.total_pages === 0 || pagination.value.page >= pagination.value.total_pages) {
    return;
  }
  pagination.value.page += 1;
  loadExperiments();
}

async function handleToggleActive(item, targetEnabled) {
  actionMessage.value = "";
  actionError.value = false;
  const actionText = targetEnabled ? "启用" : "停用";
  const confirmed = window.confirm(`确认${actionText}实验「${item.title}」吗？`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    if (targetEnabled) {
      await enableAdminExperiment(item.experiment_id);
    } else {
      await disableAdminExperiment(item.experiment_id);
    }
    actionMessage.value = `${actionText}成功：${item.title}`;
    await loadExperiments();
  } catch (error) {
    actionMessage.value = `${actionText}失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleCopyExperiment(item) {
  actionMessage.value = "";
  actionError.value = false;
  const confirmed = window.confirm(`确认复制实验「${item.title}」吗？系统会创建一个未发布的副本。`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    const copied = await copyAdminExperiment(item.experiment_id);
    actionMessage.value = `复制成功：${copied.title}（slug: ${copied.slug}）`;
    await loadExperiments();
  } catch (error) {
    actionMessage.value = `复制失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleDeleteExperiment(item) {
  actionMessage.value = "";
  actionError.value = false;
  const confirmed = window.confirm(
    `确认删除实验「${item.title}」吗？\n该实验下的提交记录也会被一起删除，此操作不可恢复。`,
  );
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    await deleteAdminExperiment(item.experiment_id);
    if (experiments.value.length === 1 && pagination.value.page > 1) {
      pagination.value.page -= 1;
    }
    actionMessage.value = `删除成功：${item.title}`;
    await loadExperiments();
  } catch (error) {
    actionMessage.value = `删除失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadExperiments();
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.head-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.head-panel h2 {
  margin: 0;
}

.head-panel p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  font-size: 14px;
  color: var(--text-muted);
}

.field input,
.field select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
}

.actions-row {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.table-meta {
  color: var(--text-muted);
  font-size: 14px;
}

.table-wrap {
  margin-top: 10px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--border-soft);
  padding: 11px 8px;
  text-align: left;
  font-size: 14px;
  line-height: 1.45;
  white-space: normal;
  word-break: break-word;
}

.col-title {
  width: 18%;
  min-width: 160px;
}

.title-cell {
  max-width: 250px;
}

.title-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.45;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 9px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  border: 1px solid transparent;
}

.status-pill::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.9;
}

.status-pill.enabled {
  background: var(--success-soft);
  border-color: var(--success-border);
  color: var(--success-strong);
}

.status-pill.disabled {
  background: var(--danger-soft);
  border-color: var(--danger-border);
  color: var(--danger-strong);
}

.status-pill.published {
  background: var(--brand-soft);
  border-color: var(--brand-border);
  color: var(--brand-700);
}

.status-pill.draft {
  background: var(--surface-2);
  border-color: var(--border-soft);
  color: var(--text-muted);
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  align-items: center;
  white-space: nowrap;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.btn.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.plain {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn.success {
  background: var(--success-strong);
  color: var(--surface-1);
}

.btn.info {
  background: var(--accent-cyan-strong);
  color: var(--surface-1);
}

.btn.copy {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.danger {
  background: var(--danger-strong);
  color: var(--surface-1);
}

.btn.mini {
  padding: 6px 10px;
  font-size: 13px;
  line-height: 1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  margin: 10px 0 0;
  color: var(--text-subtle);
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-size {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 6px 8px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.success {
  border-color: var(--success-border);
  background: var(--success-soft);
  color: var(--success-strong);
}

@media (max-width: 960px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
