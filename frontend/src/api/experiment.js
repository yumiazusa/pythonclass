import request from "./request";

export async function getExperiments() {
  const { data } = await request.get("/experiments");
  return data;
}

export async function getExperimentById(id) {
  const { data } = await request.get(`/experiments/${id}`);
  return data;
}

export async function validateGuidedTemplateImports(customImportText) {
  const { data } = await request.post("/experiments/guided-template/validate-imports", {
    custom_import_text: customImportText || "",
  });
  return data;
}
