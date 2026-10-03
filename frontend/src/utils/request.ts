import { FacialReportResponse } from "../types/report";

export interface LlmConfig {
  baseUrl: string;
  apiKey: string;
  model: string;
}

// 默认配置（不内置硬编码密钥，由用户自行在设置弹窗中输入或通过后端安全环境变量读取）
export const DEFAULT_LLM_CONFIG: LlmConfig = {
  baseUrl: "https://api.deepseek.com",
  apiKey: "",
  model: "DeepSeek-V4.1-Flash"
};

export function getLlmConfig(): LlmConfig {
  try {
    const saved = uni.getStorageSync("llm_config");
    if (saved && saved.apiKey && saved.baseUrl && saved.model) {
      return saved;
    }
  } catch (e) {}
  return DEFAULT_LLM_CONFIG;
}

export function saveLlmConfig(cfg: LlmConfig) {
  uni.setStorageSync("llm_config", cfg);
}

// 智能自适应调度后端地址
function resolveApiBaseUrl(): string {
  try {
    const sys = uni.getSystemInfoSync();
    if (sys && sys.platform === "devtools") {
      return "https://api.trythis.pw/api/v1";
    }
  } catch (e) {}
  return "https://api.trythis.pw/api/v1";
}

const BASE_URL = resolveApiBaseUrl();

function fallbackPostBase64(filePath: string, cfg: LlmConfig): Promise<FacialReportResponse> {
  return new Promise((resolve, reject) => {
    try {
      const fs = (uni as any).getFileSystemManager();
      const base64Data = fs.readFileSync(filePath, "base64");

      uni.request({
        url: `${BASE_URL}/analyze`,
        method: "POST",
        header: {
          "content-type": "application/x-www-form-urlencoded"
        },
        data: {
          image_base64: base64Data,
          custom_base_url: cfg.baseUrl,
          custom_api_key: cfg.apiKey,
          custom_model: cfg.model
        },
        timeout: 60000,
        success: (res: any) => {
          if (res.statusCode === 200) {
            resolve(res.data as FacialReportResponse);
          } else {
            reject(new Error(res.data?.detail || `分析失败 (${res.statusCode})`));
          }
        },
        fail: (e: any) => {
          reject(new Error(e.errMsg || "网络请求异常"));
        }
      });
    } catch (e: any) {
      reject(new Error(e.message || "读取图片失败"));
    }
  });
}

export function analyzeFaceImage(filePath: string): Promise<FacialReportResponse> {
  const cfg = getLlmConfig();

  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${BASE_URL}/analyze`,
      filePath: filePath,
      name: "file",
      formData: {
        custom_base_url: cfg.baseUrl,
        custom_api_key: cfg.apiKey,
        custom_model: cfg.model
      },
      timeout: 60000,
      success: (uploadRes) => {
        if (uploadRes.statusCode === 200) {
          try {
            const data: FacialReportResponse = JSON.parse(uploadRes.data);
            resolve(data);
          } catch (e) {
            reject(new Error("解析服务器响应失败"));
          }
        } else {
          try {
            const err = JSON.parse(uploadRes.data);
            reject(new Error(err.detail || `分析失败 (${uploadRes.statusCode})`));
          } catch (e) {
            reject(new Error(`服务器异常 (${uploadRes.statusCode})`));
          }
        }
      },
      fail: (err) => {
        const msg = err.errMsg || "";
        console.warn("uploadFile 失败，尝试启用 Base64 备用通道...", msg);

        if (msg.includes("socket hang up") || msg.includes("ECONNRESET") || msg.includes("timeout")) {
          fallbackPostBase64(filePath, cfg)
            .then(resolve)
            .catch(() => {
              reject(new Error("连接中断：请在微信开发者工具顶部「设置」➔「代理设置」中勾选「不使用任何代理」后重试"));
            });
          return;
        }

        if (msg.includes("url in domain list") || msg.includes("not in domain list")) {
          reject(new Error("真机拦截：请在手机小程序右上角点击「...」➔ 打开「开发调试」以允许局域网调试"));
        } else {
          reject(new Error(msg || "网络连接异常"));
        }
      }
    });
  });
}
