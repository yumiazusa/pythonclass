import request from "./request";

export async function getDocs(params = {}) {
  const { data } = await request.get("/docs", { params });
  return data;
}

export async function getDocBySlug(slug) {
  const { data } = await request.get(`/docs/${slug}`);
  return data;
}

export async function getDocCategories() {
  const { data } = await request.get("/docs/meta/categories");
  return data;
}
