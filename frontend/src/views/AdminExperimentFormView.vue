<template>
  <section class="form-page">
    <article class="panel head-panel">
      <h2>{{ isEditMode ? "编辑实验" : "新建实验" }}</h2>
      <p>支持原生模式与引导式模板模式配置，guided_template 由数据库字段驱动。</p>
    </article>

    <article v-if="errorMessage" class="panel error">{{ errorMessage }}</article>
    <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>

    <article class="panel">
      <div class="form-grid">
        <label class="field">
          <span>标题</span>
          <input v-model.trim="form.title" type="text" placeholder="例如：实验1：Python基础语法" :disabled="isLoading" />
        </label>
        <label class="field">
          <span>slug</span>
          <input v-model.trim="form.slug" type="text" placeholder="例如：exp-python-basic" :disabled="isLoading" />
        </label>
        <label class="field">
          <span>实验模式</span>
          <select v-model="form.interaction_mode" :disabled="isLoading">
            <option value="native_editor">原生模式（native_editor）</option>
            <option value="guided_template">引导式模板模式（guided_template）</option>
          </select>
        </label>
        <label class="field sort-field">
          <span>排序号</span>
          <input v-model.number="form.sort_order" type="number" :disabled="isLoading" />
        </label>
        <label class="field">
          <span>启用状态</span>
          <select v-model="form.is_active" :disabled="isLoading">
            <option :value="true">启用</option>
            <option :value="false">停用</option>
          </select>
        </label>
        <label class="field">
          <span>发布状态</span>
          <select v-model="form.is_published" :disabled="isLoading">
            <option :value="true">已发布</option>
            <option :value="false">未发布</option>
          </select>
        </label>
        <label class="field">
          <span>开放时间</span>
          <input v-model="form.open_at" type="datetime-local" :disabled="isLoading" />
        </label>
        <label class="field">
          <span>截止时间</span>
          <input v-model="form.due_at" type="datetime-local" :disabled="isLoading" />
        </label>
      </div>

      <label class="field">
        <span>实验简介（description）</span>
        <textarea v-model="form.description" rows="3" :disabled="isLoading" placeholder="用于列表展示的简介"></textarea>
      </label>

      <label class="field">
        <span>实验说明正文（instruction_content）</span>
        <textarea
          v-model="form.instruction_content"
          rows="8"
          :disabled="isLoading"
          placeholder="可填写 Markdown 或纯文本说明"
        ></textarea>
      </label>

      <template v-if="form.interaction_mode === 'native_editor'">
        <label class="field">
          <span>起始代码（starter_code）</span>
          <textarea
            v-model="form.starter_code"
            rows="12"
            :disabled="isLoading"
            placeholder="学生进入实验时看到的初始代码"
          ></textarea>
        </label>
      </template>
      <template v-else>
        <article class="mode-placeholder">
          引导式模板模式第一版：支持模板参数、导入库配置与代码模板保存。
        </article>
        <div class="guided-grid">
          <label class="field">
            <span>template_type</span>
            <input v-model.trim="form.template_type" type="text" :disabled="isLoading" placeholder="例如：web_scraping_table" />
          </label>
          <label class="field">
            <span>allow_edit_generated_code</span>
            <select v-model="form.allow_edit_generated_code" :disabled="isLoading">
              <option :value="true">允许学生继续编辑生成代码</option>
              <option :value="false">不允许（只读）</option>
            </select>
          </label>
        </div>
        <label class="field">
          <span>template_schema（JSON）</span>
          <textarea
            v-model="form.template_schema_text"
            rows="8"
            :disabled="isLoading"
            placeholder='例如：{"fields":[{"name":"target_url","type":"text"}]}'
          ></textarea>
        </label>
        <label class="field">
          <span>import_config（JSON）</span>
          <textarea
            v-model="form.import_config_text"
            rows="8"
            :disabled="isLoading"
            placeholder='例如：{"fixed_imports":["import requests"],"optional_imports":["numpy"],"allow_custom_import":true}'
          ></textarea>
        </label>
        <label class="field">
          <span v-pre>code_template（支持占位符：{{target_url}} / {{headers_block}} / {{preview_count}} / {{imports}}）</span>
          <textarea
            v-model="form.code_template"
            rows="16"
            :disabled="isLoading"
            placeholder="请输入引导式模板代码"
          ></textarea>
        </label>
      </template>

      <div class="actions-row">
        <button type="button" class="btn plain" :disabled="isLoading" @click="goBack">返回列表</button>
        <RouterLink v-if="isEditMode" class="btn test-link" :to="testPath">进入测试</RouterLink>
        <button type="button" class="btn primary" :disabled="isLoading" @click="handleSubmit">
          {{ isLoading ? "保存中..." : isEditMode ? "保存修改" : "创建实验" }}
        </button>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  createAdminExperiment,
  getAdminExperimentById,
  updateAdminExperiment,
} from "../api/admin";
import { toDateTimeLocalInput, toUtcIsoStringFromLocalInput } from "../utils/datetime";

const route = useRoute();
const router = useRouter();

const isLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);

const experimentId = computed(() => Number(route.params.id || 0));
const isEditMode = computed(() => Number.isInteger(experimentId.value) && experimentId.value > 0);
const testPath = computed(() => {
  if (!isEditMode.value) {
    return "/admin/experiments";
  }
  if (form.interaction_mode === "guided_template") {
    return `/guided-experiment?experiment_id=${experimentId.value}`;
  }
  return `/editor?experiment_id=${experimentId.value}`;
});

