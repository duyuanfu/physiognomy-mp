<template>
  <view class="scan-wrapper">
    <view class="scan-card arch-card">
      <!-- 预览照片视窗 -->
      <view class="preview-port">
        <image :src="imageSrc" class="portrait-img" mode="aspectFill" />
        <view class="scan-beam-line"></view>
      </view>

      <!-- 进度指示 -->
      <view class="progress-section">
        <view class="progress-header">
          <text class="status-main-text">正在测算面容骨相气韵...</text>
          <text class="status-pct mono-font">{{ progressPercentage }}%</text>
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPercentage + '%' }"></view>
        </view>
        <text class="active-step-hint">{{ currentStepText }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";

defineProps<{
  imageSrc: string;
}>();

const steps = [
  "正在校准面部姿态角与三庭中轴线...",
  "正在提取颧颌折角与面部长宽比...",
  "正在测算外眦上扬势与眼裂比例...",
  "正在调取典籍知识与神态心理学...",
  "正在生成您的专属骨相解构报告..."
];

const currentStepIndex = ref(0);
let timer: any = null;

const progressPercentage = computed(() => {
  return Math.min(100, Math.round(((currentStepIndex.value + 1) / steps.length) * 100));
});

const currentStepText = computed(() => {
  return steps[currentStepIndex.value];
});

onMounted(() => {
  timer = setInterval(() => {
    if (currentStepIndex.value < steps.length - 1) {
      currentStepIndex.value++;
    }
  }, 600);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.scan-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40rpx;
  background: #FBFBFC;
  box-sizing: border-box;
}

.scan-card {
  width: 100%;
  max-width: 580rpx;
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  padding: 32rpx;
}

.preview-port {
  position: relative;
  width: 100%;
  height: 520rpx;
  border-radius: 16rpx;
  overflow: hidden;
  border: 1px solid #EAECEF;
  background: #F4F4F5;
}

.portrait-img {
  width: 100%;
  height: 100%;
  filter: contrast(102%) saturate(102%);
}

.scan-beam-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4rpx;
  background: linear-gradient(90deg, transparent, #FFFFFF, #B89058, transparent);
  box-shadow: 0 0 16rpx rgba(184, 144, 88, 0.85);
  animation: sweepAnim 2s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}

@keyframes sweepAnim {
  0% { top: 0%; }
  100% { top: 98%; }
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding-top: 8rpx;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-main-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #111827;
}

.status-pct {
  font-size: 24rpx;
  font-weight: 700;
  color: #B89058;
}

.progress-track {
  width: 100%;
  height: 8rpx;
  background: #F4F4F6;
  border-radius: 9999rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #C5A059, #A37936);
  border-radius: 9999rpx;
  transition: width 0.3s ease;
}

.active-step-hint {
  font-size: 22rpx;
  color: #6B7280;
  line-height: 1.4;
}
</style>
