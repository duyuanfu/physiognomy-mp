<template>
  <view class="report-wrapper">
    <!-- 顶部档案编号标识 -->
    <view class="dossier-bar">
      <text class="dossier-title">相度 · 骨相气韵解构档案</text>
      <text class="dossier-code mono-font">档案编号 #{{ reportId }}</text>
    </view>

    <!-- 照片与高定骨相星轨标尺图层 -->
    <FacialCaliperCanvas :imageSrc="imageSrc" :metrics="metrics" />

    <!-- 核心骨相主导型 Hero 卡片 -->
    <view class="hero-archetype-card arch-card">
      <view class="archetype-top">
        <view class="archetype-badge">
          <text class="badge-text">{{ report.summary.archetype }}</text>
        </view>
        <text class="engine-tag">{{ providerUsed.toUpperCase() }} 智能解构引擎</text>
      </view>

      <view class="aura-title arch-heading">{{ report.summary.aura_title }}</view>

      <view class="tags-cluster">
        <text v-for="(tag, i) in report.summary.tags" :key="i" class="arch-pill">{{ tag }}</text>
      </view>
    </view>

    <!-- 若大模型接口报错走兜底，展示排查定位横幅 -->
    <view v-if="llmError" class="diagnostic-alert-card">
      <view class="alert-header">
        <text class="alert-icon">⚠️</text>
        <text class="alert-title">大模型接口排查诊断</text>
      </view>
      <text class="alert-desc">{{ llmError }}</text>
    </view>

    <!-- 第一章：全局格局与骨相量度 -->
    <view class="chapter-card arch-card">
      <view class="chapter-title-row">
        <text class="chapter-num mono-font">01</text>
        <text class="chapter-name arch-heading">第一章 · 全局骨相格局量度</text>
      </view>

      <!-- 三庭黄金律可视化条形图 -->
      <view class="three-parts-module">
        <view class="module-header">
          <text class="module-title">三庭黄金律 · {{ report.structure.three_parts.ratio }}</text>
          <text class="module-verdict">{{ report.structure.three_parts.verdict }}</text>
        </view>

        <!-- 可视化三庭比例分段条 (动态匹配实测比例) -->
        <view class="ratio-bar-track">
          <view class="bar-segment seg-upper" :style="{ flex: threePartsFlex.upper }">
            <text class="seg-label">上庭</text>
          </view>
          <view class="bar-segment seg-middle" :style="{ flex: threePartsFlex.middle }">
            <text class="seg-label">中庭</text>
          </view>
          <view class="bar-segment seg-lower" :style="{ flex: threePartsFlex.lower }">
            <text class="seg-label">下庭</text>
          </view>
        </view>

        <text class="module-desc">{{ report.structure.three_parts.analysis }}</text>
      </view>

      <!-- 骨骼基底解构 -->
      <view class="info-block">
        <text class="block-title">{{ report.structure.bone_frame.title }}</text>
        <text class="block-desc">{{ report.structure.bone_frame.analysis }}</text>
      </view>

      <!-- 采听耳相佐证 -->
      <view class="ear-evidence-card">
        <view class="ear-card-header">
          <view class="ear-icon-dot"></view>
          <text class="ear-header-text">采听耳相佐证 · {{ report.structure.ear_evidence.title }}</text>
        </view>
        <text class="ear-card-desc">{{ report.structure.ear_evidence.analysis }}</text>
      </view>
    </view>

    <!-- 第二章：微观五官气韵 (深度扩充至六大微观维度) -->
    <view class="chapter-card arch-card">
      <view class="chapter-title-row">
        <text class="chapter-num mono-font">02</text>
        <text class="chapter-name arch-heading">第二章 · 微观五官气韵精析</text>
      </view>

      <view class="features-list">
        <!-- 1. 眉宇骨相 -->
        <view v-if="report.features.eyebrows" class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">眉宇骨相</text>
            <text class="feature-tag">保寿官</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.eyebrows.title }}</text>
            <text class="feature-body">{{ report.features.eyebrows.desc }}</text>
          </view>
        </view>

        <!-- 2. 眼神明澈 -->
        <view class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">眼神明澈</text>
            <text class="feature-tag">监察官</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.eyes.title }}</text>
            <text class="feature-body">{{ report.features.eyes.desc }}</text>
          </view>
        </view>

        <!-- 3. 印堂山根 -->
        <view v-if="report.features.glabella" class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">印堂山根</text>
            <text class="feature-tag">命宫根基</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.glabella.title }}</text>
            <text class="feature-body">{{ report.features.glabella.desc }}</text>
          </view>
        </view>

        <!-- 4. 鼻岳财帛 -->
        <view class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">鼻岳财帛</text>
            <text class="feature-tag">审辨官</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.nose.title }}</text>
            <text class="feature-body">{{ report.features.nose.desc }}</text>
          </view>
        </view>

        <!-- 5. 唇齿出纳 -->
        <view class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">唇齿水星</text>
            <text class="feature-tag">出纳官</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.mouth.title }}</text>
            <text class="feature-body">{{ report.features.mouth.desc }}</text>
          </view>
        </view>

        <!-- 6. 地阁下颌 -->
        <view v-if="report.features.jaw" class="feature-row">
          <view class="feature-meta">
            <text class="feature-label">地阁下颌</text>
            <text class="feature-tag">奴仆基业</text>
          </view>
          <view class="feature-detail">
            <text class="feature-headline">{{ report.features.jaw.title }}</text>
            <text class="feature-body">{{ report.features.jaw.desc }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 第三章：面部多维能量图谱 -->
    <view class="chapter-card arch-card">
      <view class="chapter-title-row">
        <text class="chapter-num mono-font">03</text>
        <text class="chapter-name arch-heading">第三章 · 四维能量气场图谱</text>
      </view>

      <view class="meters-grid">
        <view class="meter-box">
          <view class="meter-header">
            <text class="meter-name">智感洞察</text>
            <text class="meter-val mono-font">{{ report.radar_scores.intellect }}</text>
          </view>
          <view class="meter-track">
            <view class="meter-fill" :style="{ width: report.radar_scores.intellect + '%' }"></view>
          </view>
        </view>

        <view class="meter-box">
          <view class="meter-header">
            <text class="meter-name">气场边界</text>
            <text class="meter-val mono-font">{{ report.radar_scores.presence }}</text>
          </view>
          <view class="meter-track">
            <view class="meter-fill" :style="{ width: report.radar_scores.presence + '%' }"></view>
          </view>
        </view>

        <view class="meter-box">
          <view class="meter-header">
            <text class="meter-name">蓄势吸金</text>
            <text class="meter-val mono-font">{{ report.radar_scores.wealth_affinity }}</text>
          </view>
          <view class="meter-track">
            <view class="meter-fill" :style="{ width: report.radar_scores.wealth_affinity + '%' }"></view>
          </view>
        </view>

        <view class="meter-box">
          <view class="meter-header">
            <text class="meter-name">情绪自洽</text>
            <text class="meter-val mono-font">{{ report.radar_scores.equanimity }}</text>
          </view>
          <view class="meter-track">
            <view class="meter-fill" :style="{ width: report.radar_scores.equanimity + '%' }"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 第四章：现代修饰锦囊 -->
    <view class="chapter-card arch-card">
      <view class="chapter-title-row">
        <text class="chapter-num mono-font">04</text>
        <text class="chapter-name arch-heading">第四章 · 现代美学增势锦囊</text>
      </view>

      <view class="advice-stack">
        <view class="advice-item">
          <view class="advice-badge">穿搭与美学灵感</view>
          <text class="advice-body">{{ report.modern_advice.style }}</text>
        </view>

        <view class="advice-item">
          <view class="advice-badge">眼神与微表情管理</view>
          <text class="advice-body">{{ report.modern_advice.expression }}</text>
        </view>

        <view class="advice-item">
          <view class="advice-badge">情绪能量自洽</view>
          <text class="advice-body">{{ report.modern_advice.mindset }}</text>
        </view>
      </view>
    </view>

    <!-- 底部常驻浮动操作栏 -->
    <view class="report-actions">
      <button class="arch-btn-primary full-width" @click="$emit('export-poster')">
        <text class="action-btn-symbol">⤓</text>
        <text>保存高清杂志海报</text>
      </button>
      <button class="arch-btn-secondary full-width" @click="$emit('re-test')">
        <text class="action-btn-symbol">↺</text>
        <text>重新测试</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { FacialMetrics, LLMReportContent } from "../types/report";
import FacialCaliperCanvas from "./FacialCaliperCanvas.vue";

const props = defineProps<{
  imageSrc: string;
  metrics: FacialMetrics;
  report: LLMReportContent;
  providerUsed: string;
  llmError?: string;
}>();

defineEmits(["export-poster", "re-test"]);

const reportId = computed(() => {
  return Math.floor(1000 + Math.random() * 9000);
});

// 动态三庭比例权重
const threePartsFlex = computed(() => {
  const ratioStr = props.metrics?.three_parts_ratio || "1 : 1 : 1";
  const parts = ratioStr.split(":").map((s) => parseFloat(s.trim()) || 1.0);
  return {
    upper: Math.max(0.5, parts[0] || 1.0),
    middle: Math.max(0.5, parts[1] || 1.0),
    lower: Math.max(0.5, parts[2] || 1.0)
  };
});
</script>

<style scoped>
.report-wrapper {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  padding: 30rpx 32rpx;
  padding-bottom: 120rpx;
  background: #FBFBFC;
  box-sizing: border-box;
  width: 100%;
}

/* 诊断提示横幅 */
.diagnostic-alert-card {
  background: #FFFBEB;
  border: 1px solid #FDE68A;
  border-radius: 12rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.alert-icon {
  font-size: 26rpx;
}

.alert-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #B45309;
}

.alert-desc {
  font-size: 22rpx;
  color: #92400E;
  line-height: 1.5;
  word-break: break-all;
}

.dossier-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 22rpx;
  color: #6B7280;
  border-bottom: 1px solid #EAECEF;
  padding-bottom: 16rpx;
  width: 100%;
}

