# 综合项目接力说明：某市在售房源数据可视化分析

## 目标

本次工作目标是为 `pythonclass` 平台新增一个期末综合实训项目：

- 项目名称：`综合项目：某市在售房源数据可视化分析`
- 项目形态：一个 `guided_template` 综合实验
- 教学节奏：三大节课分阶段推进
- 学生任务：按阶段配置参数、生成/运行代码、截图参数卡片/运行输出/二维表/图形，最后写入 Word 版实训报告
- 不要求学生从零写代码，也不在平台内收集长文本总结

三阶段安排：

1. 第一阶段：数据获取、数据预览、数据清洗、字段派生、数据存储
2. 第二阶段：数据读取、线性回归、关联关系挖掘
3. 第三阶段：分类分析、聚类分析、可视化整体分析

## 已完成

### 1. guided_template 前端能力增强

已修改：

- `frontend/src/views/GuidedTemplateExperimentView.vue`

新增能力：

- `template_schema.groups` 支持阶段卡片展示
- 每个阶段卡片有“应用本阶段参数到代码”按钮
- 单阶段应用只校验该阶段字段，不要求一次填完全部参数
- 未配置 `groups` 的旧实验保持原有统一参数网格，不破坏兼容性
- 阶段应用不会重复把 import 块插入代码顶部

关键位置：

- 阶段卡片模板：约第 42 行附近
- `templateGroups` 状态：约第 408 行附近
- `extractTemplateGroups`：约第 840 行附近
- `applyTemplateFieldsToCode` / `applyTemplateGroupToCode`：约第 1390 行附近
- 阶段卡片 CSS：约第 2090 行附近

### 2. 综合项目导入 JSON

已新增：

- `docs/final-house-visual-analysis-project-config.json`

用途：

- 后台实验导入用，不再使用 Markdown 配置文件

内容：

- `file_type`: `pythonclass_experiment_config`
- `title`: `综合项目：某市在售房源数据可视化分析`
- `slug`: `final-house-visual-analysis-project`
- `interaction_mode`: `guided_template`
- `template_type`: `final_house_visual_analysis_project`
- `allow_edit_generated_code`: `true`
- `template_schema.fields`: 29 个字段
- `template_schema.groups`: 第一阶段、第二阶段、第三阶段
- `import_config`: 包含 requests、BeautifulSoup、pandas、numpy、matplotlib、seaborn、sqlalchemy、sklearn、mlxtend 等
- `code_template`: 三阶段骨架代码，第一阶段默认开放，第二/三阶段默认注释，便于课堂逐步放开

注意：

- 之前曾生成过 `docs/final-house-visual-analysis-project-config.md`，后来已删除，因为后台导入需要 JSON。

### 3. 教学原始数据表和模拟网页

已新增：

- `table_raw/final_house_portal_raw.csv`
- `table_raw/final_house_portal_raw.sql`
- `docs/final_house_portal/index.html`
- `docs/final_house_portal/README.md`

数据说明：

- 来源：原始 `house.csv`
- 教学数据量：5036 条
- 字段：保留原始 14 个字段
  - `产权`
  - `关注`
  - `区域`
  - `单价`
  - `小区`
  - `年限`
  - `总价/万元`
  - `户型`
  - `房屋编码`
  - `挂牌时间`
  - `朝向`
  - `楼层`
  - `装修情况`
  - `面积`
- SQL 表名：`final_house_portal_raw`
- SQL 额外字段：`id` 自增主键
- 教学噪声：
  - 少量空 `区域`
  - 少量空 `小区`
  - 36 条重复 `房屋编码`
  - 面积/单价格式轻微不统一
  - 少量极端面积/单价

模拟网页：

- `docs/final_house_portal/index.html`
- 可以直接作为静态网页部署到云服务器
- 学生第一阶段填写云服务器上的 URL，使用 `requests + BeautifulSoup` 抓取表格

## 已验证

在 Windows 机器上已做过以下检查：

- `npm run build -- --outDir ../.tmp-frontend-build` 通过
- `docs/final-house-visual-analysis-project-config.json` 可正常 `json.loads`
- JSON 中三阶段 `groups` 正常存在
- `code_template` 用替换后的 import 占位符做过 Python AST 解析，通过
- `docs/final_house_portal/index.html` 用标准库 HTMLParser 验证：
  - 5036 行数据
  - 14 个原始字段
- `table_raw/final_house_portal_raw.sql` 验证：
  - 包含 `CREATE TABLE final_house_portal_raw`
  - 17 个 INSERT 分块
  - 包含 `idx_final_house_code` 和 `idx_final_house_region` 索引

## 当前 Git 状态提醒

当前 `git status --short` 中与本次综合项目直接相关的文件：

- `M frontend/src/views/GuidedTemplateExperimentView.vue`
- `?? docs/final-house-visual-analysis-project-config.json`
- `?? docs/final_house_portal/`
- `?? table_raw/final_house_portal_raw.csv`
- `?? table_raw/final_house_portal_raw.sql`
- `?? docs/HANDOFF_FINAL_HOUSE_PROJECT.md`

当前工作区里还存在一些看起来不是本次实现直接产生的 docs 变动/未跟踪文件，迁移到 Mac 后请单独判断是否纳入提交：

- `M docs/exp-big-data-visualization-business-analysis-config.json`
- `D docs/experiment7_knn_classification_design.md`
- `D docs/experiment9_big_data_visualization_config.md`
- `?? docs/exp-01-python-basic-data-types-config.json`
- `?? docs/exp-association-rule-mining-config.json`
- `?? docs/exp-clustering-kmeans-dbscan-analysis-config.json`
- `?? docs/exp-data-cleaning-basic-config.json`
- `?? docs/exp-knn-classification-analysis-config.json`
- `?? docs/exp-linear-regression-stage1-config.json`
- `?? docs/exp-mysql-read-observe-create-table-config.json`
- `?? docs/exp-web-scraping-fortune500-config.json`

不要在不了解来源的情况下直接删除或还原这些文件。

## Mac 接力建议

迁移到 Mac 后建议按这个顺序检查：

1. `git status --short`
2. 确认综合项目相关文件都在：
   - `frontend/src/views/GuidedTemplateExperimentView.vue`
   - `docs/final-house-visual-analysis-project-config.json`
   - `docs/final_house_portal/index.html`
   - `table_raw/final_house_portal_raw.csv`
   - `table_raw/final_house_portal_raw.sql`
3. 在 `frontend` 目录运行：

```bash
npm install
npm run build
```

4. 后台导入：
   - 使用 `docs/final-house-visual-analysis-project-config.json`
5. 数据准备：
   - 将 `table_raw/final_house_portal_raw.sql` 导入 MySQL，或仅把 `docs/final_house_portal` 上传到云服务器作为网页抓取入口
6. 课堂测试：
   - 第一阶段：填写网页 URL、数据库连接和目标表名，应用第一阶段参数，运行抓取/清洗/入库
   - 第二阶段：填写读取表名和回归/关联参数，应用第二阶段参数，取消注释对应代码运行
   - 第三阶段：填写分类/聚类/可视化参数，应用第三阶段参数，取消注释对应代码运行

## 仍需确认或可后续优化

- 是否需要把 `docs/final_house_portal/index.html` 上传到指定云服务器并固定 URL。
- 是否需要把 `final_house_portal_raw.sql` 导入到公共源数据库，作为教师备用数据表。
- 是否需要在后台导入后调整 `sort_order`，当前 JSON 中设置为 `100`。
- 如需更强体验，可后续把阶段卡片内的字段再拆成小节，但当前实现已满足“三阶段逐步配置、逐步运行”的要求。