const form = reactive({
  title: "",
  slug: "",
  description: "",
  instruction_content: "",
  starter_code: "",
  interaction_mode: "native_editor",
  template_type: "",
  template_schema_text: "",
  code_template: "",
  import_config_text: "",
  allow_edit_generated_code: true,
  sort_order: 0,
  is_active: true,
  is_published: false,
  open_at: "",
  due_at: "",
});

function parseJsonText(value, fieldLabel) {
  const text = (value || "").trim();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${fieldLabel} 不是有效 JSON`);
  }
}

function formatJsonText(value) {
  if (!value || typeof value !== "object") {
    return "";
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return "";
  }
}

function buildPayload() {
  const payload = {
    title: form.title.trim(),
    slug: form.slug.trim(),
    description: form.description.trim() || null,
    instruction_content: form.instruction_content.trim() || null,
    starter_code: form.interaction_mode === "native_editor" ? form.starter_code : null,
    interaction_mode: form.interaction_mode,
    template_type: null,
    template_schema: null,
    code_template: null,
    import_config: null,
    allow_edit_generated_code: Boolean(form.allow_edit_generated_code),
    sort_order: Number.isFinite(Number(form.sort_order)) ? Number(form.sort_order) : 0,
    is_active: Boolean(form.is_active),
    is_published: Boolean(form.is_published),
    open_at: toUtcIsoStringFromLocalInput(form.open_at),
    due_at: toUtcIsoStringFromLocalInput(form.due_at),
  };
  if (form.interaction_mode === "guided_template") {
    payload.template_type = form.template_type.trim() || null;
    payload.template_schema = parseJsonText(form.template_schema_text, "template_schema");
    payload.code_template = form.code_template || null;
    payload.import_config = parseJsonText(form.import_config_text, "import_config");
  }
  return payload;
}

function applyDetail(detail) {
  form.title = detail.title || "";
  form.slug = detail.slug || "";
  form.description = detail.description || "";
  form.instruction_content = detail.instruction_content || "";
  form.starter_code = detail.starter_code || "";
  form.interaction_mode = detail.interaction_mode || "native_editor";
  form.template_type = detail.template_type || "";
  form.template_schema_text = formatJsonText(detail.template_schema);
  form.code_template = detail.code_template || "";
  form.import_config_text = formatJsonText(detail.import_config);
  form.allow_edit_generated_code = detail.allow_edit_generated_code !== false;
  form.sort_order = Number.isFinite(Number(detail.sort_order)) ? Number(detail.sort_order) : 0;
  form.is_active = Boolean(detail.is_active);
  form.is_published = Boolean(detail.is_published);
  form.open_at = toDateTimeLocalInput(detail.open_at);
  form.due_at = toDateTimeLocalInput(detail.due_at);
}

async function loadDetail() {
  if (!isEditMode.value) {
    return;
  }
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const detail = await getAdminExperimentById(experimentId.value);
    applyDetail(detail);
  } catch (error) {
    errorMessage.value = `实验详情加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

function goBack() {
  router.push("/admin/experiments");
}

async function handleSubmit() {
  actionMessage.value = "";
  actionError.value = false;
  errorMessage.value = "";

  let payload = null;
  try {
    payload = buildPayload();
  } catch (error) {
    actionMessage.value = error.message || "表单格式校验失败";
    actionError.value = true;
    return;
  }
  if (!payload.title) {
    actionMessage.value = "标题不能为空";
    actionError.value = true;
    return;
  }
  if (!payload.slug) {
    actionMessage.value = "slug 不能为空";
    actionError.value = true;
    return;
  }
  if (payload.open_at && payload.due_at && new Date(payload.due_at).getTime() <= new Date(payload.open_at).getTime()) {
    actionMessage.value = "截止时间必须晚于开放时间";
    actionError.value = true;
    return;
  }

  isLoading.value = true;
  try {
    if (isEditMode.value) {
      await updateAdminExperiment(experimentId.value, payload);
      actionMessage.value = "实验更新成功";
    } else {
      const created = await createAdminExperiment(payload);
      actionMessage.value = "实验创建成功";
      await router.replace(`/admin/experiments/${created.experiment_id}/edit`);
      return;
    }
    await loadDetail();
  } catch (error) {
    actionMessage.value = `保存失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadDetail();
});
</script>

<style scoped>
.form-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 16px;
}

.head-panel h2 {
  margin: 0;
}

.head-panel p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.field span {
  font-size: 14px;
  color: var(--text-muted);
}

.field input,
.field select,
.field textarea {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.sort-field input {
  width: 100%;
  max-width: 100%;
}

.mode-placeholder {
  margin-top: 10px;
  border: 1px dashed var(--border-strong);
  border-radius: 8px;
  padding: 12px;
  background: var(--surface-3);
  color: var(--text-muted);
  font-size: 14px;
}

.guided-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.actions-row {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.plain {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn.test-link {
  background: var(--accent-cyan-strong);
  color: var(--surface-1);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  .form-grid {
    grid-template-columns: 1fr;
  }

  .guided-grid {
    grid-template-columns: 1fr;
  }

  .sort-field input {
    width: 100%;
    max-width: 100%;
  }
}
</style>