/* 主导型 Hero 卡片 */
.hero-archetype-card {
  border-left: 8rpx solid #B89058;
}

.archetype-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  width: 100%;
}

.archetype-badge {
  background: #FDF9F2;
  border: 1px solid #F3E4C9;
  padding: 8rpx 24rpx;
  border-radius: 9999rpx;
}

.badge-text {
  color: #B89058;
  font-size: 28rpx;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.engine-tag {
  font-size: 20rpx;
  color: #6B7280;
  background: #F6F7F9;
  padding: 6rpx 16rpx;
  border-radius: 9999rpx;
}

.aura-title {
  font-size: 40rpx;
  line-height: 1.35;
  color: #111827;
  margin-bottom: 24rpx;
}

.tags-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

/* 章节结构卡片 */
.chapter-card {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.chapter-title-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  border-bottom: 1px solid #EAECEF;
  padding-bottom: 18rpx;
  width: 100%;
}

.chapter-num {
  font-size: 24rpx;
  color: #B89058;
  font-weight: 700;
}

.chapter-name {
  font-size: 28rpx;
  color: #111827;
}

/* 三庭模块 */
.three-parts-module {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  width: 100%;
}

.module-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.module-verdict {
  font-size: 24rpx;
  color: #1F5B6A;
  font-weight: 500;
}

.ratio-bar-track {
  display: flex;
  width: 100%;
  height: 28rpx;
  background: #F6F7F9;
  border-radius: 9999rpx;
  overflow: hidden;
  margin: 6rpx 0;
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16rpx;
  font-weight: 600;
  color: #FFFFFF;
}

.seg-upper {
  flex: 1;
  background: #3B82F6;
}

.seg-middle {
  flex: 1.05;
  background: #B89058;
}

.seg-lower {
  flex: 0.95;
  background: #10B981;
}

.module-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.75;
}

