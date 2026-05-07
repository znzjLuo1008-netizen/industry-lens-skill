---
name: industry-lens
description: >
  行业关键词百科页面生成器。输入一个行业名（如"智能驾驶"），直接输出一个完整的单页 HTML：
  包含 100 个关键词卡片（专业释义 + 查资料 + 行业数据 + 大白话 四区块）+ 3 家标杆公司拆解
  （生态位 + 护城河 + 生命周期 + 收入结构）。
  适用于：快速了解陌生行业、投研辅助、行业 Wiki 建设、给非专业读者科普。
  触发词：行业百科、IndustryLens、行业关键词、100 词、30 秒看懂行业、行业三强拆解。
version: 1.0.0
author: 小罗
agent_created: true
tags: [industry, wiki, keywords, research, investment, encyclopedia]
---

# 🔍 IndustryLens — 行业关键词百科生成器

## 核心能力

输入**一个行业名称**，自动调用 DeepSeek 生成一份完整的**单页 HTML 行业百科**，包含：

- **100 个关键词卡片**（4 区块布局）：
  - 📖 **专业释义** 150-200 字三段式（定义 + 2025-2026 最新数据 + 产业影响）
  - 🔍 **查资料** Wiki + Google 一键跳转
  - 📈 **行业数据** 35-70 字含具体数字和公司名
  - 💬 **大白话** 25-50 字生活化类比
- **3 家标杆公司深度拆解**：
  - 生态位（30 字定位）
  - 护城河专业版（100 字+）+ 大白话版
  - 企业生命周期（初创/成长/成熟/转型/衰退 5 阶段）
  - 收入结构（多条目堆叠条，pct 加和=100）
- **数字/L 级别/百分比 自动高亮**（链接样式蓝底 + 下划线）
- **4 分类**：核心概念 · 财务指标 · 技术术语 · 商业模型（各约 25 词）
- **纯前端单页**（无构建，双击 HTML 即可）

## 设计原则（必须遵守）

### 视觉风格
1. **浅色极简** — 白底、细分隔线、圆角 16px
2. **主色调深绿 + 灰白**：
   - 主色：`#166534`（深绿）/ `#0F6E56`（青）/ `#185FA5`（链接蓝）
   - 辅色：`#E8F1EB`（浅绿底）/ `#F0F8F2`（大白话底色）/ `#F4F4F1`（按钮底）
   - 高亮：`#22C55E` 系列（mark 标签）
3. **拒绝**：彩色渐变条、多色胶囊、emoji 标签、青绿色系（Natural Palette 已弃用）
4. **仅"大白话"区块保留淡绿底**作为情感锚点

### 卡片布局规则
1. **关键词卡片**：白底 + 0.5px 细边 + 16px 圆角，区块之间用 0.5px 分隔线分开（不用色块）
2. **公司卡片**：白底 + 12px 阴影 + 24px 圆角，**无彩色顶部条**
3. **区块标签**：纯文字 + uppercase + 字距，**无胶囊背景**
4. **拒绝**：竖线（左边框、border-left）、多重边框、彩色装饰条

### 交互体验
1. **数字自动高亮**：`\d+%` 和 `L0-L5` 自动套 `.kw-num-hl`（蓝底 + 底部下划线）
2. **Wiki/Google 按钮**：深绿色浅底，hover 深绿白字
3. **访问官网按钮**：灰白风，hover 浅绿
4. **卡片 hover 上浮 3px** + 阴影加深
5. **IntersectionObserver 滚动渐入**（delay 0-540ms 错峰）

### 字号 & 字体
1. **标题**：Space Grotesk（英文）+ Noto Sans SC（中文），font-weight 600
2. **正文**：Inter + Noto Sans SC，font-weight 400-500
3. **关键词标题**：1.06rem / weight 600
4. **正文**：0.86rem / line-height 1.85
5. **区块标签**：0.66rem uppercase letter-spacing .1em

### 文案铁律
1. **研报视角**：生态位 / 护城河 / 生命周期
2. **禁用投资语言**：目标价 / PE / DCF / 买入卖出
3. **数据必须含 2025-2026 具体数字 + 公司名**，禁编造
4. **大白话**要有类比和幽默感，禁短语化

## 工作流程

### 🚀 快捷路径（推荐）

Skill 已提供完整脚本 `references/generate.py`，直接调用即可：

```bash
# 基本用法：生成并输出到当前目录
python3 ~/.workbuddy/skills/industry-lens/references/generate.py "智能驾驶"

# 指定输出路径
python3 ~/.workbuddy/skills/industry-lens/references/generate.py "智能驾驶" /tmp/auto.html

# 从已有数据库读取（秒开，不调 API）
python3 ~/.workbuddy/skills/industry-lens/references/generate.py "智能驾驶" \
  --preloaded /Users/luoluo/WorkBuddy/20260417171541/industrylens/preloaded_data_v5.js
```

生成后用 `preview_url` 工具打开预览。

### 详细工作流程

#### Step 1: 理解用户意图
用户输入可能是：
- **标准行业名**（如"智能驾驶"、"生物医药"）→ 直接生成
- **泛模糊词**（如"新能源"）→ 澄清是光伏/风电/储能/氢能哪一个
- **公司名**（如"特斯拉"）→ 反向映射到所属行业（智能驾驶）
- **技术词**（如"Transformer"）→ 反向映射到所属行业（人工智能）

