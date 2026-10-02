## Context

本项目旨在构建一个高规格的微信小程序“现代骨相与面容解构”，采用 Uni-app (Vue 3 + TS) 前端与 Python FastAPI 后端。产品核心在于彻底抛弃传统相学的江湖迷信色彩，以高精度计算机视觉（MediaPipe）测量出的客观面部几何指标为锚点，通过 RAG 调取清洗转译后的相学经典与现代神态心理学依据，最终由多模态大模型输出极简高级冷淡风的结构化报告。

## Goals / Non-Goals

**Goals:**
- 构建完整的单人面容解构 MVP 链路（拍照/上传 ➔ 几何量测 ➔ RAG 匹配 ➔ 大模型推理 ➔ 极简报告渲染 ➔ 海报导出）。
- 实现微秒级 CV 算法，精确测量：脸部长宽比、下颌收拢夹角、眼裂长宽比、外眦上扬角及耳位相对高低。
- 建立多模型热插拔与自动故障转移适配层（首选 Gemini 1.5 Flash 8B，备用国内通义千问 Qwen-VL-Plus）。
- 建立并严格执行《UI & Visual Design Spec》，确保极简高级冷淡风的视觉呈现、标尺绘制与动效过渡。
- 在接口和数据结构中为中远期功能（夫妻相合盘、岁月成长变化、社交玩法）预留扩展字段。

**Non-Goals:**
- 第一期不包含在线支付与充值系统（先打通体验与社交分享）。
- 第一期不实现实时的多帧视频流追踪，仅针对单张高清照片做静态 3D/2D Mesh 解析。
- 不做长期人脸图像存储，分析完毕即阅后即焚，确保隐私合规。

## Decisions

### 1. 算法层：MediaPipe Face Mesh (478 关键点)
- **决策**：采用 Google MediaPipe Face Mesh 进行离线几何测量。
- **替代方案考虑**：Dlib 68 点（精度不够，无法细致刻画眼裂缘与下颌角）；InsightFace（依赖较重，安装复杂）。
- **理由**：MediaPipe 纯 CPU 运行只需 15ms，拥有 468+10 虹膜精细点，足以完成去姿态角旋转、微米级眼部与下颌几何运算。

### 2. 知识增强层：轻量嵌入式 RAG (ChromaDB + Query Synthesizer)
- **决策**：使用轻量嵌入式向量库 ChromaDB 配合标签倒排索引。
- **理由**：零运维成本，无需独立启动 Docker，根据 CV 测出的离散指标（如 `canthal_tilt > 3.0`）自动构造混合检索探针，精确召回 3~4 条权威典籍切片。

### 3. 模型适配层：双通道热备 (Adapter Pattern)
- **决策**：抽象 `BaseLLMProvider`，封装 `GeminiFlashProvider` 与 `QwenVLProvider`。
- **理由**：Gemini 1.5 Flash 8B 成本极低、速度秒级，配合境外代理通道为主用；国内 Qwen-VL-Plus 为热备，超时或报错毫秒级无缝降级，前端完全无感知。

---

## UI & Visual Design Spec (专章：极简高级冷淡美学设计系统)

为了杜绝普通 AI 生成界面的廉价感与土味，前端必须严格遵守以下设计系统规范：

### 1. 调色盘与设计令牌 (Color Tokens)
```css
:root {
  /* 背景底色：极深邃夜空黑与悬浮层 */
  --bg-primary: #0C0D0E;       /* 主背景 */
  --bg-surface: #141518;       /* 卡片与悬浮面板 */
  --bg-surface-elevated: #1C1D21; /* 高亮悬浮/弹窗 */

  /* 边框与极细标尺线 */
  --border-subtle: #24262B;    /* 0.5px 极细卡片边框 */
  --border-caliper: #3E424B;   /* 标尺刻度与基准线 */
  --crosshair: #8E929B;        /* 准星十字标记与锚点 */

  /* 文本梯度 */
  --text-title: #F5F5F7;       /* 钛空白主标题 */
  --text-body: #C7C7CC;        /* 浅冷灰正文内容 */
  --text-muted: #6E7179;       /* 石墨灰元数据与编号 */

  /* 点缀色 (严格限制用量 < 3%) */
  --accent-gold-matte: #B59E75;/* 哑光冷金 (仅用于核心主导型徽标) */
  --accent-cyan-cold: #7EA0B7; /* 冰川冷蓝 (用于外眦角度标记) */
}
```

