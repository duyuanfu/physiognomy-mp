<template>
  <view class="app-root">
    <!-- 跨视图平滑适应动画转场包裹器 (首页 ➔ Loading ➔ 报告) -->
    <transition name="view-fade" mode="out-in">
      <!-- 状态 1: 首页 Hero 入口 (大画幅人像比例 + 内嵌前置取景 + 辅助线精修) -->
      <view v-if="appState === 'hero'" key="hero" class="hero-screen view-transition-enter">
        <!-- 顶部品牌导航栏与模型配置入口 -->
        <view class="hero-nav-bar">
          <view class="nav-brand-group">
            <image src="/static/logo.png" class="brand-logo-img" mode="aspectFit" />
            <view class="brand-text-col">
              <text class="brand-main">相度</text>
              <text class="brand-sub">度量骨相 · 洞见气度</text>
            </view>
          </view>

          <view class="nav-right-actions">
            <view class="nav-setting-capsule" @click="openConfigModal">
              <text class="gear-icon">⚙</text>
              <text class="setting-label">{{ activeModelShortName }}</text>
            </view>
          </view>
        </view>

        <!-- 核心主体：大尺寸 3:4 竖向人像取景卡片 (高度大于宽度，保证拍下整张脸) -->
        <view class="main-capture-card arch-card">
          <!-- A. 实时前置相机模式 (3:4 人像黄金高比 + 医美级精细辅助线) -->
          <view v-if="isCameraLive" class="embedded-camera-box">
            <!-- #ifdef MP-WEIXIN -->
            <camera
              device-position="front"
              flash="off"
              class="live-camera-view"
              @error="onCameraError"
            >
              <!-- 覆盖在实时视频流上的高对比精细辅助线 -->
              <cover-view class="camera-guideline-overlay">
                <!-- 四角金属刻度标 -->
                <cover-view class="hud-corner-mark hud-tl"></cover-view>
                <cover-view class="hud-corner-mark hud-tr"></cover-view>
                <cover-view class="hud-corner-mark hud-bl"></cover-view>
                <cover-view class="hud-corner-mark hud-br"></cover-view>

                <!-- 核心面容椭圆框与精细三庭辅助线 -->
                <cover-view class="guide-oval-ring">
                  <cover-view class="guide-axis-v"></cover-view>
                  <cover-view class="guide-h-line"></cover-view>
                  <cover-view class="guide-eye-tag">双眸水平对齐线</cover-view>
                  <cover-view class="guide-forehead-tick">额高发际</cover-view>
                  <cover-view class="guide-chin-tick">下颌托底</cover-view>
                </cover-view>
              </cover-view>
            </camera>
            <!-- #endif -->
            <!-- #ifndef MP-WEIXIN -->
            <view class="h5-camera-mock" @click="checkPrivacyAndChoose('camera')">
              <text class="capture-lead-text">点击调起前置摄像头拍摄</text>
            </view>
            <!-- #endif -->
          </view>

          <!-- B. 待机引导视窗 (3:4 大画幅人像比例) -->
          <view v-else class="capture-visual-box" @click="startEmbeddedCamera">
            <view class="visual-inner-ring">
              <!-- 四角微刻度 -->
              <view class="box-corner box-tl"></view>
              <view class="box-corner box-tr"></view>
              <view class="box-corner box-bl"></view>
              <view class="box-corner box-br"></view>

              <view class="camera-icon-circle">
                <text class="icon-camera">📷</text>
              </view>
              <text class="capture-lead-text">开启前置相机对准拍摄</text>
              <text class="capture-sub-text">竖向人像画幅 · 实时黄金辅助线</text>
            </view>
          </view>

          <!-- 按钮组 -->
          <view class="capture-btn-group">
            <button v-if="isCameraLive" class="arch-btn-primary full-btn" @click="snapPhotoFromCamera">
              <text class="btn-symbol">✦</text>
              <text>捕捉面容并解构</text>
            </button>
            <button v-else class="arch-btn-primary full-btn" @click="startEmbeddedCamera">
              <text class="btn-symbol">✦</text>
              <text>开启前置镜头拍摄</text>
            </button>

            <view class="sub-actions-row">
              <button v-if="isCameraLive" class="arch-btn-secondary sub-btn" @click="isCameraLive = false">
                <text>关闭镜头</text>
              </button>
              <button class="arch-btn-secondary sub-btn" @click="checkPrivacyAndChoose('album')">
                <text class="btn-symbol">🖼</text>
                <text>相册选择</text>
              </button>
            </view>
          </view>
        </view>

        <!-- 三大核心解构维度说明 -->
        <view class="dimensions-strip">
          <view class="dim-item">
            <text class="dim-num mono-font">01</text>
            <text class="dim-text">三庭黄金律</text>
          </view>
          <view class="dim-dot">·</view>
          <view class="dim-item">
            <text class="dim-num mono-font">02</text>
            <text class="dim-text">下颌骨相折角</text>
          </view>
          <view class="dim-dot">·</view>
          <view class="dim-item">
            <text class="dim-num mono-font">03</text>
            <text class="dim-text">采听耳相神采</text>
          </view>
        </view>

        <!-- 底部安全与合规声明 -->
        <view class="privacy-footer">
          <text class="lock-icon">🔒</text>
          <text class="privacy-label">面容特征仅用于实时量测 · 不做底片留存 · 严守隐私</text>
        </view>
      </view>

      <!-- 状态 2: 扫描仪式感动效 (带平滑过渡与入场浮动) -->
      <view v-else-if="appState === 'scanning'" key="scanning" class="view-transition-enter">
        <ScanCeremonyOverlay :imageSrc="selectedImage" />
      </view>

      <!-- 状态 3: 杂志级解读报告呈现 (带优雅层叠滑入过渡动效) -->
      <view v-else-if="appState === 'report' && reportData" key="report" class="view-transition-enter">
        <EditorialReportCard
          :imageSrc="selectedImage"
          :metrics="reportData.metrics"
          :report="reportData.report"
          :providerUsed="reportData.provider_used"
          @export-poster="handleExportPoster"
          @re-test="resetToHero"
        />
      </view>
    </transition>

    <!-- 前端统一多厂商模型配置弹窗 (预置厂商选择 + 兜底提示) -->
    <view v-if="showConfigModal" class="config-modal-mask">
      <view class="config-modal-card arch-card">
        <view class="modal-header">
          <view class="modal-title-group">
            <text class="modal-title arch-heading">大模型与推理接口配置</text>
            <text class="modal-desc">内置多厂商快速切换 · 支持任意 OpenAI 兼容接口</text>
          </view>
          <text class="modal-close-x" @click="showConfigModal = false">✕</text>
        </view>

        <!-- 厂商一键预设选择卡片 -->
        <view class="vendor-selector-row">
          <view
            class="vendor-pill"
            :class="{ 'vendor-active': selectedVendor === 'deepseek' }"
            @click="selectVendor('deepseek')"
          >DeepSeek 官方</view>
          <view
            class="vendor-pill"
            :class="{ 'vendor-active': selectedVendor === 'gemini' }"
            @click="selectVendor('gemini')"
          >Google Gemini</view>
          <view
            class="vendor-pill"
            :class="{ 'vendor-active': selectedVendor === 'qwen' }"
            @click="selectVendor('qwen')"
          >阿里通义千问</view>
          <view
            class="vendor-pill"
            :class="{ 'vendor-active': selectedVendor === 'custom' }"
            @click="selectVendor('custom')"
          >自定义接口</view>
        </view>

        <!-- 表单项 -->
        <view class="modal-form">
          <view class="form-field">
            <text class="field-label">接口地址 (Base URL)</text>
            <input
              v-model="tempConfig.baseUrl"
              class="field-input mono-font"
              placeholder="https://api.deepseek.com"
            />
          </view>

          <view class="form-field">
            <view class="field-label-row">
              <text class="field-label">API 密钥 (API Key)</text>
              <text class="field-fallback-tip">（若留空则自动使用系统内置兜底）</text>
            </view>
            <input
              v-model="tempConfig.apiKey"
              class="field-input mono-font"
              type="text"
              placeholder="可输入你的专属 sk-... 或留空"
            />
          </view>

          <view class="form-field">
            <text class="field-label">模型名称 (Model)</text>
            <input
              v-model="tempConfig.model"
              class="field-input mono-font"
              placeholder="DeepSeek-V4.1-Flash"
            />
          </view>
        </view>

        <!-- 底部按钮 -->
        <view class="modal-actions">
          <button class="arch-btn-secondary modal-btn" @click="resetToDefaultConfig">恢复默认</button>
          <button class="arch-btn-primary modal-btn" @click="saveUserConfig">保存并生效</button>
        </view>
      </view>
    </view>

    <!-- 离屏 Canvas 用于导出海报 -->
    <canvas
      canvas-id="posterCanvas"
      id="posterCanvas"
      class="hidden-poster-canvas"
      style="width: 750px; height: 1334px; position: fixed; left: -9999px; top: -9999px;"
    ></canvas>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, getCurrentInstance } from "vue";
