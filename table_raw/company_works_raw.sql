SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

DROP TABLE IF EXISTS `company_works_raw`;

CREATE TABLE `company_works_raw` (
  `记录编号` VARCHAR(20) PRIMARY KEY COMMENT '企业业务记录编号',
  `业务日期` DATE NOT NULL COMMENT '业务发生日期',
  `区域` VARCHAR(20) NOT NULL COMMENT '业务所属区域',
  `城市` VARCHAR(30) NOT NULL COMMENT '业务所在城市',
  `事业部` VARCHAR(30) NOT NULL COMMENT '企业内部事业部',
  `销售渠道` VARCHAR(30) NOT NULL COMMENT '销售渠道',
  `客户类型` VARCHAR(30) NOT NULL COMMENT '客户类型',
  `产品类别` VARCHAR(30) NOT NULL COMMENT '产品类别',
  `订单数量` INT NOT NULL COMMENT '订单数量',
  `销售收入` DECIMAL(12,2) NOT NULL COMMENT '销售收入金额',
  `成本金额` DECIMAL(12,2) NOT NULL COMMENT '业务成本金额',
  `毛利金额` DECIMAL(12,2) NOT NULL COMMENT '销售收入减成本金额',
  `毛利率` DECIMAL(8,4) NOT NULL COMMENT '毛利金额占销售收入比例',
  `折扣率` DECIMAL(8,4) NOT NULL COMMENT '订单折扣比例',
  `应收金额` DECIMAL(12,2) NOT NULL COMMENT '应向客户收取金额',
  `回款金额` DECIMAL(12,2) NOT NULL COMMENT '已回款金额',
  `回款状态` VARCHAR(20) NOT NULL COMMENT '已回款、部分回款、未回款',
  `发票状态` VARCHAR(20) NOT NULL COMMENT '已开票、待开票、发票异常',
  `库存周转天数` INT NOT NULL COMMENT '库存周转天数',
  `客户满意度` DECIMAL(6,2) NOT NULL COMMENT '客户满意度评分',
  `风险等级` VARCHAR(20) NOT NULL COMMENT '低风险、中风险、高风险'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET @row_number := 0;

INSERT INTO `company_works_raw` (
  `记录编号`,
  `业务日期`,
  `区域`,
  `城市`,
  `事业部`,
  `销售渠道`,
  `客户类型`,
  `产品类别`,
  `订单数量`,
  `销售收入`,
  `成本金额`,
  `毛利金额`,
  `毛利率`,
  `折扣率`,
  `应收金额`,
  `回款金额`,
  `回款状态`,
  `发票状态`,
  `库存周转天数`,
  `客户满意度`,
  `风险等级`
)
SELECT
  CONCAT('CW', LPAD(n, 6, '0')) AS `记录编号`,
  DATE_ADD('2025-01-01', INTERVAL MOD(n - 1, 365) DAY) AS `业务日期`,
  ELT(MOD(n, 5) + 1, '华东', '华南', '华北', '西南', '华中') AS `区域`,
  CASE MOD(n, 10)
    WHEN 0 THEN '上海'
    WHEN 1 THEN '杭州'
    WHEN 2 THEN '广州'
    WHEN 3 THEN '深圳'
    WHEN 4 THEN '北京'
    WHEN 5 THEN '天津'
    WHEN 6 THEN '成都'
    WHEN 7 THEN '重庆'
    WHEN 8 THEN '武汉'
    ELSE '长沙'
  END AS `城市`,
  ELT(MOD(n, 4) + 1, '零售事业部', '企业服务事业部', '财税服务事业部', '供应链事业部') AS `事业部`,
  ELT(MOD(n, 4) + 1, '直营网点', '电商平台', '代理商', '企业大客户') AS `销售渠道`,
  ELT(MOD(n, 3) + 1, '个人客户', '中小企业', '集团客户') AS `客户类型`,
  ELT(MOD(n * 2 + FLOOR((n - 1) / 5), 5) + 1, '硬件设备', '软件订阅', '咨询服务', '财税服务', '维护服务') AS `产品类别`,
  `订单数量`,
  `销售收入`,
  `成本金额`,
  `销售收入` - `成本金额` AS `毛利金额`,
  ROUND((`销售收入` - `成本金额`) / NULLIF(`销售收入`, 0), 4) AS `毛利率`,
  `折扣率`,
  `应收金额`,
  `回款金额`,
  CASE
    WHEN `回款金额` >= `应收金额` * 0.98 THEN '已回款'
    WHEN `回款金额` <= `应收金额` * 0.2 THEN '未回款'
    ELSE '部分回款'
  END AS `回款状态`,
  CASE
    WHEN MOD(n, 31) = 0 THEN '发票异常'
    WHEN MOD(n, 7) IN (0, 1) THEN '待开票'
    ELSE '已开票'
  END AS `发票状态`,
  `库存周转天数`,
  `客户满意度`,
  CASE
    WHEN `回款金额` <= `应收金额` * 0.2 OR `折扣率` >= 0.18 OR `毛利率预估` < 0.16 THEN '高风险'
    WHEN `回款金额` < `应收金额` * 0.8 OR `折扣率` >= 0.12 OR `库存周转天数` > 55 THEN '中风险'
    ELSE '低风险'
  END AS `风险等级`
FROM (
  SELECT
    n,
    `订单数量`,
    `折扣率`,
    ROUND(`基准收入` * (1 - `折扣率`), 2) AS `销售收入`,
    ROUND(`基准收入` * (1 - `折扣率`) * (1 - `毛利率预估`), 2) AS `成本金额`,
    ROUND(`基准收入` * (1 - `折扣率`) * (1 + CASE WHEN MOD(n, 6) = 0 THEN 0.13 ELSE 0.00 END), 2) AS `应收金额`,
    ROUND(`基准收入` * (1 - `折扣率`) * (1 + CASE WHEN MOD(n, 6) = 0 THEN 0.13 ELSE 0.00 END) *
      CASE
        WHEN MOD(n, 17) = 0 THEN 0.00
        WHEN MOD(n, 9) = 0 THEN 0.45
        WHEN MOD(n, 6) = 0 THEN 0.72
        ELSE 1.00
      END, 2
    ) AS `回款金额`,
    `库存周转天数`,
    `客户满意度`,
    `毛利率预估`
  FROM (
    SELECT
      n,
      1 + MOD(n * 7, 48) AS `订单数量`,
      ROUND(0.02 + MOD(n * 13, 20) / 100.0, 4) AS `折扣率`,
      ROUND(
        (1800 + MOD(n * 137, 86000)) *
        CASE MOD(n, 5)
          WHEN 0 THEN 1.35
          WHEN 1 THEN 1.10
          WHEN 2 THEN 0.95
          WHEN 3 THEN 1.22
          ELSE 1.00
        END *
        CASE MOD(n, 4)
          WHEN 0 THEN 1.28
          WHEN 1 THEN 1.05
          WHEN 2 THEN 0.92
          ELSE 1.16
        END,
        2
      ) AS `基准收入`,
      ROUND(0.14 + MOD(n * 11, 30) / 100.0, 4) AS `毛利率预估`,
      12 + MOD(n * 5, 72) AS `库存周转天数`,
      ROUND(72 + MOD(n * 19, 2800) / 100.0, 2) AS `客户满意度`
    FROM (
      SELECT @row_number := @row_number + 1 AS n
      FROM
        (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) d1
        CROSS JOIN (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) d2
        CROSS JOIN (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) d3
        CROSS JOIN (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) d4
    ) seq
  ) base_data
) final_data;

SELECT COUNT(*) AS `生成行数` FROM `company_works_raw`;
