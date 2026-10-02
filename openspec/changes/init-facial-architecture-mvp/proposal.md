## Why

传统相学测算应用多充斥低质迷信文案与粗糙视觉，存在严重的微信生态审核合规风险及大模型视觉幻觉（如误判五官特征）问题。本项目打造一款基于“现代骨相美学与微表情神态心理学”的微信小程序，结合高精度计算机视觉（MediaPipe）几何量测与权威知识库 RAG，驱动多模态大模型输出极简冷淡杂志风的深度骨相解构报告，兼具高合规性、科学专业度与社交裂变传播力。

## What Changes

- **初始化现代骨相美学小程序 (MVP)**：支持单人面相拍照/上传、面部对齐引导、毫秒级几何计算、仪式感扫描与杂志级报告呈现。
- **高精度 CV 几何量测引擎**：提取头部去旋转后的面部长宽比、下颌收拢夹角、眼裂长宽比、外眦上扬角及耳位相对高低。
- **结构化相学与美学 RAG 知识库**：沉淀清洗后的《冰鉴》《麻衣神相》去迷信化精髓，融合现代颅面美学与微表情心理学，依据几何特征动态召回。
- **多模型无缝故障转移适配层**：以 Google Gemini 1.5 Flash 8B 为主模型（极速低成本），国内阿里通义千问 Qwen-VL-Plus 为热备用模型，严格输出强类型 JSON。
- **极简高级冷淡风 UI 与海报导出**：黑白灰高对比冷淡风视觉规范、前端 Canvas 高清长海报生成。
- **预留中远期演进能力**：接口与数据模型层预留“夫妻相双人合盘”、“岁月成长与精气神对比”、“社交标签盲盒”等后续扩展字段。

## Capabilities

### New Capabilities
- `facial-geometry-engine`: 基于 MediaPipe 478 关键点的面部几何量测引擎，计算去姿态角后的脸部长宽比、下颌夹角、外眦上扬角、眼裂比例。
- `physiognomy-rag-knowledge`: 面相古籍与现代美学切片知识库，支持根据 CV 测算指标动态合成 Query 并召回权威依据。
- `model-provider-adapter`: 多模态大模型抽象适配层，支持 Gemini 1.5 Flash 8B 与国内 Qwen-VL 自动容灾降级，约束 JSON Schema 输出。
- `mini-program-ui`: Uni-app 极简冷淡风小程序，包含相机对齐遮罩、扫描仪式感动效、结构化卡片排版与 Canvas 海报生成。

### Modified Capabilities
<!-- 本次为初始版本，无既有能力变更 -->

## Impact

- **前端系统**：新建 Uni-app (Vue 3 + TypeScript + Vite + UnoCSS) 项目工程。
- **后端服务**：新建 Python FastAPI 后端服务，集成 `mediapipe`、`opencv-python`、`chromadb`、`google-generativeai`、`dashscope` 等依赖。
- **网络与基础设施**：需配置海外代理（针对 Gemini）与国内直连 API Key，支持环境配置热切换。