import { onShareAppMessage, onShareTimeline } from "@dcloudio/uni-app";
import ScanCeremonyOverlay from "../../components/ScanCeremonyOverlay.vue";
import EditorialReportCard from "../../components/EditorialReportCard.vue";
import {
  analyzeFaceImage,
  getLlmConfig,
  saveLlmConfig,
  DEFAULT_LLM_CONFIG,
  LlmConfig
} from "../../utils/request";
import { drawAndSavePoster } from "../../utils/poster";
import { FacialReportResponse } from "../../types/report";

// 微信官方转发给好友
onShareAppMessage(() => {
  return {
    title: "相度 · 度量骨相，洞见气度",
    path: "/pages/index/index",
    imageUrl: "/static/logo.png"
  };
});

// 微信官方分享到朋友圈
onShareTimeline(() => {
  return {
    title: "相度 · 现代面容骨相量度与神态美学",
    query: "",
    imageUrl: "/static/logo.png"
  };
});

type AppState = "hero" | "scanning" | "report";

const appState = ref<AppState>("hero");
const selectedImage = ref<string>("");
const reportData = ref<FacialReportResponse | null>(null);

// 嵌入式前置相机
const isCameraLive = ref(false);

// 模型配置状态管理
const showConfigModal = ref(false);
const activeConfig = ref<LlmConfig>(getLlmConfig());
const tempConfig = ref<LlmConfig>({ ...activeConfig.value });
const selectedVendor = ref<"deepseek" | "gemini" | "qwen" | "custom">("deepseek");

