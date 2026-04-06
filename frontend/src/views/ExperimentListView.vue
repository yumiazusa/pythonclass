<template>
  <section class="experiments-page">
    <div class="header-card">
      <h2>实验列表</h2>
      <p>请选择一个实验进入编辑器，或先查看实验说明。</p>
    </div>

    <div v-if="isLoading" class="state-card">正在加载实验列表...</div>
    <div v-else-if="errorMessage" class="state-card error">{{ errorMessage }}</div>
    <template v-else>
      <div v-if="warningMessage" class="state-card warn">{{ warningMessage }}</div>
      <div v-if="experiments.length === 0 || visibleExperiments.length === 0" class="state-card">暂无可用实验</div>
      <div v-else class="list-wrap">
        <article v-for="item in visibleExperiments" :key="item.id" class="exp-card">
          <div class="exp-head">
            <h3>{{ item.title }}</h3>
            <div class="tag-row">
              <span :class="['active-tag', item.is_active ? 'on' : 'off']">
                {{ item.is_active ? "启用中" : "未启用" }}
              </span>
              <span :class="['publish-tag', getExperimentScheduleState(item).key]">
                {{ getExperimentScheduleState(item).label }}
              </span>
              <span :class="['mode-tag', item.interaction_mode === 'guided_template' ? 'guided' : 'native']">
                {{ item.interaction_mode === "guided_template" ? "引导式模板" : "原生模式" }}
              </span>
            </div>
          </div>
          <p class="desc">{{ item.description || "暂无实验描述" }}</p>
          <p class="meta">开放时间：{{ formatTime(item.open_at) }}</p>
          <p class="meta">截止时间：{{ formatTime(item.due_at) }}</p>
          <p class="meta">更新时间：{{ formatTime(item.updated_at) }}</p>
          <div class="actions">
            <RouterLink v-if="canEnterExperiment(item)" class="btn enter" :to="getEnterPath(item)">
              进入实验
            </RouterLink>
            <button v-else type="button" class="btn enter disabled" @click="handleEnterBlocked(item)">
              {{ getBlockedButtonText(item) }}
            </button>
            <RouterLink class="btn docs" :to="`/docs?experiment_id=${item.id}`">查看说明</RouterLink>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getExperiments } from "../api/experiment";
import { formatApiDateTime, parseApiDateTime } from "../utils/datetime";

const experiments = ref([]);
const isLoading = ref(true);
const errorMessage = ref("");
const visibleExperiments = ref([]);
const warningMessage = ref("");

function formatTime(value) {
  return formatApiDateTime(value);
}

function getExperimentScheduleState(item) {
  const now = Date.now();
  const openAtDate = parseApiDateTime(item?.open_at);
  const dueAtDate = parseApiDateTime(item?.due_at);
  const openAt = openAtDate ? openAtDate.getTime() : null;
  const dueAt = dueAtDate ? dueAtDate.getTime() : null;
  if (!item?.is_published) {
    return { key: "unpublished", label: "未发布" };
  }
  if (typeof openAt === "number" && !Number.isNaN(openAt) && now < openAt) {
    return { key: "not-open", label: "尚未开放" };
  }
  if (typeof dueAt === "number" && !Number.isNaN(dueAt) && now > dueAt) {
    return { key: "overdue", label: "已截止" };
  }
  return { key: "open", label: "进行中" };
}

function canEnterExperiment(item) {
  const state = getExperimentScheduleState(item);
  return state.key !== "unpublished" && state.key !== "not-open";
}

function getEnterPath(item) {
  if (item?.interaction_mode === "guided_template") {
    return `/guided-experiment?experiment_id=${item.id}`;
  }
  return `/editor?experiment_id=${item.id}`;
}

function getBlockedButtonText(item) {
  const state = getExperimentScheduleState(item);
  if (state.key === "unpublished") {
    return "未发布";
  }
  if (state.key === "not-open") {
    return "未开放";
  }
  return "暂不可进入";
}

function handleEnterBlocked(item) {
  warningMessage.value = "";
  const state = getExperimentScheduleState(item);
  if (state.key === "unpublished") {
    warningMessage.value = "当前实验未发布，请稍后再进入";
    return;
  }
  if (state.key === "not-open") {
    warningMessage.value = "当前实验尚未开放，请在开放时间后进入";
    return;
  }
  warningMessage.value = `当前实验${state.label}，请稍后再进入`;
}

async function loadExperiments() {
  isLoading.value = true;
  errorMessage.value = "";
  warningMessage.value = "";
  try {
    experiments.value = await getExperiments();
    visibleExperiments.value = experiments.value.filter((item) => item?.is_published);
  } catch (error) {
    errorMessage.value = `加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadExperiments();
});
</script>

<style scoped>
.experiments-page {
  display: grid;
  gap: 14px;
}

.header-card,
.state-card,
.exp-card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.header-card h2 {
  margin: 0;
}

.header-card p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.state-card {
  color: var(--text-body);
}

.state-card.error {
  border-color: var(--danger-border);
  color: var(--danger-strong);
  background: var(--danger-soft);
}

.state-card.warn {
  border-color: var(--warn-border);
  color: var(--warn-strong);
  background: var(--warn-soft);
}

.list-wrap {
  display: grid;
  gap: 12px;
}

.exp-card {
  display: grid;
  gap: 10px;
}

.exp-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exp-head h3 {
  margin: 0;
}

.active-tag {
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
}

.active-tag.on {
  background: var(--success-soft);
  color: var(--success-strong);
}

.active-tag.off {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.publish-tag {
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
}

.publish-tag.open {
  background: var(--success-soft);
  color: var(--success-strong);
}

.publish-tag.not-open {
  background: var(--brand-soft-2);
  color: var(--accent-indigo-strong);
}

.publish-tag.overdue {
  background: var(--warn-soft);
  color: var(--warn-strong);
}

.publish-tag.unpublished {
  background: var(--surface-2);
  color: var(--text-muted);
}

.mode-tag {
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  padding: 4px 10px;
}

.mode-tag.native {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

.mode-tag.guided {
  background: var(--warn-soft);
  color: var(--warn-strong);
}

.desc {
  margin: 0;
  color: var(--text-body);
}

.meta {
  margin: 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-weight: 600;
  font-size: 14px;
}

.btn.enter {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.docs {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}

.btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .exp-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .tag-row {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .exp-card {
    padding: 14px;
  }

  .actions {
    display: grid;
    gap: 8px;
  }

  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
