# 相度 (XiangDu) · 现代面容骨相量度与神态美学小程序

> **以数度量 · 见相入微**  
> 基于高精度计算机视觉（MediaPipe 478 关键点）与大语言模型（DeepSeek / Gemini / Qwen-VL）的多模态面容美学量测小程序。

---

## 目录
- [项目简介](#项目简介)
- [目录结构](#目录结构)
- [本地开发快速启动](#本地开发快速启动)
- [生产环境全流程部署指南](#生产环境全流程部署指南)
  - [一、后端 Docker 容器化部署](#一后端-docker-容器化部署)
  - [二、Nginx 反向代理与 HTTPS 配置](#二nginx-反向代理与-https-配置)
  - [三、Cloudflare CDN 与 SSL 避坑指南](#三cloudflare-cdn-与-ssl-避坑指南)
  - [四、微信公众平台合规与隐私指引 (解决 errno 112)](#四微信公众平台合规与隐私指引-解决-errno-112)
  - [五、小程序前端生产打包与正式上线发版](#五小程序前端生产打包与正式上线发版)
- [常见报错与踩坑排查手册](#常见报错与踩坑排查手册)
- [许可证](#许可证)

---

## 项目简介

**「相度」** 彻底剥离了传统相学的江湖迷信色彩，以高精度计算机视觉技术提取的客观人体颌面几何指标（面长宽比、下颌骨相夹角、三庭黄金律、外眦仰角、五眼比例、出纳官唇比等）为科学依据，结合去迷信化清洗后的《冰鉴》《麻衣神相》经典与现代神态微表情心理学，驱动多模态大模型输出时尚杂志级的高定骨相解构报告。

### 核心亮点
- **478 稠密关键点量测**：MediaPipe Face Mesh 亚像素级打点，2D 头部姿态去倾斜校准（De-roll）；
- **全套科学相学量度**：三庭精微比率、下颌收拢折角、外眦飞扬势、五眼内眦间距比、财帛中岳鼻翼丰隆比、唇形厚度比；
- **自适应 RAG 知识检索**：根据实测几何特征自动合成检索探针，从本地轻量知识库召回权威依据注入大模型上下文；
- **前端动态模型配置**：支持在小程序前端直接在线配置任何兼容 OpenAI 协议的模型（默认预置 DeepSeek-V4.1-Flash，支持快速切换本地 Gemini-3.8-Flash 或自定义中转）；
- **多模型无缝容灾降级**：以 DeepSeek / Gemini 为主通道，国内阿里通义千问 Qwen-VL-Plus 为热备，内置极端离线装配引擎，保证 99.9% 高可用；
- **高定极简杂志风 UI**：纯净暖玉白与香槟哑光金高奢色彩体系，自适应 9:16 高清朋友圈长海报生成。

---

## 目录结构

```text
physiognomy-mp/
├── backend/                       # Python FastAPI 后端服务
│   ├── app/
│   │   ├── api/v1/                # 核心接口 (/api/v1/analyze, /api/v1/health)
│   │   ├── core/                  # 配置与异常处理
│   │   ├── prompts/               # 现代相学与心理学 Prompt 模板
│   │   ├── providers/             # DeepSeek / Gemini / Qwen 动态模型适配层
│   │   ├── schemas/               # Pydantic 强类型数据模型
│   │   └── services/              # MediaPipe 478点引擎与 RAG 知识检索
│   ├── face_landmarker.task       # MediaPipe 官方高精度模型
│   ├── Dockerfile                 # 生产环境容器构建规范 (包含 libEGL 动态库)
│   ├── requirements.txt           # Python 依赖清单
│   └── .env.example               # 环境配置模板
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
├── docker-compose.yml             # 生产环境一键编排配置
├── nginx.conf.example             # 生产环境 Nginx 反向代理参考
├── start_backend.bat              # Windows 一键启动后端
├── start_frontend.bat             # Windows 一键启动前端开发预览
├── start_mp_weixin.bat            # Windows 一键启动微信小程序编译监听
└── build_mp_weixin.bat            # 微信小程序正式生产打包脚本
```

---

## 本地开发快速启动

### 1. 后端启动 (FastAPI)

在 Windows 电脑上，直接双击根目录下的 **`start_backend.bat`** 即可。  
或手动执行：
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* 服务接口文档：`http://127.0.0.1:8000/api/v1/docs`
* 探活接口：`http://127.0.0.1:8000/api/v1/health`

### 2. 前端启动 (Uni-app)

在 Windows 电脑上，直接双击根目录下的 **`start_mp_weixin.bat`**（微信端）或 **`start_frontend.bat`**（H5端）。  
或手动执行：
```bash
cd frontend
npm install

# 微信小程序开发模式 (自动编译并输出至 dist/dev/mp-weixin)
npm run dev:mp-weixin

# 或 H5 网页开发模式 (浏览器访问 http://localhost:5173)
npm run dev:h5
```

### 3. 导入微信开发者工具调试

1. 打开 **微信开发者工具** ➔ 点击 **导入**；
2. 目录选择：`frontend/dist/dev/mp-weixin`；
3. AppID：`wxd6d00a7513f90fe9`；
4. 右上角「详情」➔「本地设置」➔ 勾选 **“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书”** 即可在模拟器中体验。

---

## 生产环境全流程部署指南

将本项目正式上线为面向全网用户的微信小程序，包含 **后端 Docker 部署** 与 **前端提审发版**。

### 一、后端 Docker 容器化部署

建议云服务器系统选择 **Ubuntu 22.04 LTS** 或 **Debian 12**，配置推荐 2核2G 或 2核4G。

#### 1. 安装 Docker 与 Docker Compose
```bash
curl -fsSL https://get.docker.com | bash
sudo systemctl enable --now docker
```

#### 2. 拉取项目源码
```bash
# 建议放置在 /opt 或用户目录下
cd /opt
sudo git clone https://github.com/duyuanfu/physiognomy-mp.git
sudo chown -R $USER:$USER /opt/physiognomy-mp
cd physiognomy-mp
```
*注：若提示 `detected dubious ownership in repository`，执行：*
```bash
git config --global --add safe.directory /opt/physiognomy-mp
```

#### 3. 配置生产环境变量
```bash
cd backend
cp .env.example .env
nano .env
```
配置大模型推理凭证（默认已预置 DeepSeek-V4.1-Flash）：
```ini
DEFAULT_PROVIDER=custom_openai
DEFAULT_API_KEY=sk-368bdbc412ea4f369721e644a0b330e2
DEFAULT_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=DeepSeek-V4.1-Flash
PRIMARY_TIMEOUT_SECONDS=35.0
```

#### 4. 使用 Docker Compose 一键构建并启动
回到项目根目录：
```bash
docker compose up -d --build
```
* 验证状态：`docker compose ps`，看到 `xiangdu-backend` 处于 `Up (healthy)` 即代表启动成功。
* 本地验证：`curl http://127.0.0.1:8000/api/v1/health` 返回 `{"status":"healthy"}`。

---

### 二、Nginx 反向代理与 HTTPS 配置

微信小程序强制要求接口走备案域名的 HTTPS 协议。

#### 1. 独立二级域名规划（推荐架构）
为相度小程序分配一个独立的二级域名，例如：**`api.yourdomain.com`**（如 `api.trythis.pw`），与服务器上的其他业务彻底解耦。

#### 2. 安装 Nginx 并配置反向代理
在服务器上安装 Nginx：
```bash
sudo apt update && sudo apt install nginx -y
```

上传你的 SSL 证书文件至 `/etc/nginx/ssl/`，然后编辑配置：
```bash
sudo nano /etc/nginx/sites-available/xiangdu
```

写入以下标准配置：
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    # 强制将 HTTP 重定向至 HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 证书文件路径
    ssl_certificate /etc/nginx/ssl/yourdomain.pem;
    ssl_certificate_key /etc/nginx/ssl/yourdomain.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ★ 关键：允许上传的照片体积上限 (设为 50M，防止微信上传大图时报 413 / socket hang up)
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # ★ 关键：大模型推理耗时缓冲 (必须拉长至 75 秒，防止 Nginx 提前切断连接)
        proxy_connect_timeout 75s;
        proxy_read_timeout 75s;
        proxy_send_timeout 75s;

        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

启用站点并重载 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/xiangdu /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

在公网浏览器访问 `https://api.yourdomain.com/api/v1/health`，出现绿色安全锁且返回 `{"status":"healthy"}` 即代表反向代理配置成功！

---

### 三、Cloudflare CDN 与 SSL 避坑指南

若你的域名接入了 Cloudflare CDN（开启了小黄云代理），必须注意以下两处设置：

1. **解决 301 死循环报错（`ERR_TOO_MANY_REDIRECTS`）**：
   * **原因**：Cloudflare 默认的 `Flexible` 模式会用 HTTP (80端口) 回源，而 Nginx 强制 301 跳转 HTTPS，两者循环踢皮球。
   * **解决**：进入 Cloudflare ➔ **「SSL/TLS」** ➔ **「概述」** ➔ 将加密模式从 `Flexible` 切换为 **「Full (完全)」**。
2. **解决证书报错 526（`Error code 526: Invalid SSL certificate`）**：
   * **原因**：若开启了 `Full (strict)`，Cloudflare 会严格校验源站证书是否包含二级域名。
   * **解决**：在 **「SSL/TLS」** 概述中保持选择 **「Full」**（不要选 Strict），或者向 Cloudflare 申请免费的 Origin CA 泛域名证书部署在 Nginx 上。
3. **避免端口覆盖规则冲突**：
   * 若 Cloudflare 中配置了指向其他容器（如 Java 8080）的 `Origin Rules`，请将规则限制为 `Hostname equals "yourdomain.com"`，确保 `api.yourdomain.com` 走正常的 443 回源端口。

---

### 四、微信公众平台合规与隐私指引 (解决 errno 112)

微信小程序在手机真机上调用摄像头或相册时，若后台未报备，会触发拦截：`chooseImage:fail api scope is not declared in the privacy agreement (errno: 112)`。

#### 1. 配置服务器合法域名
1. 登录 **[微信公众平台](https://mp.weixin.qq.com/)** 后台；
2. 进入 **「开发」** ➔ **「开发管理」** ➔ **「开发设置」** ➔ **「服务器域名」**；
3. 将你的域名添加至白名单：
   * `request合法域名`：`https://api.yourdomain.com`
   * `uploadFile合法域名`：`https://api.yourdomain.com`
   * `downloadFile合法域名`：`https://api.yourdomain.com`

#### 2. 配置《用户隐私保护指引》（100% 稳过模板）
在公众平台后台点击 **「设置」** ➔ **「基本设置」** ➔ **「服务内容声明」** ➔ **「用户隐私保护指引」** ➔ 点击 **「去更新」**，增加以下权限声明（直接复制）：

| 权限类别 | 对应接口 | 申请理由标准文案 (直接复制) |
| :--- | :--- | :--- |
| **选中的照片或视频信息** | `wx.chooseMedia` / `wx.chooseImage` | **用于用户主动上传面部清晰肖像，进行三庭比例等面部美学几何特征计算，生成个性化的现代骨相与神态美学解构报告。** |
| **摄像头** | `wx.chooseMedia` (camera) | **用于用户在光线充足环境下实时对准拍摄面部正面肖像，进行面容骨相特征点校准与美学报告生成。** |
| **保存图片或视频到相册** | `wx.saveImageToPhotosAlbum` | **用于将用户生成的专属面容骨相美学杂志长海报保存至本地手机相册，方便用户留存与自主分享。** |

*注：严禁填写任何“算命、看相、测凶吉”等封建迷信词汇，严格按照上述“美学几何计算”表述，提交后通常几分钟内自动核准通过。*

---

### 五、小程序前端生产打包与正式上线发版

#### 1. 切换生产环境接口地址
打开本地前端工程中的 `frontend/src/utils/request.ts`，将 `BASE_URL` 改为你配置好的线上生产地址：
```typescript
const BASE_URL = "https://api.yourdomain.com/api/v1";
```

#### 2. 生成正式生产打包代码
在项目根目录下双击运行 **`build_mp_weixin.bat`**（或在控制台执行 `npm run build:mp-weixin`）。  
代码将编译并高度压缩输出至：
`frontend/dist/build/mp-weixin`

#### 3. 提交审核与全量发布
1. 打开 **微信开发者工具**；
2. 导入项目目录：`frontend/dist/build/mp-weixin`；
3. 点击右上角蓝色的 **「上传」** 按钮，填写版本号（如 `1.0.0`）及发布备注；
4. 登录 **微信公众平台** ➔ **「版本管理」** ➔ 找到刚刚上传的开发版本；
5. 点击 **「提交审核」**；
6. 审核通过后（一般为 2~12 小时），点击 **「全量发布」**，即可在全网微信中搜索并使用「相度」小程序！

---

## 常见报错与踩坑排查手册

### 1. Docker 报错 `OSError: libEGL.so.1: cannot open shared object file`
* **原因**：Linux 容器环境缺失 MediaPipe 底层 C++ 依赖的 OpenGL / EGL 动态库。
* **解决**：确保 `backend/Dockerfile` 中已安装 `libgl1`, `libegl1`, `libgles2`, `libglib2.0-0`，重构容器即可：`docker compose up -d --build`。

### 2. 模拟器上传报错 `uploadFile:fail Error: socket hang up`
* **原因**：开发电脑上开启了代理软件（如 Clash、VPN），微信开发者工具内部的 Node.js 将 localhost 请求转发到了代理导致中断。
* **解决**：在微信开发者工具顶部点击 **「设置」** ➔ **「代理设置」** ➔ 勾选 **「不使用任何代理，直接连接网络」**，重编即可。

### 3. 手机真机报错 `uploadFile:fail url not in domain list`
* **解决**：在手机小程序右上角点击 **「...」** ➔ 往下拉点击 **「开发调试」**（开启后会自动重启并显示绿色 vConsole 按钮，此时强制关闭真机白名单校验）。

### 4. 手机真机报错 `uploadFile:fail fail:time out`
* **原因**：电脑 Wi-Fi 配置文件被 Windows 设为“公用网络（Public）”，导致 Windows 防火墙静默丢弃了手机发来的局域网请求。
* **解决**：在 Windows 设置中将连接的 Wi-Fi 网络类型从“公用网络”切换为 **“专用网络”**。

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源协议。
