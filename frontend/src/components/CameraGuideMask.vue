<template>
  <view class="studio-wrapper">
    <!-- 顶部极简指引 -->
    <view class="guide-header">
      <text class="guide-main-title">面容对齐取景</text>
      <text class="guide-sub-title">请在自然光线下正视镜头 · 完整露出双耳与额头</text>
    </view>

    <!-- 中央纯净取景视窗 (极简清爽，去除多余噪点与虚假标语) -->
    <view class="studio-viewfinder">
      <!-- 四角极简卡尺 -->
      <view class="caliper-corner corner-tl"></view>
      <view class="caliper-corner corner-tr"></view>
      <view class="caliper-corner corner-bl"></view>
      <view class="caliper-corner corner-br"></view>

      <!-- 核心面容椭圆框 -->
      <view class="face-guide-aura">
        <view class="reticle-axis-v"></view>
        <view class="reticle-axis-h"></view>
        <!-- 仅保留眼位与下颌基准标记 -->
        <view class="guide-tag-eye">双眸水平线</view>
        <view class="guide-tag-chin">下颌托底</view>
      </view>

      <!-- 左右耳朵定位光翼 -->
      <view class="ear-wing wing-left">
        <text class="wing-bracket">‹</text>
        <text class="wing-text">左耳</text>
      </view>
      <view class="ear-wing wing-right">
        <text class="wing-text">右耳</text>
        <text class="wing-bracket">›</text>
      </view>
    </view>

    <!-- 底部双操作区：简洁明快 -->
    <view class="studio-actions-footer">
      <view class="action-btn-row">
        <button class="arch-btn-secondary flex-btn" @click="$emit('select-album')">
          <text>相册选择</text>
        </button>
        <button class="arch-btn-primary flex-btn" @click="$emit('take-photo')">
          <text>对准拍摄</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
defineEmits(["select-album", "take-photo"]);
</script>

<style scoped>
.studio-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  min-height: 100vh;
  padding: 50rpx 40rpx;
  background: #FBFBFC;
  box-sizing: border-box;
  width: 100%;
}

.guide-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  text-align: center;
  padding-top: 20rpx;
}

.guide-main-title {
  font-size: 38rpx;
  font-weight: 700;
  color: #111827;
}

.guide-sub-title {
  font-size: 24rpx;
  color: #6B7280;
}

/* 纯净取景视窗 */
.studio-viewfinder {
  position: relative;
  width: 100%;
  max-width: 580rpx;
  height: 720rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  border: 1px solid #EAECEF;
  box-shadow: 0 10rpx 36rpx rgba(0, 0, 0, 0.04);
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 四角金属卡尺标 */
.caliper-corner {
  position: absolute;
  width: 28rpx;
  height: 28rpx;
  border-color: #B89058;
}

.corner-tl {
  top: 20rpx;
  left: 20rpx;
  border-top: 4rpx solid #B89058;
  border-left: 4rpx solid #B89058;
}

.corner-tr {
  top: 20rpx;
  right: 20rpx;
  border-top: 4rpx solid #B89058;
  border-right: 4rpx solid #B89058;
}

.corner-bl {
  bottom: 20rpx;
  left: 20rpx;
  border-bottom: 4rpx solid #B89058;
  border-left: 4rpx solid #B89058;
}

.corner-br {
  bottom: 20rpx;
  right: 20rpx;
  border-bottom: 4rpx solid #B89058;
  border-right: 4rpx solid #B89058;
}

/* 核心椭圆框 */
.face-guide-aura {
  position: relative;
  width: 420rpx;
  height: 560rpx;
  border: 2rpx dashed #B89058;
  border-radius: 210rpx / 280rpx;
}

.reticle-axis-v {
  position: absolute;
  top: 0;
  left: 50%;
  width: 1px;
  height: 100%;
  background: rgba(184, 144, 88, 0.15);
}

.reticle-axis-h {
  position: absolute;
  top: 40%;
  left: 0;
  width: 100%;
  height: 1px;
  background: rgba(184, 144, 88, 0.2);
}

.guide-tag-eye {
  position: absolute;
  top: 38%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #FFFFFF;
  padding: 0 12rpx;
  font-size: 18rpx;
  color: #B89058;
}

.guide-tag-chin {
  position: absolute;
  bottom: 12rpx;
  left: 50%;
  transform: translateX(-50%);
  font-size: 18rpx;
  color: #6B7280;
}

/* 耳翼指示 */
.ear-wing {
  position: absolute;
  top: 45%;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.wing-left { left: 16rpx; }
.wing-right { right: 16rpx; }

.wing-bracket {
  font-size: 40rpx;
  color: #B89058;
  line-height: 1;
}

.wing-text {
  font-size: 18rpx;
  color: #6B7280;
}

/* 底部操作区 */
.studio-actions-footer {
  width: 100%;
  padding-bottom: 20rpx;
}

.action-btn-row {
  display: flex;
  gap: 20rpx;
  width: 100%;
}

.flex-btn {
  flex: 1;
}
</style>
