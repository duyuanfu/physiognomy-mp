<template>
  <view class="app-root">
    <!-- 状态 1: 首页 Hero 入口 (支持前端自定义配置大模型与地址) -->
    <view v-if="appState === 'hero'" class="hero-screen">
      <!-- 顶部品牌导航栏与模型配置入口 -->
      <view class="hero-nav-bar">
        <view class="nav-brand-group">
          <!-- 官方高定 Logo -->
          <image src="/static/logo.png" class="brand-logo-img" mode="aspectFit" />
          <view class="brand-text-col">
            <text class="brand-main">相度</text>
            <text class="brand-sub">度量骨相 · 洞见气度</text>
          </view>
        </view>

        <view class="nav-right-actions">
          <!-- 齿轮模型配置按钮 -->
          <view class="nav-setting-capsule" @click="openConfigModal">
            <text class="gear-icon">⚙</text>
            <text class="setting-label">{{ activeModelShortName }}</text>
          </view>
        </view>
      </view>

      <!-- 核心主体：纯净大气的上传与拍摄互动卡片 -->
      <view class="main-capture-card arch-card">
        <view class="capture-visual-box" @click="checkPrivacyAndChoose('camera')">
          <view class="visual-inner-ring">
            <view class="camera-icon-circle">
              <text class="icon-camera">📷</text>
            </view>
            <text class="capture-lead-text">点击对准拍摄肖像</text>
            <text class="capture-sub-text">或从手机相册中选择正面照片</text>
          </view>
        </view>

        <!-- 极简双操作按钮组 -->
        <view class="capture-btn-group">
          <button class="arch-btn-primary full-btn" @click="checkPrivacyAndChoose('camera')">
            <text class="btn-symbol">✦</text>
            <text>即刻拍摄</text>
          </button>
          <button class="arch-btn-secondary full-btn" @click="checkPrivacyAndChoose('album')">
            <text class="btn-symbol">🖼</text>
            <text>相册上传</text>
          </button>
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

    <!-- 状态 2: 取景校准引导遮罩 -->
    <CameraGuideMask
      v-else-if="appState === 'guide'"
      @select-album="checkPrivacyAndChoose('album')"
      @take-photo="checkPrivacyAndChoose('camera')"
    />

    <!-- 状态 3: 扫描仪式感动效 -->
    <ScanCeremonyOverlay
      v-else-if="appState === 'scanning'"
      :imageSrc="selectedImage"
    />

    <!-- 状态 4: 杂志级解读报告呈现 -->
    <view v-else-if="appState === 'report' && reportData">
      <EditorialReportCard
        :imageSrc="selectedImage"
        :metrics="reportData.metrics"
        :report="reportData.report"
        :providerUsed="reportData.provider_used"
        @export-poster="handleExportPoster"
        @re-test="resetToHero"
      />
    </view>

    <!-- 前端自定义模型配置弹窗 (干净温润纯白弹窗) -->
    <view v-if="showConfigModal" class="config-modal-mask">
      <view class="config-modal-card arch-card">
        <view class="modal-header">
          <view class="modal-title-group">
            <text class="modal-title arch-heading">LLM 智能模型配置</text>
            <text class="modal-desc">支持自定义任何兼容 OpenAI 协议的推理接口与模型</text>
          </view>
          <text class="modal-close-x" @click="showConfigModal = false">✕</text>
        </view>

        <!-- 快速预设选项 -->
        <view class="presets-row">
          <text class="presets-title">快速配置：</text>
          <view class="preset-pill" @click="applyPreset('deepseek')">DeepSeek 官方</view>
          <view class="preset-pill" @click="applyPreset('gemini')">本地 Gemini 3.8</view>
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
            <text class="field-label">API 密钥 (API Key)</text>
            <input
              v-model="tempConfig.apiKey"
              class="field-input mono-font"
              type="text"
              placeholder="sk-..."
            />
          </view>

          <view class="form-field">
            <text class="field-label">模型名称 (Model Name)</text>
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
          <button class="arch-btn-primary modal-btn" @click="saveUserConfig">保存生效</button>
        </view>
      </view>
    </view>

    <!-- 用于导出 9:16 高清海报的离屏 Canvas -->
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
import CameraGuideMask from "../../components/CameraGuideMask.vue";
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

type AppState = "hero" | "guide" | "scanning" | "report";

const appState = ref<AppState>("hero");
const selectedImage = ref<string>("");
const reportData = ref<FacialReportResponse | null>(null);

