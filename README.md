# 相度 (XiangDu) · 现代面容骨相量度与神态美学小程序

> **以数度量 · 见相入微**  
> 基于高精度计算机视觉（MediaPipe 478关键点）与大语言模型（Gemini / Qwen-VL）的多模态面容美学量测小程序。

---

## 项目简介

**「相度」** 彻底剥离了传统相学的江湖迷信色彩，以高精度计算机视觉技术提取的客观人体颌面几何指标（面长宽比、下颌骨相夹角、三庭黄金律、外眦仰角、五眼比例、出纳官唇比等）为科学依据，结合去迷信化清洗后的《冰鉴》《麻衣神相》经典与现代神态微表情心理学，驱动多模态大模型输出时尚杂志级的高定骨相解构报告。

### 核心亮点
- **478 稠密关键点量测**：MediaPipe Face Mesh 亚像素级打点，2D 头部姿态去倾斜校准（De-roll）；
- **全套科学相学量度**：三庭精微比率、下颌收拢折角、外眦飞扬势、五眼内眦间距比、财帛中岳鼻翼丰隆比、唇形厚度比；
- **自适应 RAG 知识检索**：根据实测几何特征自动合成检索探针，从本地轻量知识库召回权威依据注入大模型上下文；
- **多模型无缝容灾降级**：以 Google Gemini 1.5/3.8 Flash 为主通道，国内阿里通义千问 Qwen-VL-Plus 为热备，内置极端离线装配引擎，保证 99.9% 高可用；
- **高定极简杂志风 UI**：纯净暖玉白与香槟哑光金高奢色彩体系，自适应 9:16 高清朋友圈长海报生成。

---

## 目录结构

```text
physiognomy-mp/
├── backend/                       # Python FastAPI 后端服务
│   ├── app/
│   │   ├── api/v1/                # 分析与探活接口 (/api/v1/analyze)
│   │   ├── core/                  # 配置与异常处理
│   │   ├── prompts/               # 现代相学与心理学 Prompt 模板
│   │   ├── providers/             # Gemini / Qwen 多模型抽象适配层
│   │   ├── schemas/               # Pydantic 强类型数据模型
│   │   └── services/              # MediaPipe CV 引擎与 RAG 知识检索
│   ├── face_landmarker.task       # MediaPipe 官方高精度模型
│   ├── requirements.txt           # Python 依赖
│   └── .env.example               # 环境配置示例
│
├── frontend/                      # Uni-app (Vue 3 + Vite + TypeScript) 前端
│   ├── src/
│   │   ├── components/            # 取景框、扫描动效、标尺图层、杂志报告卡
│   │   ├── pages/index/           # 主流程沉浸式页面
│   │   ├── static/                # 官方高定「相度」Logo 图标
│   │   ├── style.css              # 高定极简设计系统 (Design Tokens)
│   │   └── utils/                 # 请求通信与 Canvas 2D 朋友圈海报生成
│   ├── manifest.json              # 小程序与 H5 配置 (AppID: wxd6d00a7513f90fe9)
│   ├── pages.json                 # 页面路由与窗口样式
│   └── package.json               # 前端依赖配置
│
├── start_backend.bat              # Windows 一键启动后端
├── start_frontend.bat             # Windows 一键启动前端开发预览
├── start_mp_weixin.bat            # Windows 一键启动微信小程序编译监听
└── build_mp_weixin.bat            # 微信小程序正式生产打包
```

---

## 快速开始

### 1. 后端启动 (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*(或直接双击根目录下的 `start_backend.bat`)*

* 接口文档地址：`http://127.0.0.1:8000/api/v1/docs`

### 2. 前端启动 (Uni-app)

```bash
cd frontend
npm install

# 微信小程序开发模式 (输出至 dist/dev/mp-weixin)
npm run dev:mp-weixin

# 或 H5 网页开发模式
npm run dev:h5
```
*(或直接双击根目录下的 `start_mp_weixin.bat`)*

### 3. 微信小程序导入

1. 打开 **微信开发者工具** ➔ 点击 **导入**；
2. 目录选择：`frontend/dist/dev/mp-weixin`；
3. AppID：`wxd6d00a7513f90fe9`；
4. 右上角「详情」➔「本地设置」➔ 勾选 **“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书”** 即可开始调试。

---

## 许可证

MIT License
