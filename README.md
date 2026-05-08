# 🔍 IndustryLens Skill

[English](README.en.md) | [中文](README.md)


> **输入一个行业名，30 秒生成包含 100 词百科 + 3 家标杆公司深度拆解 + 产业链上中下游 12-14 细分的研报风单页 HTML**

![GitHub](https://img.shields.io/badge/Type-WorkBuddy%20Skill-166534)
![License](https://img.shields.io/badge/License-MIT-blue)
![AI](https://img.shields.io/badge/LLM-DeepSeek-8b5cf6)
![Version](https://img.shields.io/badge/Version-v1.3.0-22C55E)

🌐 **在线 Demo**：[znzjluo1008-netizen.github.io/industry-lens-skill](https://znzjluo1008-netizen.github.io/industry-lens-skill/)

---

## 📸 效果预览

本 skill 生成的页面效果（见 `examples/` 目录，可直接点击在线访问）：

| 行业 | 在线访问 | 词数 | 公司数 | 产业链 |
|---|---|---|---|---|
| 光伏 | [打开 →](https://znzjluo1008-netizen.github.io/industry-lens-skill/examples/%E5%85%89%E4%BC%8F-%E7%99%BE%E7%A7%91.html) | 100 | 3 | 上中下 12 细分 / 59 家 |
| 智能驾驶 | [打开 →](https://znzjluo1008-netizen.github.io/industry-lens-skill/examples/%E6%99%BA%E8%83%BD%E9%A9%BE%E9%A9%B6-%E7%99%BE%E7%A7%91.html) | 100 | 3 | 上中下 13 细分 / 64 家 |
| AI 生图 | [打开 →](https://znzjluo1008-netizen.github.io/industry-lens-skill/examples/AI%E7%94%9F%E5%9B%BE-%E7%99%BE%E7%A7%91.html) | 100 | 3 | 上中下 13 细分 / 65 家 |
| 烟草 | [打开 →](https://znzjluo1008-netizen.github.io/industry-lens-skill/examples/%E7%83%9F%E8%8D%89-%E7%99%BE%E7%A7%91.html) | 100 | 3 | 上中下 14 细分 / 69 家 |

每个关键词卡包含 **4 区块**：
- 📖 **专业释义** 150-200 字三段式（定义 + 2025-2026 数据 + 产业影响）
- 🔍 **查资料** Wiki + Google 一键跳转
- 📈 **行业数据** 35-70 字含具体数字和公司名
- 💬 **大白话** 25-50 字生活化类比

每家公司卡包含：**生态位 + 护城河（专业版/大白话）+ 生命周期 + 收入结构（堆叠进度条）**

**产业链 v1.3 升级**（研报风横向价值链）：
- 上中下游三层结构 + 每层标注毛利徽章 / 议价能力徽章
- 每层 3-5 个细分环节，每个环节 4-5 家真实公司
- 跨层公司唯一性（v1.3 红线）：一家公司只能归到一层，按"营收占比/市场地位/战略叙事/避让"四原则判定主业
- `keyInsight` 黄色卡片点出 2025-2026 核心矛盾

---

## 🚀 快速开始

### 方式一：作为 WorkBuddy Skill 使用（推荐）

1. 安装到本地：
```bash
# 克隆到 WorkBuddy 的 skills 目录
git clone https://github.com/znzjLuo1008-netizen/industry-lens-skill.git \
  ~/.workbuddy/skills/industry-lens
```

2. 在 WorkBuddy 对话里直接说：
```
帮我做个《脑机接口》的行业百科
IndustryLens 看看半导体
```

skill 自动被触发，3 分钟内输出 HTML。

### 方式二：命令行直接调用

```bash
# 1. 设置 DeepSeek API Key
export DS_KEY="sk-你的密钥"

# 2. 生成百科
python3 references/generate.py "智能驾驶"
# → 输出到 ./智能驾驶-百科.html

# 指定输出路径
python3 references/generate.py "生物医药" /tmp/bio.html

# 从已有预加载数据库读取（秒开，不调 API）
python3 references/generate.py "智能驾驶" \
  --preloaded /path/to/preloaded_data.js
```

---

## 🏗 目录结构

```
industry-lens-skill/
├── SKILL.md                     ← WorkBuddy skill 触发规则 + 设计规范 + v1.3 产业链铁律
├── index.html                   ← GitHub Pages 主页（4 行业卡片入口）
├── references/
│   ├── generate.py              ← 主入口脚本（含产业链生成 + 质量自检）
│   ├── html_template.html       ← 完整单页 HTML 骨架（CSS+JS，含研报风产业链可视化）
│   ├── api_call.py              ← DeepSeek API 封装
│   └── prompt_templates.md      ← 全量 prompt 模板（含 v1.3 跨层唯一性硬约束）
├── examples/                    ← 4 个真实生成样例
│   ├── 光伏-百科.html
│   ├── 智能驾驶-百科.html
│   ├── AI生图-百科.html
│   └── 烟草-百科.html
├── README.md / README.en.md
└── LICENSE
```

---

## 🎨 设计原则

### 视觉风格
- **浅色极简**：白底、0.5px 细分隔线、16px 圆角
- **主色调深绿 + 灰白**：`#166534` / `#0F6E56` / `#185FA5`
- **拒绝**：彩色渐变条、多色胶囊、emoji 标签、多重边框
- **仅"大白话"区块保留淡绿底**（情感锚点）

### 产业链可视化（v1.3 沉淀的踩坑铁律）
- ❌ Sankey 桑基图不适合产业链拆解（公司数量凑流量值不承载商业含义）
- ✅ 横向三段式价值链（Bessemer / a16z / 高瓴研报标配）：三色淡底 + 毛利/议价徽章 + 细分行 + 公司标签
- 🛡 跨层公司唯一性红线：一家公司只能归到一层，按主业判定四原则归一
- 📦 纯 CSS+HTML 实现，零外部依赖（避免 D3/d3-sankey CDN 失败）

### 交互体验
- **数字自动高亮**：百分比、L 等级自动套链接样式（蓝底 + 底部下划线）
- **Wiki / Google 按钮**：深绿色浅底，hover 深绿白字
- **卡片 hover 上浮 3px** + 阴影加深
- **IntersectionObserver 滚动渐入**

### 文案铁律
- **研报视角**：生态位 / 护城河 / 生命周期（禁投资化语言）
- **数据必须含 2025-2026 具体数字 + 公司名**，禁编造
- **大白话**要有类比和幽默感

---

## ⚙️ 技术栈

- **纯前端 HTML + Inline CSS + Vanilla JS**（无构建、双击即打开）
- **DeepSeek Chat API** 生成数据（支持其他 OpenAI 兼容 API）
- **Python 3** 调用脚本
- **无数据库依赖**（数据全部 inline 在 HTML）

### API 调用要点
1. 用 `curl -k` 跳过 SSL 校验（公司内网兼容）
2. 用临时文件 `--data @file.json` 避免 shell 转义
3. 100 词生成拆成 2 次调用（1-50 + 51-100）避免 token 截断
4. 公司单独调用（schema 不同）
5. 产业链单独调用（v1.1 起）：max_tokens 6000，含跨层唯一性硬约束
6. 带质量自检：pro ≥130 字、ref 覆盖率 100%、公司 ≥3 条 revenue
7. 产业链生成后必跑跨层重复扫描（v1.3 红线）

---

## 📊 成本估算

| 规模 | API 次数 | 耗时 | 费用 |
|---|---|---|---|
| 单行业生成 | 4 次（关键词×2 + 公司 + 产业链） | 5-8 min | ~$0.20 |
| 100 行业批量 | 400 次 | 5-8 hrs | ~$20 |
| 跳过产业链 | 3 次 | 3-4 min | ~$0.15 |

---

## 🛠 定制开发

### 修改视觉样式
编辑 `references/html_template.html` 中的 `<style>` 块。注意保持：
- 主色 `#0F6E56` / `#166534` 不变（除非想换色系）
- 区块间用 `border-top: 0.5px` 分隔而非色块
- `.kw-num-hl` 等高亮 class 名保持不变（JS 依赖）

### 修改关键词数量
`generate.py` 里的 `generate_keywords()` 默认 2 批 × 50。改为 1 批就是 50 词，或改 prompt 为 "rank 1-30" 就变 30 词。

### 换 LLM
修改 `api_call.py` 里的 `API_URL` 和 `body['model']`。兼容 OpenAI API 协议的都能用（Kimi / ChatGPT / Qwen / GLM 等）。

---

## 💡 已知限制

- 数据依赖 LLM 知识截至 2025 年，更新的数字可能有偏差
- 人脸/人物图像在卡片中**不生成**（仅公司 Logo，通过 Clearbit 获取）
- 完整 100 词单次生成会撞 token 上限，必须 split
- Civitai Logo 等部分公司 Clearbit 可能缺图，自动 fallback 首字母
- DeepSeek 生成产业链时仍会犯跨层重复（一体化龙头自动塞 2-3 层），必须跑 v1.3 审计脚本兜底

---

## 🔗 相关项目

- **本 Skill 在线 Demo**：[znzjluo1008-netizen.github.io/industry-lens-skill](https://znzjluo1008-netizen.github.io/industry-lens-skill/)（4 行业完整示例）
- **IndustryLens 主站**：[znzjluo1008-netizen.github.io/industrylens](https://znzjluo1008-netizen.github.io/industrylens/)（109 行业完整预加载版）
- **WorkBuddy**：[codebuddy.cn/docs/workbuddy](https://www.codebuddy.cn/docs/workbuddy/Overview)（AI 助手平台，本 skill 的运行宿主）

---

## 📜 License

MIT License · © 2026 小罗 (znzjLuo1008-netizen)

---

## 📝 更新日志

- **v1.3.0**（2026-05-08）：一体化龙头判定法则 + 4 行业示例上线 GitHub Pages + 价值流动区块修复
- **v1.2.0**（2026-05-08）：产业链可视化铁律沉淀（Sankey 选型禁区 + 跨层重复红线）
- **v1.1.0**（2026-05-07）：新增产业链上中下游 3 层模块
- **v1.0.0**（2026-05-06）：100 词关键词卡片 + 3 家公司深度拆解

---

## 🙋 反馈

欢迎开 [Issue](https://github.com/znzjLuo1008-netizen/industry-lens-skill/issues) 或 PR。
