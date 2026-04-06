<template>
  <section class="placeholder-page">
    <article class="card">
      <h2>{{ experiment?.title || "引导式模板实验" }}</h2>
      <p class="desc">
        该实验将采用引导式模板模式，当前尚未开放。
      </p>
      <p v-if="experiment?.description" class="meta">实验简介：{{ experiment.description }}</p>
      <div class="actions">
        <RouterLink class="btn list" to="/experiments">返回实验列表</RouterLink>
        <RouterLink class="btn docs" :to="docsPath">查看实验说明</RouterLink>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { getExperimentById } from "../api/experiment";

const route = useRoute();
const experiment = ref(null);
const fallbackExperimentId = Number(import.meta.env.VITE_EXPERIMENT_ID);

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
const docsPath = computed(() => `/docs?experiment_id=${experimentId.value}`);

async function loadExperiment() {
  if (!experimentId.value) {
    experiment.value = null;
    return;
  }
  try {
    experiment.value = await getExperimentById(experimentId.value);
  } catch (error) {
    experiment.value = null;
  }
}

onMounted(() => {
  loadExperiment();
});
</script>

<style scoped>
.placeholder-page {
  display: grid;
  gap: 14px;
}

.card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 20px;
}

.card h2 {
  margin: 0;
}

.desc {
  margin: 10px 0 0;
  color: var(--text-body);
}

.meta {
  margin: 10px 0 0;
  color: var(--text-subtle);
  font-size: 14px;
}

.actions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  text-decoration: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-weight: 600;
  font-size: 14px;
}

.btn.list {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn.docs {
  background: var(--brand-soft-2);
  color: var(--brand-700);
}
</style>
