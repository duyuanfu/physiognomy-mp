<template>
  <view class="caliper-box">
    <!-- 自然彩色照片 -->
    <image
      :src="imageSrc"
      class="portrait-img"
      mode="aspectFill"
      @load="onImageLoad"
    />

    <!-- 高定骨相轮廓与五官几何标尺绘制层 (高防崩保护) -->
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
  try {
    const query = uni.createSelectorQuery().in(instance);
    query.select(".caliper-box").boundingClientRect((rect: any) => {
      if (!rect || !rect.width || !rect.height) return;

      const cw = rect.width;
      const ch = rect.height;

      const ctx = uni.createCanvasContext("blueprintCanvas", instance);
      ctx.clearRect(0, 0, cw, ch);

      const cp = props.metrics?.caliper_points;
      if (!cp) return;

      // aspectFill 居中裁剪比例映射
      const scale = Math.max(cw / (imgWidth || 1), ch / (imgHeight || 1));
      const offsetX = (cw - (imgWidth || 1) * scale) / 2;
      const offsetY = (ch - (imgHeight || 1) * scale) / 2;

      function mapX(x: number) {
        return (x || 0) * scale + offsetX;
      }
      function mapY(y: number) {
        return (y || 0) * scale + offsetY;
      }

      const COLOR_PEARL_WHITE = "rgba(255, 255, 255, 0.88)";
      const COLOR_CHAMPAGNE = "rgba(212, 175, 55, 0.75)";
      const COLOR_SHADOW = "rgba(17, 24, 39, 0.22)";

      // 1. 绘制细腻面部轮廓星轨线
      if (Array.isArray(cp.contour_polygon) && cp.contour_polygon.length > 2) {
        ctx.beginPath();
        ctx.setStrokeStyle(COLOR_PEARL_WHITE);
        ctx.setLineWidth(1.6);
        ctx.setLineDash([4, 3], 0);

        const startPt = cp.contour_polygon[0];
        if (Array.isArray(startPt)) {
          ctx.moveTo(mapX(startPt[0]), mapY(startPt[1]));
          for (let i = 1; i < cp.contour_polygon.length; i++) {
            const pt = cp.contour_polygon[i];
            if (Array.isArray(pt)) {
              ctx.lineTo(mapX(pt[0]), mapY(pt[1]));
            }
          }
          ctx.stroke();
          ctx.setLineDash([], 0);
        }
      }

      // 2. 绘制三庭水平黄金分割横线标尺
      const levels = cp.three_parts_levels;
      if (levels && levels.trichion_y != null && levels.brow_y != null) {
        const yTrichion = mapY(levels.trichion_y);
        const yBrow = mapY(levels.brow_y);
        const yNose = mapY(levels.subnasale_y);
        const yMenton = mapY(levels.menton_y);

        const lineLeft = 18;
        const lineRight = cw - 76;

        [yTrichion, yBrow, yNose, yMenton].forEach((y) => {
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

          ctx.beginPath();
          ctx.setStrokeStyle(COLOR_CHAMPAGNE);
          ctx.moveTo(lineLeft, y - 4);
          ctx.lineTo(lineLeft, y + 4);
          ctx.moveTo(lineRight, y - 4);
          ctx.lineTo(lineRight, y + 4);
          ctx.stroke();
        });

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

        ctx.setStrokeStyle("rgba(212, 175, 55, 0.5)");
        ctx.setLineWidth(1);
        ctx.beginPath();
        ctx.moveTo(cw - 72, yTrichion);
        ctx.lineTo(cw - 72, yMenton);
        ctx.stroke();
      }

      // 3. 五官辅助线
      // A. 眉骨骨相连线
      if (Array.isArray(cp.brow_peak_left) && Array.isArray(cp.brow_peak_right) && Array.isArray(cp.nasion)) {
        ctx.setStrokeStyle(COLOR_CHAMPAGNE);
        ctx.setLineWidth(1);
        ctx.beginPath();
        ctx.moveTo(mapX(cp.brow_peak_right[0]), mapY(cp.brow_peak_right[1]));
        ctx.lineTo(mapX(cp.nasion[0]), mapY(cp.nasion[1]));
        ctx.lineTo(mapX(cp.brow_peak_left[0]), mapY(cp.brow_peak_left[1]));
        ctx.stroke();
      }

      // B. 财帛中岳聚气三角
      if (Array.isArray(cp.nasion) && Array.isArray(cp.alar_left) && Array.isArray(cp.alar_right) && Array.isArray(cp.nose_tip)) {
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

      // C. 唇峰出纳弓线 (严格防空指针保护)
      if (Array.isArray(cp.lip_left) && Array.isArray(cp.lip_right) && Array.isArray(cp.lip_top)) {
        ctx.setStrokeStyle("rgba(255, 255, 255, 0.75)");
        ctx.setLineWidth(1);
        ctx.beginPath();
        ctx.moveTo(mapX(cp.lip_right[0]), mapY(cp.lip_right[1]));
        ctx.lineTo(mapX(cp.lip_top[0]), mapY(cp.lip_top[1]));
        ctx.lineTo(mapX(cp.lip_left[0]), mapY(cp.lip_left[1]));
        ctx.stroke();
      }

      // D. 双眼内外眦视轴连线
      if (Array.isArray(cp.left_eye_inner) && Array.isArray(cp.left_eye_outer) && Array.isArray(cp.right_eye_inner) && Array.isArray(cp.right_eye_outer)) {
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

      // 4. 关键骨相珍珠高光点 (严格类型守护)
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
        if (!Array.isArray(pt) || pt.length < 2) return;
        const px = mapX(pt[0]);
        const py = mapY(pt[1]);

        ctx.beginPath();
        ctx.setStrokeStyle("rgba(212, 175, 55, 0.7)");
        ctx.setLineWidth(1);
        ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.setFillStyle("#FFFFFF");
        ctx.arc(px, py, 2.2, 0, 2 * Math.PI);
        ctx.fill();
      });

      ctx.draw();
    }).exec();
  } catch (err) {
    console.warn("Facial blueprint draw caught safely:", err);
  }
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