const activeModelShortName = computed(() => {
  const m = activeConfig.value.model || "DeepSeek";
  if (m.toLowerCase().includes("deepseek")) return "DeepSeek";
  if (m.toLowerCase().includes("gemini")) return "Gemini";
  if (m.toLowerCase().includes("qwen")) return "Qwen";
  return m.slice(0, 10);
});

function openConfigModal() {
  tempConfig.value = { ...activeConfig.value };
  showConfigModal.value = true;
}

function selectVendor(type: "deepseek" | "gemini" | "qwen" | "custom") {
  selectedVendor.value = type;
  if (type === "deepseek") {
    tempConfig.value.baseUrl = "https://api.deepseek.com";
    tempConfig.value.model = "DeepSeek-V4.1-Flash";
  } else if (type === "gemini") {
    tempConfig.value.baseUrl = "http://localhost:8045/v1";
    tempConfig.value.model = "gemini-3.8-flash";
  } else if (type === "qwen") {
    tempConfig.value.baseUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1";
    tempConfig.value.model = "qwen-vl-plus";
  }
}

function resetToDefaultConfig() {
  tempConfig.value = { ...DEFAULT_LLM_CONFIG };
  selectedVendor.value = "deepseek";
}

function saveUserConfig() {
  activeConfig.value = { ...tempConfig.value };
  saveLlmConfig(activeConfig.value);
  showConfigModal.value = false;
  uni.showToast({ title: "模型配置已更新生效", icon: "success" });
}

const instance = getCurrentInstance();

function resetToHero() {
  selectedImage.value = "";
  reportData.value = null;
  isCameraLive.value = false;
  appState.value = "hero";
}

// 开启嵌入式前置原生相机
function startEmbeddedCamera() {
  // #ifdef MP-WEIXIN
  uni.authorize({
    scope: "scope.camera",
    success: () => {
      isCameraLive.value = true;
    },
    fail: () => {
      checkPrivacyAndChoose("camera");
    }
  });
  // #endif
  // #ifndef MP-WEIXIN
  checkPrivacyAndChoose("camera");
  // #endif
}

function onCameraError() {
  isCameraLive.value = false;
  checkPrivacyAndChoose("camera");
}

