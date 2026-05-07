# 🔍 IndustryLens Skill

> **输入一个行业名，30 秒生成 100 词百科 + 3 家标杆公司深度拆解的单页 HTML**

![GitHub](https://img.shields.io/badge/Type-WorkBuddy%20Skill-166534)
![License](https://img.shields.io/badge/License-MIT-blue)
![AI](https://img.shields.io/badge/LLM-DeepSeek-8b5cf6)

🌐 **在线 Demo**：[znzjluo1008-netizen.github.io/industrylens](https://znzjluo1008-netizen.github.io/industrylens/)

---

## 📸 效果预览

本 skill 生成的页面效果（见 `examples/` 目录）：

| 行业 | 文件 | 词数 | 公司数 |
|---|---|---|---|
| 智能驾驶 | `examples/智能驾驶-百科.html` | 100 | 3 |
| 光伏 | `examples/光伏-百科.html` | 100 | 3 |
| AI 生图 | `examples/AI生图-百科.html` | 50 | 3 |

每个关键词卡包含 **4 区块**：
- 📖 **专业释义** 150-200 字三段式（定义 + 2025-2026 数据 + 产业影响）
- 🔍 **查资料** Wiki + Google 一键跳转
- 📈 **行业数据** 35-70 字含具体数字和公司名
- 💬 **大白话** 25-50 字生活化类比

每家公司卡包含：**生态位 + 护城河（专业版/大白话）+ 生命周期 + 收入结构（堆叠进度条）**

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
├── SKILL.md                     ← WorkBuddy skill 触发规则 + 设计规范
├── references/
│   ├── generate.py              ← 主入口脚本
│   ├── html_template.html       ← 完整单页 HTML 骨架（CSS+JS）
│   ├── api_call.py              ← DeepSeek API 封装
│   └── prompt_templates.md      ← 全量 prompt 模板
├── examples/                    ← 生成样例
│   ├── 智能驾驶-百科.html
│   ├── 光伏-百科.html
│   └── AI生图-百科.html
├── README.md
└── LICENSE
```

---

## 🎨 设计原则

### 视觉风格
- **浅色极简**：白底、0.5px 细分隔线、16px 圆角
- **主色调深绿 + 灰白**：`#166534` / `#0F6E56` / `#185FA5`
- **拒绝**：彩色渐变条、多色胶囊、emoji 标签、多重边框
- **仅"大白话"区块保留淡绿底**（情感锚点）

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
5. 带质量自检：pro ≥130 字、ref 覆盖率 100%、公司 ≥3 条 revenue

---

## 📊 成本估算

| 规模 | API 次数 | 耗时 | 费用 |
|---|---|---|---|
| 单行业生成 | 3 次 | 3-4 min | ~$0.15 |
| 100 行业批量 | 300 次 | 3-5 hrs | ~$15 |

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

---

## 🔗 相关项目

- **IndustryLens 主站**：[https://znzjluo1008-netizen.github.io/industrylens/](https://znzjluo1008-netizen.github.io/industrylens/)（109 行业完整预加载版）
- **WorkBuddy**：[codebuddy.cn/docs/workbuddy](https://www.codebuddy.cn/docs/workbuddy/Overview)（AI 助手平台，本 skill 的运行宿主）

---

## 📜 License

MIT License · © 2026 小罗 (znzjLuo1008-netizen)

---

## 🙋 反馈

欢迎开 [Issue](https://github.com/znzjLuo1008-netizen/industry-lens-skill/issues) 或 PR。