/* 信息块 */
.info-block {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.block-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.block-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.75;
}

/* 耳相佐证卡片 */
.ear-evidence-card {
  background: #FDF9F2;
  border: 1px solid #F3E4C9;
  border-radius: 12rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.ear-card-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.ear-icon-dot {
  width: 12rpx;
  height: 12rpx;
  background: #B89058;
  border-radius: 50%;
}

.ear-header-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #B89058;
}

.ear-card-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
}

/* 五官拆解清单 (扩充至六大微观项) */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.feature-row {
  display: flex;
  gap: 24rpx;
  border-bottom: 1px solid #EAECEF;
  padding-bottom: 24rpx;
}

.feature-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.feature-meta {
  width: 150rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.feature-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #111827;
}

.feature-tag {
  font-size: 20rpx;
  color: #6B7280;
}

.feature-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.feature-headline {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F5B6A;
}

.feature-body {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
}

/* 能量图谱仪表 */
.meters-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  width: 100%;
}

.meter-box {
  flex: 1 1 calc(50% - 16rpx);
  min-width: 260rpx;
  background: #F6F7F9;
  border: 1px solid #EAECEF;
  border-radius: 12rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.meter-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.meter-name {
  font-size: 26rpx;
  font-weight: 500;
  color: #4B5563;
}

.meter-val {
  font-size: 40rpx;
  font-weight: 700;
  color: #111827;
}

.meter-track {
  width: 100%;
  height: 8rpx;
  background: #E5E7EB;
  border-radius: 9999rpx;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: #B89058;
  border-radius: 9999rpx;
}

/* 锦囊堆叠 */
.advice-stack {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.advice-item {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.advice-badge {
  align-self: flex-start;
  font-size: 22rpx;
  color: #1F5B6A;
  background: #F0F7F9;
  padding: 4rpx 16rpx;
  border-radius: 6rpx;
  font-weight: 600;
}

.advice-body {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.75;
}

/* 底部操作 */
.report-actions {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-top: 10rpx;
  width: 100%;
}

.action-btn-symbol {
  font-size: 32rpx;
  font-weight: bold;
}

.full-width {
  width: 100%;
}
</style>