// 抓拍高清人像帧
function snapPhotoFromCamera() {
  // #ifdef MP-WEIXIN
  const cameraCtx = uni.createCameraContext();
  if (cameraCtx && cameraCtx.takePhoto) {
    cameraCtx.takePhoto({
      quality: "high",
      success: (res: any) => {
        isCameraLive.value = false;
        onImageSelected(res.tempImagePath);
      },
      fail: () => {
        checkPrivacyAndChoose("camera");
      }
    });
    return;
  }
  // #endif
  checkPrivacyAndChoose("camera");
}

function checkPrivacyAndChoose(preferredSource: "album" | "camera") {
  // #ifdef MP-WEIXIN
  const wxAny = (uni as any);
  if (wxAny.getPrivacySetting) {
    wxAny.getPrivacySetting({
      success: (res: any) => {
        if (res.needAuthorization) {
          if (wxAny.requirePrivacyAuthorize) {
            wxAny.requirePrivacyAuthorize({
              success: () => {
                handleChooseImage(preferredSource);
              },
              fail: () => {
                uni.showToast({ title: "需要同意隐私协议才能拍摄选图", icon: "none" });
              }
            });
          } else {
            handleChooseImage(preferredSource);
          }
        } else {
          handleChooseImage(preferredSource);
        }
      },
      fail: () => {
        handleChooseImage(preferredSource);
      }
    });
    return;
  }
  // #endif

  handleChooseImage(preferredSource);
}

const onImageSelected = async (filePath: string) => {
  selectedImage.value = filePath;
  appState.value = "scanning";
  try {
    const response = await analyzeFaceImage(selectedImage.value);
    reportData.value = response;
    setTimeout(() => {
      appState.value = "report";
    }, 1600);
  } catch (error: any) {
    uni.showModal({
      title: "解构提醒",
      content: error.message || "未能捕捉到清晰面部能量，请确保正视镜头重新拍摄",
      showCancel: false,
      confirmText: "重新拍摄",
      success: () => {
        appState.value = "hero";
      }
    });
  }
};

function handleChooseImage(preferredSource: "album" | "camera") {
  const sources: ("album" | "camera")[] = preferredSource === "camera" 
    ? ["camera", "album"] 
    : ["album"];

  const uniAny = uni as any;
  if (uniAny.chooseMedia) {
    uniAny.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: sources,
      camera: "front",
      success: (res: any) => {
        if (res.tempFiles && res.tempFiles.length > 0) {
          onImageSelected(res.tempFiles[0].tempFilePath);
        }
      },
      fail: (err: any) => {
        handlePickerError(err, preferredSource);
      }
    });
  } else {
    uni.chooseImage({
      count: 1,
      sizeType: ["compressed", "original"],
      sourceType: sources,
      success: (res) => {
        if (res.tempFilePaths && res.tempFilePaths.length > 0) {
          onImageSelected(res.tempFilePaths[0]);
        }
      },
      fail: (err: any) => {
        handlePickerError(err, preferredSource);
      }
    });
  }
}

function handlePickerError(err: any, preferredSource: "album" | "camera") {
  console.warn("选图/拍照捕获:", err);
  if (err.errno === 112 || (err.errMsg && err.errMsg.includes("privacy agreement"))) {
    uni.showModal({
      title: "隐私权限提示",
      content: "微信安全限制：当前小程序的【用户隐私保护指引】中尚未声明【收集照片/视频】权限。\n\n请在微信公众平台后台(mp.weixin.qq.com)「设置-基本设置-服务内容声明-用户隐私保护指引」中添加“选中的照片或视频”权限即可恢复。",
      showCancel: false,
      confirmText: "我知道了"
    });
    return;
  }
  
  if (preferredSource === "camera") {
    uni.chooseImage({
      count: 1,
      sourceType: ["album"],
      success: (res) => {
        if (res.tempFilePaths && res.tempFilePaths.length > 0) {
          selectedImage.value = res.tempFilePaths[0];
          appState.value = "scanning";
          analyzeFaceImage(selectedImage.value)
            .then(resp => {
              reportData.value = resp;
              setTimeout(() => { appState.value = "report"; }, 1600);
            })
            .catch(e => {
              uni.showToast({ title: e.message || "分析失败", icon: "none" });
              appState.value = "hero";
            });
        }
      },
      fail: () => {}
    });
  }
}

