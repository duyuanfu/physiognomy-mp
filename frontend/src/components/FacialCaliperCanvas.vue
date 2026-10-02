<template>
  <view class="caliper-box">
    <!-- 自然彩色照片 -->
    <image
      :src="imageSrc"
      class="portrait-img"
      mode="aspectFill"
      @load="onImageLoad"
    />

    <!-- 高定骨相轮廓与三庭几何标尺绘制层 (纯粹科学美学，不列出多余数据胶囊) -->
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

    // 坐标映射比例 (aspectFill 居中裁剪对齐算法)
    const scale = Math.max(cw / imgWidth, ch / imgHeight);
    const offsetX = (cw - imgWidth * scale) / 2;
    const offsetY = (ch - imgHeight * scale) / 2;

    function mapX(x: number) {
      return x * scale + offsetX;
    }
    function mapY(y: number) {
      return y * scale + offsetY;
    }

    // 1. 绘制细腻面部轮廓星轨线 (tracing facial contour)
    if (cp.contour_polygon && cp.contour_polygon.length > 2) {
      ctx.beginPath();
      ctx.setStrokeStyle("rgba(184, 144, 88, 0.75)");
      ctx.setLineWidth(1.5);
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

    // 2. 绘制三庭水平黄金分割横线与侧边标尺 (发际线 / 眉骨 / 鼻底 / 下巴底)
    const levels = cp.three_parts_levels;
    if (levels) {
      const yTrichion = mapY(levels.trichion_y);
      const yBrow = mapY(levels.brow_y);
      const yNose = mapY(levels.subnasale_y);
      const yMenton = mapY(levels.menton_y);

      ctx.setStrokeStyle("rgba(184, 144, 88, 0.55)");
      ctx.setLineWidth(1);

      // 横贯水平细线
      const lineLeft = 20;
      const lineRight = cw - 70;

      [yTrichion, yBrow, yNose, yMenton].forEach((y) => {
        ctx.beginPath();
        ctx.moveTo(lineLeft, y);
        ctx.lineTo(lineRight, y);
        ctx.stroke();

        // 两侧微十字端点
        ctx.beginPath();
        ctx.moveTo(lineLeft, y - 4);
        ctx.lineTo(lineLeft, y + 4);
        ctx.moveTo(lineRight, y - 4);
        ctx.lineTo(lineRight, y + 4);
        ctx.stroke();
      });

      // 右侧三庭侧标文字
      ctx.setFillStyle("#B89058");
      ctx.setFontSize(11);
      ctx.fillText("上庭", cw - 56, (yTrichion + yBrow) / 2 + 4);
      ctx.fillText("中庭", cw - 56, (yBrow + yNose) / 2 + 4);
      ctx.fillText("下庭", cw - 56, (yNose + yMenton) / 2 + 4);

      // 右侧连接弧标
      ctx.setStrokeStyle("rgba(184, 144, 88, 0.4)");
      ctx.beginPath();
      ctx.moveTo(cw - 64, yTrichion);
      ctx.lineTo(cw - 64, yMenton);
      ctx.stroke();
    }

    // 3. 双眼水平轴线与微扬指示
    if (cp.left_eye_inner && cp.left_eye_outer && cp.right_eye_inner && cp.right_eye_outer) {
      ctx.setStrokeStyle("rgba(31, 91, 106, 0.65)");
      ctx.setLineWidth(1);

      // 左眼外内眦连线
      ctx.beginPath();
      ctx.moveTo(mapX(cp.left_eye_inner[0]), mapY(cp.left_eye_inner[1]));
      ctx.lineTo(mapX(cp.left_eye_outer[0]), mapY(cp.left_eye_outer[1]));
      ctx.stroke();

      // 右眼外内眦连线
      ctx.beginPath();
      ctx.moveTo(mapX(cp.right_eye_inner[0]), mapY(cp.right_eye_inner[1]));
      ctx.lineTo(mapX(cp.right_eye_outer[0]), mapY(cp.right_eye_outer[1]));
      ctx.stroke();
    }

    // 4. 关键五官骨相定位星芒点 (瞳孔、山根、鼻尖、下巴顶、下颌折角)
    ctx.setFillStyle("#B89058");
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

      ctx.beginPath();
      ctx.arc(px, py, 2.5, 0, 2 * Math.PI);
      ctx.fill();

      // 微光外晕
      ctx.beginPath();
      ctx.setStrokeStyle("rgba(184, 144, 88, 0.35)");
      ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
      ctx.stroke();
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