如果输入不明确，**用 AskUserQuestion 澄清**，再开工。

#### Step 2: 优先查已有数据库

如果本机存在 `/Users/luoluo/WorkBuddy/20260417171541/industrylens/preloaded_data_v5.js`（IndustryLens 主项目的预加载数据），**优先用它**，避免重复调用 DeepSeek（节省约 $0.1-0.2 / 次）。

#### Step 3: 调用 DeepSeek 生成数据（库里没有才调）

调用 2-3 次 API（避免 token 截断）：

**调用 1 — 关键词 1-50**（core + finance 为主）
**调用 2 — 关键词 51-100**（tech + biz + 长尾）
**调用 3 — 3 家标杆公司**

Prompt 模板详见 `references/prompt_templates.md`。

#### Step 4: 拼装单页 HTML

读取 `references/html_template.html` 作为骨架，注入 JSON 数据到：
- `INDUSTRY` — 行业元信息
- `KEYWORDS` — 关键词数组（100 条）
- `COMPANIES` — 公司数组（3 条）

核心渲染函数（已在模板中）：
- `renderGrid()` — 100 词卡片 → CSS Grid 自适应 340px 列
- `renderTop3()` — 3 公司卡片 → 三栏
- `autoHl(html)` — 数字/百分比/L级别 自动加 `<b class="kw-num-hl">` 包裹
- `renderCatFilter()` — 分类按钮（全部/核心/财务/技术/商业）

#### Step 5: 质量自检

生成后执行质量检查：
- 关键词数量：≥95 条
- pro 字数均值：≥130 字
- industryData 有数据：≥90% 条含数字
- ref 覆盖率：100%（每条都有 Wiki + Google）
- 公司：必须 3 家且都有 moatPro≥80字 + revenue≥3条
- 如不达标，重新生成薄弱批次

#### Step 6: 输出文件 + 预览

输出到 `./{行业名}-百科.html`（用户当前目录），然后 `preview_url` 打开。

## JSON Schema

```json
{
  "industry": {
    "name": "智能驾驶",
    "desc": "利用传感器、算法和控制系统实现车辆部分或完全自主行驶的技术"
  },
  "keywords": [
    {
      "rank": 1,
      "cat": "core|finance|tech|biz",
      "term": "自动驾驶分级",
      "pro": "SAE J3016 将自动驾驶分为 L0-L5 共 6 级... (150-200字)",
      "ref": {"google": "自动驾驶分级 2025", "wiki": "Self-driving car"},
      "industryData": "2025年中国 L2 新车渗透率 55%+... (35-70字)",
      "ez": "就像考试分数，L0 是零分，L5 是满分 100... (25-50字)"
    }
    // ... 共 100 条
  ],
  "companies": [
    {
      "name": "特斯拉",
      "enName": "Tesla",
      "domain": "tesla.com",
      "ecoNiche": "电动车+FSD一体化垂直整合巨头",
      "tags": ["FSD", "自研芯片", "4680电池"],
      "moatPro": "特斯拉拥有全球最大自动驾驶数据集... (100字+)",
      "moatEz": "FSD就是汽车界的iOS... (30字+)",
      "lifecycle": 2,
      "lifeLabel": "成熟期",
      "revenue": [
        {"label": "汽车销售", "pct": 85, "color": "#0F6E56"},
        {"label": "能源业务", "pct": 8, "color": "#185FA5"},
        {"label": "服务收入", "pct": 7, "color": "#888"}
      ]
    }
    // ... 共 3 家
  ]
}
```

## 必读参考文件

实现时必须读取这些文件：

1. **`references/prompt_templates.md`** — DeepSeek 的 system + user prompt 模板（关键词 + 公司 + 增强扩写）
2. **`references/html_template.html`** — 完整 HTML 骨架（CSS + JS 渲染逻辑），直接替换数据后即可输出
3. **`references/api_call.py`** — Python 封装的 DeepSeek API 调用函数（含 curl -k 走 SSL、临时文件、重试）

## 可选：离线库匹配

如果用户当前工作目录有 `preloaded_data_v5.js`（IndustryLens 主项目的预加载数据），**优先从该文件读取**已有行业数据，避免重复调用 DeepSeek。

## 关键技术坑

1. **SSL 证书校验失败**（公司网络）：必须用 `curl -k` 跳过校验，不能用 urllib
2. **大 JSON payload**：必须写临时文件用 `--data @file.json`，不能 shell 内联
3. **token 截断**：100 词单次调用会撞 32K 上限，必须分 2 次（1-50 + 51-100）
4. **autoHl 防重复包裹**：用 `__PHn__` placeholder 先保护 mark/b/a 标签，再做正则替换，最后还原
5. **单项 100% 收入兜底**：渲染公司卡片时检测 `revenue.length===1 && revenue[0].pct===100`，改显"营收结构未公开"提示

## 输出格式

最终输出单个 HTML 文件：
- 文件名：`./{行业名}-百科.html`（例如 `./智能驾驶-百科.html`）
- 大小：约 500KB（含数据注入）
- 不依赖外部 CDN（除 Google Fonts 和 Clearbit Logo）
- 双击即可在浏览器打开，无需任何构建
