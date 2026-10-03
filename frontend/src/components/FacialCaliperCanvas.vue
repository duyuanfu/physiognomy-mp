<template>
  <view class="caliper-box">
    <!-- 自然彩色照片 -->
    <image
      :src="imageSrc"
      class="portrait-img"
      mode="aspectFill"
      @load="onImageLoad"
    />

    <!-- 高定骨相轮廓与五官几何标尺绘制层 (友好型高奢雅致配色，丰富五官辅助线) -->
    <canvas
      canvas-id="blueprintCanvas"
      id="blueprintCanvas"
      class="blueprint-canvas"
    ></canvas>
  </view>
</template>

<script setup lang="ts">
import { onMounted, getCurrentInstance, watch } from "vue";
import { FacialMetrics } from "../types/report";

const props = defineProps<{
  imageSrc: string;
  metrics: FacialMetrics;
}>();

const instance = getCurrentInstance();
let imgWidth = 0;
let imgHeight = 0;

function onImageLoad(e: any) {
  if (e.detail) {
    imgWidth = e.detail.width || 1;
    imgHeight = e.detail.height || 1;
    drawFacialBlueprint();
  }
}

function drawFacialBlueprint() {
  const query = uni.createSelectorQuery().in(instance);
  query.select(".caliper-box").boundingClientRect((rect: any) => {
    if (!rect || !rect.width || !rect.height) return;

    const cw = rect.width;
    const ch = rect.height;

    const ctx = uni.createCanvasContext("blueprintCanvas", instance);
    ctx.clearRect(0, 0, cw, ch);

    const cp = props.metrics.caliper_points;
    if (!cp) return;

    // aspectFill 居中裁剪比例映射
    const scale = Math.max(cw / imgWidth, ch / imgHeight);
    const offsetX = (cw - imgWidth * scale) / 2;
    const offsetY = (ch - imgHeight * scale) / 2;

    function mapX(x: number) {
      return x * scale + offsetX;
    }
    function mapY(y: number) {
      return y * scale + offsetY;
    }

    // 友好型高级配色定义：
    // 主线：柔和微发光珍珠白 (在暖色皮肤上清晰自然、绝不刺眼)
    const COLOR_PEARL_WHITE = "rgba(255, 255, 255, 0.88)";
    // 辅线：雅致香槟金 (温润微雕)
    const COLOR_CHAMPAGNE = "rgba(212, 175, 55, 0.75)";
    // 阴影底描边：保证浅色皮肤与深色背景下均字字分明
    const COLOR_SHADOW = "rgba(17, 24, 39, 0.22)";

    // 1. 绘制细腻面部轮廓星轨线 (柔和珍珠白微虚线)
    if (cp.contour_polygon && cp.contour_polygon.length > 2) {
      ctx.beginPath();
      ctx.setStrokeStyle(COLOR_PEARL_WHITE);
      ctx.setLineWidth(1.6);
      ctx.setLineDash([4, 3], 0);

      const startPt = cp.contour_polygon[0];
      ctx.moveTo(mapX(startPt[0]), mapY(startPt[1]));
      for (let i = 1; i < cp.contour_polygon.length; i++) {
        const pt = cp.contour_polygon[i];
        ctx.lineTo(mapX(pt[0]), mapY(pt[1]));
      }
      ctx.stroke();
      ctx.setLineDash([], 0); // 恢复实线
    }

    // 2. 绘制三庭水平黄金分割横线标尺 (带深浅双层描边)
    const levels = cp.three_parts_levels;
    if (levels) {
      const yTrichion = mapY(levels.trichion_y);
      const yBrow = mapY(levels.brow_y);
      const yNose = mapY(levels.subnasale_y);
      const yMenton = mapY(levels.menton_y);

      const lineLeft = 18;
      const lineRight = cw - 76;

      [yTrichion, yBrow, yNose, yMenton].forEach((y) => {
        // 先铺一层柔和半透明深色底，再叠珍珠高光线
        ctx.setStrokeStyle(COLOR_SHADOW);
        ctx.setLineWidth(2.5);
        ctx.beginPath();
        ctx.moveTo(lineLeft, y);
        ctx.lineTo(lineRight, y);
        ctx.stroke();

        ctx.setStrokeStyle(COLOR_PEARL_WHITE);
        ctx.setLineWidth(1.2);
        ctx.beginPath();
        ctx.moveTo(lineLeft, y);
        ctx.lineTo(lineRight, y);
        ctx.stroke();

        // 左右端点微十字标
        ctx.beginPath();
        ctx.setStrokeStyle(COLOR_CHAMPAGNE);
        ctx.moveTo(lineLeft, y - 4);
        ctx.lineTo(lineLeft, y + 4);
        ctx.moveTo(lineRight, y - 4);
        ctx.lineTo(lineRight, y + 4);
        ctx.stroke();
      });

      // 右侧三庭侧标文字 (温润白底高透小胶囊)
      const tags = [
        { label: "上庭", y: (yTrichion + yBrow) / 2 },
        { label: "中庭", y: (yBrow + yNose) / 2 },
        { label: "下庭", y: (yNose + yMenton) / 2 }
      ];

      tags.forEach((item) => {
        ctx.setFillStyle("rgba(255, 255, 255, 0.92)");
        ctx.fillRect(cw - 68, item.y - 12, 48, 22);

        ctx.setStrokeStyle("rgba(212, 175, 55, 0.4)");
        ctx.strokeRect(cw - 68, item.y - 12, 48, 22);

        ctx.setFillStyle("#967032");
        ctx.setFontSize(11);
        ctx.fillText(item.label, cw - 56, item.y + 4);
      });

      // 侧边连续基准竖线
      ctx.setStrokeStyle("rgba(212, 175, 55, 0.5)");
      ctx.setLineWidth(1);
      ctx.beginPath();
      ctx.moveTo(cw - 72, yTrichion);
      ctx.lineTo(cw - 72, yMenton);
      ctx.stroke();
    }

    // 3. ★ 新增：五官精细辅助线扩充 (眉宇、鼻岳财帛三角、唇形弓线)
    // A. 眉骨骨相连线 (保寿官 · 左右眉峰至印堂)
    if (cp.brow_peak_left && cp.brow_peak_right && cp.nasion && cp.brow_peak_left[0] > 0) {
      ctx.setStrokeStyle(COLOR_CHAMPAGNE);
      ctx.setLineWidth(1);
      ctx.beginPath();
      ctx.moveTo(mapX(cp.brow_peak_right[0]), mapY(cp.brow_peak_right[1]));
      ctx.lineTo(mapX(cp.nasion[0]), mapY(cp.nasion[1]));
      ctx.lineTo(mapX(cp.brow_peak_left[0]), mapY(cp.brow_peak_left[1]));
      ctx.stroke();
    }

    // B. 财帛中岳聚气三角 (审辨官 · 山根至鼻翼及鼻尖)
    if (cp.nasion && cp.alar_left && cp.alar_right && cp.nose_tip && cp.alar_left[0] > 0) {
      ctx.setStrokeStyle("rgba(212, 175, 55, 0.65)");
      ctx.setLineWidth(1.2);
      ctx.beginPath();
      ctx.moveTo(mapX(cp.nasion[0]), mapY(cp.nasion[1]));
      ctx.lineTo(mapX(cp.alar_left[0]), mapY(cp.alar_left[1]));
      ctx.lineTo(mapX(cp.nose_tip[0]), mapY(cp.nose_tip[1]));
      ctx.lineTo(mapX(cp.alar_right[0]), mapY(cp.alar_right[1]));
      ctx.closePath();
      ctx.stroke();
    }

    // C. 唇峰出纳弓线 (出纳官 · 嘴角至唇峰)
    if (cp.lip_left && cp.lip_right && cp.lip_top && cp.lip_left[0] > 0) {
      ctx.setStrokeStyle("rgba(255, 255, 255, 0.75)");
      ctx.setLineWidth(1);
      ctx.beginPath();
      ctx.moveTo(mapX(cp.lip_r[0] || cp.lip_left[0]), mapY(cp.lip_r[1] || cp.lip_left[1]));
      ctx.lineTo(mapX(cp.lip_top[0]), mapY(cp.lip_top[1]));
      ctx.lineTo(mapX(cp.lip_l[0] || cp.lip_right[0]), mapY(cp.lip_l[1] || cp.lip_right[1]));
      ctx.stroke();
    }

    // D. 双眼内外眦视轴连线
    if (cp.left_eye_inner && cp.left_eye_outer && cp.right_eye_inner && cp.right_eye_outer) {
      ctx.setStrokeStyle(COLOR_PEARL_WHITE);
      ctx.setLineWidth(1.2);

      ctx.beginPath();
      ctx.moveTo(mapX(cp.left_eye_inner[0]), mapY(cp.left_eye_inner[1]));
      ctx.lineTo(mapX(cp.left_eye_outer[0]), mapY(cp.left_eye_outer[1]));
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(mapX(cp.right_eye_inner[0]), mapY(cp.right_eye_inner[1]));
      ctx.lineTo(mapX(cp.right_eye_outer[0]), mapY(cp.right_eye_outer[1]));
      ctx.stroke();
    }

    // 4. 关键骨相珍珠高光点 (瞳孔、山根、鼻尖、下巴顶、下颌角)
    const keyPoints = [
      cp.trichion,
      cp.menton,
      cp.jaw_left,
      cp.jaw_right,
      cp.left_eye_inner,
      cp.left_eye_outer,
      cp.right_eye_inner,
      cp.right_eye_outer,
      cp.nose_tip,
      cp.subnasale
    ];

    keyPoints.forEach((pt) => {
      if (!pt) return;
      const px = mapX(pt[0]);
      const py = mapY(pt[1]);

      // 外圈香槟光晕
      ctx.beginPath();
      ctx.setStrokeStyle("rgba(212, 175, 55, 0.7)");
      ctx.setLineWidth(1);
      ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
      ctx.stroke();

      // 核心珍珠白
      ctx.beginPath();
      ctx.setFillStyle("#FFFFFF");
      ctx.arc(px, py, 2.2, 0, 2 * Math.PI);
      ctx.fill();
    });

    ctx.draw();
  }).exec();
}

watch(
  () => props.metrics,
  () => {
    if (imgWidth > 0) {
      drawFacialBlueprint();
    }
  },
  { deep: true }
);

onMounted(() => {
  setTimeout(() => {
    if (imgWidth > 0) {
      drawFacialBlueprint();
    }
  }, 300);
});
</script>

<style scoped>
.caliper-box {
  position: relative;
  width: 100%;
  height: 600rpx;
  background: #F4F4F6;
  border-radius: 16rpx;
  overflow: hidden;
  border: 1px solid #EAECEF;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
}

.portrait-img {
  width: 100%;
  height: 100%;
}

.blueprint-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
