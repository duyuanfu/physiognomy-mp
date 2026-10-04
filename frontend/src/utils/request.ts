import { FacialReportResponse } from "../types/report";

export interface LlmConfig {
  baseUrl: string;
  apiKey: string;
  model: string;
}

// 默认配置
export const DEFAULT_LLM_CONFIG: LlmConfig = {
  baseUrl: "https://api.deepseek.com",
  apiKey: "",
  model: "deepseek-flash"
};

export function getLlmConfig(): LlmConfig {
  try {
    const saved = uni.getStorageSync("llm_config");
    if (saved && saved.baseUrl && saved.model) {
      return saved;
    }
  } catch (e) {}
  return DEFAULT_LLM_CONFIG;
}

export function saveLlmConfig(cfg: LlmConfig) {
  uni.setStorageSync("llm_config", cfg);
}

// ★ 线上云端生产统一入口 (已彻底删除 devtools 本地判断分支，全端统一请求云服务器)
const BASE_URL = "https://api.trythis.pw/api/v1";

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
            const errDetail = res.data?.detail || res.data?.message || `服务器返回异常 (HTTP ${res.statusCode})`;
            reject(new Error(errDetail));
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
        console.warn("uploadFile 异常，尝试 Base64 备用通道...", msg);

        if (msg.includes("socket hang up") || msg.includes("ECONNRESET") || msg.includes("timeout")) {
          fallbackPostBase64(filePath, cfg)
            .then(resolve)
            .catch((e) => {
              reject(new Error(e.message || "连接中断，请重试"));
            });
          return;
        }

        if (msg.includes("url in domain list") || msg.includes("not in domain list")) {
          reject(new Error("真机拦截：请在手机小程序右上角点击「...」➔ 打开「开发调试」以允许公网通信"));
        } else {
          reject(new Error(msg || "网络连接异常"));
        }
      }
    });
  });
}