// 模型配置状态管理
const showConfigModal = ref(false);
const activeConfig = ref<LlmConfig>(getLlmConfig());
const tempConfig = ref<LlmConfig>({ ...activeConfig.value });

const activeModelShortName = computed(() => {
  const m = activeConfig.value.model || "DeepSeek";
  if (m.toLowerCase().includes("deepseek")) return "DeepSeek-V4.1";
  if (m.toLowerCase().includes("gemini")) return "Gemini-3.8";
  return m.slice(0, 12);
});

function openConfigModal() {
  tempConfig.value = { ...activeConfig.value };
  showConfigModal.value = true;
}

function applyPreset(type: "deepseek" | "gemini") {
  if (type === "deepseek") {
    tempConfig.value = {
      baseUrl: "https://api.deepseek.com",
      apiKey: "sk-368bdbc412ea4f369721e644a0b330e2",
      model: "DeepSeek-V4.1-Flash"
    };
  } else if (type === "gemini") {
    tempConfig.value = {
      baseUrl: "http://localhost:8045/v1",
      apiKey: "sk-f9ae12d50cca49a78ce1d7241caf6570",
      model: "gemini-3.8-flash"
    };
  }
}

function resetToDefaultConfig() {
  tempConfig.value = { ...DEFAULT_LLM_CONFIG };
}

function saveUserConfig() {
  activeConfig.value = { ...tempConfig.value };
  saveLlmConfig(activeConfig.value);
  showConfigModal.value = false;
  uni.showToast({ title: "模型配置已更新生效", icon: "success" });
}

const instance = getCurrentInstance();

function enterGuideMode() {
  appState.value = "guide";
}

function resetToHero() {
  selectedImage.value = "";
  reportData.value = null;
  appState.value = "hero";
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

function handleChooseImage(preferredSource: "album" | "camera") {
  const sources: ("album" | "camera")[] = preferredSource === "camera" 
    ? ["camera", "album"] 
    : ["album"];

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

  const uniAny = uni as any;
  if (uniAny.chooseMedia) {
    uniAny.chooseMedia({
      count: 1,
      mediaType: ["image"],
      sourceType: sources,
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

/* 首页整体布局 */
.hero-screen {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  min-height: 100vh;
  padding: 50rpx 40rpx;
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

/* 顶部模型配置徽标胶囊 */
.nav-setting-capsule {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FDF9F2;
  border: 1px solid #F3E4C9;
  padding: 8rpx 20rpx;
  border-radius: 9999rpx;
  box-shadow: 0 2rpx 8rpx rgba(184, 144, 88, 0.1);
  transition: all 0.2s ease;
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
  letter-spacing: 0.02em;
}

/* 核心互动卡片 */
.main-capture-card {
  width: 100%;
  max-width: 620rpx;
  padding: 36rpx;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  border: 1px solid #EAECEF;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.03);
}

.capture-visual-box {
  width: 100%;
  height: 380rpx;
  background: radial-gradient(circle at center, rgba(184, 144, 88, 0.08) 0%, #FAFAF8 80%);
  border: 2rpx dashed #C5A059;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.capture-visual-box:active {
  background: radial-gradient(circle at center, rgba(184, 144, 88, 0.14) 0%, #F5F4EE 80%);
}

.visual-inner-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.camera-icon-circle {
  width: 96rpx;
  height: 96rpx;
  background: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 20rpx rgba(184, 144, 88, 0.2);
  margin-bottom: 8rpx;
}

.icon-camera {
  font-size: 42rpx;
}

.capture-lead-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.capture-sub-text {
  font-size: 22rpx;
  color: #6B7280;
}

/* 按钮组 */
.capture-btn-group {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  width: 100%;
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

/* 模型配置弹窗样式 */
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

/* 快速预设选项 */
.presets-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.presets-title {
  font-size: 20rpx;
  color: #6B7280;
}

.preset-pill {
  font-size: 20rpx;
  color: #B89058;
  background: #FDF9F2;
  border: 1px solid #F3E4C9;
  padding: 6rpx 16rpx;
  border-radius: 9999rpx;
  font-weight: 500;
  transition: all 0.2s ease;
}

.preset-pill:active {
  background: #F6EDE0;
}

/* 表单字段 */
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

.field-label {
  font-size: 22rpx;
  font-weight: 600;
  color: #374151;
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

/* 底部操作 */
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