function handleExportPoster() {
  if (!reportData.value || !selectedImage.value) return;

  uni.showLoading({ title: "正在绘制高精度海报..." });
  drawAndSavePoster("posterCanvas", selectedImage.value, reportData.value, instance)
    .then(() => {
      uni.hideLoading();
    })
    .catch((err) => {
      uni.hideLoading();
      console.error("生成海报失败:", err);
    });
}
</script>

<style scoped>
.app-root {
  width: 100%;
  min-height: 100vh;
  background-color: #FBFBFC;
  box-sizing: border-box;
}

/* ★ 跨视图平滑适应动画 (空间连续性) */
.view-transition-enter {
  animation: viewFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes viewFadeIn {
  from {
    opacity: 0;
    transform: translateY(16rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 首页整体布局 */
.hero-screen {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  min-height: 100vh;
  padding: 40rpx 36rpx;
  background: #FBFBFC;
  box-sizing: border-box;
}

/* 顶部导航与配置按钮 */
.hero-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-top: 10rpx;
}

.nav-brand-group {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.brand-logo-img {
  width: 76rpx;
  height: 76rpx;
  border-radius: 18rpx;
  box-shadow: 0 4rpx 16rpx rgba(184, 144, 88, 0.22);
}

.brand-text-col {
  display: flex;
  flex-direction: column;
}

.brand-main {
  font-size: 32rpx;
  font-weight: 700;
  color: #111827;
  letter-spacing: 0.04em;
  line-height: 1.2;
}

.brand-sub {
  font-size: 18rpx;
  color: #B89058;
  letter-spacing: 0.04em;
  font-weight: 600;
  line-height: 1.2;
}

.nav-setting-capsule {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FDF9F2;
  border: 1px solid #F3E4C9;
  padding: 8rpx 20rpx;
  border-radius: 9999rpx;
  box-shadow: 0 2rpx 8rpx rgba(184, 144, 88, 0.1);
}

.nav-setting-capsule:active {
  background: #F6EDE0;
}

.gear-icon {
  font-size: 20rpx;
  color: #B89058;
}

.setting-label {
  font-size: 20rpx;
  color: #B89058;
  font-weight: 600;
}

/* 核心互动卡片 */
.main-capture-card {
  width: 100%;
  max-width: 620rpx;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  border: 1px solid #EAECEF;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.03);
}

/* ★ 待机视窗：高度大于宽度 (3:4 人像竖向黄金比)，拍下整张脸 */
.capture-visual-box {
  position: relative;
  width: 100%;
  height: 580rpx;
  background: radial-gradient(circle at center, rgba(184, 144, 88, 0.08) 0%, #FAFAF8 80%);
  border: 2rpx dashed #C5A059;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.capture-visual-box:active {
  background: radial-gradient(circle at center, rgba(184, 144, 88, 0.14) 0%, #F5F4EE 80%);
}

.visual-inner-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14rpx;
}

.box-corner {
  position: absolute;
  width: 24rpx;
  height: 24rpx;
  border-color: #B89058;
}

.box-tl { top: 16rpx; left: 16rpx; border-top: 3rpx solid #B89058; border-left: 3rpx solid #B89058; }
.box-tr { top: 16rpx; right: 16rpx; border-top: 3rpx solid #B89058; border-right: 3rpx solid #B89058; }
.box-bl { bottom: 16rpx; left: 16rpx; border-bottom: 3rpx solid #B89058; border-left: 3rpx solid #B89058; }
.box-br { bottom: 16rpx; right: 16rpx; border-bottom: 3rpx solid #B89058; border-right: 3rpx solid #B89058; }

.camera-icon-circle {
  width: 108rpx;
  height: 108rpx;
  background: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 28rpx rgba(184, 144, 88, 0.25);
  margin-bottom: 10rpx;
}

.icon-camera {
  font-size: 48rpx;
}

.capture-lead-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #111827;
}

.capture-sub-text {
  font-size: 22rpx;
  color: #6B7280;
}

/* ★ 嵌入式前置原生相机视窗 (高度扩大至 600rpx，人像比例大画幅) */
.embedded-camera-box {
  position: relative;
  width: 100%;
  height: 600rpx;
  border-radius: 16rpx;
  overflow: hidden;
  border: 2rpx solid #B89058;
  box-shadow: 0 10rpx 36rpx rgba(184, 144, 88, 0.18);
}

.live-camera-view {
  width: 100%;
  height: 100%;
}

.camera-guideline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 四角高精金属刻度 */
.hud-corner-mark {
  position: absolute;
  width: 24rpx;
  height: 24rpx;
  border-color: #B89058;
}

.hud-tl { top: 16rpx; left: 16rpx; border-top: 4rpx solid #B89058; border-left: 4rpx solid #B89058; }
.hud-tr { top: 16rpx; right: 16rpx; border-top: 4rpx solid #B89058; border-right: 4rpx solid #B89058; }
.hud-bl { bottom: 16rpx; left: 16rpx; border-bottom: 4rpx solid #B89058; border-left: 4rpx solid #B89058; }
.hud-br { bottom: 16rpx; right: 16rpx; border-bottom: 4rpx solid #B89058; border-right: 4rpx solid #B89058; }

/* 3:4 黄金人像面部轮廓引导框 */
.guide-oval-ring {
  position: relative;
  width: 380rpx;
  height: 500rpx;
  border: 2rpx dashed rgba(255, 255, 255, 0.85);
  border-radius: 190rpx / 250rpx;
  box-shadow: 0 0 20rpx rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.guide-axis-v {
  position: absolute;
  top: 0;
  left: 50%;
  width: 1px;
  height: 100%;
  background: rgba(255, 255, 255, 0.35);
}

.guide-h-line {
  position: absolute;
  top: 40%;
  left: 0;
  width: 100%;
  height: 2rpx;
  background: rgba(255, 255, 255, 0.7);
}

.guide-eye-tag {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 18rpx;
  color: #FFFFFF;
  background: rgba(0, 0, 0, 0.55);
  padding: 4rpx 14rpx;
  border-radius: 9999rpx;
}

.guide-forehead-tick {
  position: absolute;
  top: 14rpx;
  font-size: 16rpx;
  color: rgba(255, 255, 255, 0.8);
}

.guide-chin-tick {
  position: absolute;
  bottom: 14rpx;
  font-size: 16rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 按钮组 */
.capture-btn-group {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
}

.sub-actions-row {
  display: flex;
  gap: 16rpx;
  width: 100%;
}

.sub-btn {
  flex: 1;
}

.full-btn {
  width: 100%;
}

.btn-symbol {
  font-size: 24rpx;
}

/* 底部三维度说明 */
.dimensions-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18rpx;
  padding: 10rpx 0;
}

.dim-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.dim-num {
  font-size: 20rpx;
  color: #B89058;
  font-weight: 700;
}

.dim-text {
  font-size: 22rpx;
  color: #6B7280;
}

.dim-dot {
  color: #D1D5DB;
  font-size: 22rpx;
}

/* 隐私声明 */
.privacy-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  padding-bottom: 16rpx;
}

.lock-icon {
  font-size: 20rpx;
}

.privacy-label {
  font-size: 20rpx;
  color: #9CA3AF;
  letter-spacing: 0.02em;
}

/* 统一厂商选择弹窗 */
.config-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(6px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx;
  box-sizing: border-box;
}

.config-modal-card {
  width: 100%;
  max-width: 640rpx;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-title-group {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.modal-title {
  font-size: 34rpx;
  color: #111827;
}

.modal-desc {
  font-size: 20rpx;
  color: #6B7280;
}

.modal-close-x {
  font-size: 32rpx;
  color: #9CA3AF;
  padding: 8rpx;
  line-height: 1;
}

/* 多厂商快捷选项栏 */
.vendor-selector-row {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
}

.vendor-pill {
  font-size: 22rpx;
  color: #6B7280;
  background: #F4F4F6;
  border: 1px solid #EAECEF;
  padding: 10rpx 20rpx;
  border-radius: 9999rpx;
  font-weight: 500;
  transition: all 0.2s ease;
}

.vendor-active {
  color: #B89058;
  background: #FDF9F2;
  border-color: #F3E4C9;
  font-weight: 600;
  box-shadow: 0 2rpx 8rpx rgba(184, 144, 88, 0.12);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-label {
  font-size: 22rpx;
  font-weight: 600;
  color: #374151;
}

.field-fallback-tip {
  font-size: 18rpx;
  color: #B89058;
}

.field-input {
  width: 100%;
  height: 76rpx;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 24rpx;
  color: #111827;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: #B89058;
  background: #FFFFFF;
}

.modal-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 10rpx;
}

.modal-btn {
  flex: 1;
}

.hidden-poster-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
}
</style>