### 2. 间距网格与排版系统 (Grid & Typography)
* **网格原则**：严格基于 4px 基础网格系统，常用间距为 `8px`, `16px`, `24px`, `32px`。
* **卡片圆角**：统一使用微圆角 `4px` 或 `6px`，**严禁使用超过 12px 的大胶囊圆角**。
* **字体排印**：
  * 英文字符与数字：采用高智感等宽/半等宽衬线体（`Space Mono`, `DIN`, `Courier New` 兜底），展示 `∠ +6.8°`、`RATIO 1:1.05:0.95`；
  * 中文字体：利落无衬线体系（`PingFang SC`, `Hiragino Sans GB`），行高控制在 `1.6`，字间距 `letter-spacing: 0.05em ~ 0.1em`。

### 3. 核心组件原型与交互规范 (Component Anatomy)

#### A. 取景对齐遮罩组件 (`CameraGuideMask`)
* 界面覆盖全屏 70% 黑色半透明暗角；
* 中间镂空椭圆人脸取景框，四周带有极细的十字准星（`+`）与耳朵对齐辅助虚线；
* 上部带有实时提示气泡：“保持平视 · 露出双耳与额头”。

#### B. 仪式感扫描组件 (`ScanCeremonyOverlay`)
* 照片自动转为高反差黑白灰度；
* 一根 1px 宽的银白冷光扫描线以 `cubic-bezier(0.4, 0, 0.2, 1)` 缓动上下循环扫描；
* 右下角动态打字机输出计算日志：
  * `[T+0.8s] ALIGNING THREE-PARTS RATIO... [OK]`
  * `[T+1.6s] CALCULATING JAWLINE GONIAL ANGLE: 88.5°...`
  * `[T+2.4s] RETRIEVING CLASSICAL ARCHETYPES...`

#### C. 骨骼标尺与图像覆盖层 (`FacialCaliperCanvas`)
* 在用户照片表面渲染 Canvas 2D 标尺图层：
  * 内外眦连线：0.5px 极细银线，外眦标注弧度扇区与 `∠ +6.8°`；
  * 面部长宽：左侧与下侧带有工程卡尺样式的端点截线与数值 `1.42`；
  * 关键锚点：在鼻根点、下巴顶、下颌转折处浮现微型 `+` 符号。

#### D. 杂志级排版报告 (`EditorialReportCard`)
* 采用类似《Monocle》或《Vogue》的冷淡排版：
  * Header：`FACIAL ARCHITECTURE // DOSSIER NO. 2025-0891`；
  * 主导型徽标：`清骨敛气型`（配哑光冷金极细边框）；
  * 四维能量雷达：极简黑底单色多边形线框，无冗余底色；
  * 底部固定浮动操作栏：`[ 保存高清海报 ]`、`[ 重新测算 ]`。

#### E. 海报生成画布 (`PosterCanvas`)
* 竖版 9:16 长图，顶层嵌入经过灰度处理与标尺标注的照片，中间呈现骨相分析精粹，底部附带小程序极简太阳码。

---

## 中远期扩展架构储备 (Reserved Capabilities Roadmap)

在当前 MVP 的数据结构和接口设计中，预留以下字段，便于无缝升级：

```json
{
  "version": "1.0.0",
  "subject_mode": "single", // 预留: "single" | "couple_match" | "timeline_compare"
  "metrics": {
    "face_ratio": 1.42,
    "jaw_angle": 88.5,
    "canthal_tilt": 6.8
  },
  "extensions": {
    // 扩展 1: 夫妻相/双人契合度预留
    "couple_analysis": {
      "partner_id": null,
      "similarity_score": null,
      "complementary_points": []
    },
    // 扩展 2: 时间轴成长与状态对比预留
    "timeline_history": {
      "previous_record_id": null,
      "vitality_delta": null,   // 精气神变化分
      "firmness_delta": null   // 紧致度变化
    },
    // 扩展 3: 社交趣味卡片预留
    "social_card": {
      "meme_title": "天选搞钱体质",
      "aura_rarity": "TOP 3%"
    }
  }
}
```

## Risks / Trade-offs

- **[风险 1: 弱光或大角度侧脸导致关键点漂移]**
  → **对策**：在 CV 阶段增加质检阈值（姿态偏转角 Pitch/Yaw 超过 20° 时直接返回拦截并引导重拍）。
- **[风险 2: 海外 Gemini 接口偶发网络超时]**
  → **对策**：FastAPI 配置 6 秒严格超时，失败无缝切入国内 Qwen-VL-Plus。
- **[风险 3: 微信小程序审核涉及算命类目敏感词]**
  → **对策**：Prompt 与输出规范完全剔除一切迷信词汇，全面采用“美学、神态心理学、自驱力”表述，首页醒目标注“现代面部美学性格科普测试”免责声明。
