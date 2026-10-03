<template>
  <view class="caliper-box">
    <!-- 自然彩色照片 -->
    <image
      :src="imageSrc"
      class="portrait-img"
      mode="aspectFill"
      @load="onImageLoad"
    />

    <!-- 高定骨相轮廓与三庭几何标尺绘制层 (高对比冷色调，彻底解决与肤色相近看不清的问题) -->
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

    // 1. 绘制细腻面部轮廓星轨线 (采用高对比冰川冷蓝青，彻底与暖黄肤色分离)
    if (cp.contour_polygon && cp.contour_polygon.length > 2) {
      ctx.beginPath();
      ctx.setStrokeStyle("rgba(2, 132, 199, 0.9)"); // 亮青冷蓝
      ctx.setLineWidth(1.8);
      ctx.setLineDash([5, 3], 0);

      const startPt = cp.contour_polygon[0];
      ctx.moveTo(mapX(startPt[0]), mapY(startPt[1]));
      for (let i = 1; i < cp.contour_polygon.length; i++) {
        const pt = cp.contour_polygon[i];
        ctx.lineTo(mapX(pt[0]), mapY(pt[1]));
      }
      ctx.stroke();
      ctx.setLineDash([], 0); // 恢复实线
    }

    // 2. 绘制三庭水平黄金分割标尺横线 (高对比荧光冷白带青光)
    const levels = cp.three_parts_levels;
    if (levels) {
      const yTrichion = mapY(levels.trichion_y);
      const yBrow = mapY(levels.brow_y);
      const yNose = mapY(levels.subnasale_y);
      const yMenton = mapY(levels.menton_y);

      // 横贯水平细线 (采用明亮冷青色线，清晰可见)
      const lineLeft = 16;
      const lineRight = cw - 72;

      [yTrichion, yBrow, yNose, yMenton].forEach((y) => {
        // 先画一层深色半透明阴影，再画高光线，保证无论亮肤还是暗肤都极其醒目
        ctx.setStrokeStyle("rgba(0, 0, 0, 0.35)");
        ctx.setLineWidth(2.5);
        ctx.beginPath();
        ctx.moveTo(lineLeft, y);
        ctx.lineTo(lineRight, y);
        ctx.stroke();

        ctx.setStrokeStyle("#00D2D3"); // 荧光冷青色
        ctx.setLineWidth(1.2);
        ctx.beginPath();
        ctx.moveTo(lineLeft, y);
        ctx.lineTo(lineRight, y);
        ctx.stroke();

        // 两侧微十字端点
        ctx.beginPath();
        ctx.setStrokeStyle("#00D2D3");
        ctx.moveTo(lineLeft, y - 5);
        ctx.lineTo(lineLeft, y + 5);
        ctx.moveTo(lineRight, y - 5);
        ctx.lineTo(lineRight, y + 5);
        ctx.stroke();
      });

      // 右侧三庭侧标文字 (深青底色微胶囊)
      const tags = [
        { label: "上庭", y: (yTrichion + yBrow) / 2 },
        { label: "中庭", y: (yBrow + yNose) / 2 },
        { label: "下庭", y: (yNose + yMenton) / 2 }
      ];

      tags.forEach((item) => {
        ctx.setFillStyle("rgba(15, 23, 42, 0.75)"); // 深冷灰背景块
        ctx.fillRect(cw - 64, item.y - 12, 46, 22);

        ctx.setFillStyle("#00D2D3");
        ctx.setFontSize(11);
        ctx.fillText(item.label, cw - 54, item.y + 4);
      });

      // 侧边连续基准竖线
      ctx.setStrokeStyle("rgba(0, 210, 211, 0.6)");
      ctx.setLineWidth(1.2);
      ctx.beginPath();
      ctx.moveTo(cw - 68, yTrichion);
      ctx.lineTo(cw - 68, yMenton);
      ctx.stroke();
    }

    // 3. 双眼水平轴线与微扬指示 (高清晰度对比)
    if (cp.left_eye_inner && cp.left_eye_outer && cp.right_eye_inner && cp.right_eye_outer) {
      ctx.setStrokeStyle("#38BDF8"); // 冰晶蓝
      ctx.setLineWidth(1.4);

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

    // 4. 关键五官骨相定位星芒点 (高亮珍珠白核心 + 蓝光微晕，在皮肤上对比度极强)
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

      // 外圈冷光晕
      ctx.beginPath();
      ctx.setStrokeStyle("rgba(0, 210, 211, 0.8)");
      ctx.setLineWidth(1);
      ctx.arc(px, py, 5, 0, 2 * Math.PI);
      ctx.stroke();

      // 核心高光白点
      ctx.beginPath();
      ctx.setFillStyle("#FFFFFF");
      ctx.arc(px, py, 2.5, 0, 2 * Math.PI);
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
