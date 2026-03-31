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

const experiments = ref([]);
const isLoading = ref(true);
const errorMessage = ref("");
const visibleExperiments = ref([]);
const warningMessage = ref("");

function formatTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", { hour12: false });
}

function getExperimentScheduleState(item) {
  const now = Date.now();
  const openAt = item?.open_at ? new Date(item.open_at).getTime() : null;
  const dueAt = item?.due_at ? new Date(item.due_at).getTime() : null;
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
  background: #fff;
  border: 1px solid #e5e8f0;
  border-radius: 12px;
  padding: 18px;
}

.header-card h2 {
  margin: 0;
}

.header-card p {
  margin: 8px 0 0;
  color: #4b5563;
}

.state-card {
  color: #374151;
}

.state-card.error {
  border-color: #fecaca;
  color: #b91c1c;
  background: #fef2f2;
}

.state-card.warn {
  border-color: #fdba74;
  color: #9a3412;
  background: #fff7ed;
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
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
}

.active-tag.on {
  background: #dcfce7;
  color: #166534;
}

.active-tag.off {
  background: #fee2e2;
  color: #991b1b;
}

.publish-tag {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
}

.publish-tag.open {
  background: #dcfce7;
  color: #166534;
}

.publish-tag.not-open {
  background: #e0e7ff;
  color: #3730a3;
}

.publish-tag.overdue {
  background: #fef3c7;
  color: #92400e;
}

.publish-tag.unpublished {
  background: #f3f4f6;
  color: #4b5563;
}

.mode-tag {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
}

.mode-tag.native {
  background: #dbeafe;
  color: #1d4ed8;
}

.mode-tag.guided {
  background: #fef3c7;
  color: #92400e;
}

.desc {
  margin: 0;
  color: #374151;
}

.meta {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
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
  background: #2563eb;
  color: #fff;
}

.btn.docs {
  background: #e0e7ff;
  color: #1d4ed8;
}

.btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .actions {
    flex-direction: column;
  }
}
</style>
