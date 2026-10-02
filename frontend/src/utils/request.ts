import { FacialReportResponse } from "../types/report";

// 智能自适应调度后端地址：
// 1. 微信模拟器端(devtools): 使用稳定直连的 http://127.0.0.1:8000
// 2. 手机真机端(ios/android): 自动使用同一局域网 Wi-Fi 的 http://192.168.1.21:8000
function resolveApiBaseUrl(): string {
  try {
    const sys = uni.getSystemInfoSync();
    if (sys && sys.platform === "devtools") {
      return "http://127.0.0.1:8000/api/v1";
    }
  } catch (e) {}
  return "http://192.168.1.21:8000/api/v1";
}

const BASE_URL = resolveApiBaseUrl();

// 通过 Base64 走标准 POST 请求（专门用来突破微信开发者工具本地代理对 uploadFile 的 socket 劫持）
function fallbackPostBase64(filePath: string): Promise<FacialReportResponse> {
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
          image_base64: base64Data
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
  return new Promise((resolve, reject) => {
    // 优先尝试标准 uploadFile
    uni.uploadFile({
      url: `${BASE_URL}/analyze`,
      filePath: filePath,
      name: "file",
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

        // 如果触发了微信开发工具常见的 socket hang up，立即自动无缝切换到 Base64 通道
        if (msg.includes("socket hang up") || msg.includes("ECONNRESET") || msg.includes("timeout")) {
          fallbackPostBase64(filePath)
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
