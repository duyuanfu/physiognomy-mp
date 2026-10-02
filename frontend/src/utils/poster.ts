import { FacialReportResponse } from "../types/report";

// 智能多行自动断行绘制算法 (防止长文本超出画布边缘)
function drawWrappedText(
  ctx: any,
  text: string,
  x: number,
  startY: number,
  maxWidth: number,
  lineHeight: number,
  maxLines: number = 3
): number {
  if (!text) return startY;
  
  let currentLine = "";
  let currentY = startY;
  let lineCount = 0;

  for (let i = 0; i < text.length; i++) {
    const testLine = currentLine + text[i];
    let testWidth = 0;
    try {
      testWidth = ctx.measureText ? ctx.measureText(testLine).width : testLine.length * 13;
    } catch (e) {
      testWidth = testLine.length * 13;
    }

    if (testWidth > maxWidth && currentLine.length > 0) {
      lineCount++;
      if (lineCount >= maxLines) {
        ctx.fillText(currentLine.slice(0, -1) + "...", x, currentY);
        return currentY + lineHeight;
      }
      ctx.fillText(currentLine, x, currentY);
      currentLine = text[i];
      currentY += lineHeight;
    } else {
      currentLine = testLine;
    }
  }

  if (currentLine.length > 0) {
    ctx.fillText(currentLine, x, currentY);
    currentY += lineHeight;
  }
  return currentY;
}

export function drawAndSavePoster(
  canvasId: string,
  imageSrc: string,
  res: FacialReportResponse,
  componentInstance: any
): Promise<string> {
  return new Promise((resolve, reject) => {
    const ctx = uni.createCanvasContext(canvasId, componentInstance);
    const W = 750;
    const H = 1334;
    const paddingX = 60;
    const contentW = W - paddingX * 2;

    // 1. 纯净暖白艺术纸底色
    ctx.setFillStyle("#FAFAF8");
    ctx.fillRect(0, 0, W, H);

    // 2. 双重高定优雅边框 (外层浅灰，内层哑光淡金)
    ctx.setStrokeStyle("#EBE8E1");
    ctx.setLineWidth(2);
    ctx.strokeRect(28, 28, W - 56, H - 56);

    ctx.setStrokeStyle("rgba(184, 144, 88, 0.35)");
    ctx.setLineWidth(1);
    ctx.strokeRect(38, 38, W - 76, H - 76);

    // 3. Header 顶部卷标
    ctx.setFillStyle("#B89058");
    ctx.setFontSize(24);
    ctx.fillText("相 度", paddingX, 76);

    ctx.setFillStyle("#747068");
    ctx.setFontSize(18);
    ctx.fillText("// 度量骨相 · 洞见气度", paddingX + 70, 76);

    ctx.setFillStyle("#9CA3AF");
    ctx.setFontSize(16);
    ctx.fillText("二〇二六 · 典藏版", W - paddingX - 130, 76);

    // 4. 自然肖像呈现 (去除死板的数据遮罩条，给肖像加精致边框)
    const photoY = 100;
    const photoH = 430;
    ctx.drawImage(imageSrc, paddingX, photoY, contentW, photoH);

    // 照片四周精致细金边框
    ctx.setStrokeStyle("rgba(184, 144, 88, 0.4)");
    ctx.setLineWidth(1);
    ctx.strokeRect(paddingX, photoY, contentW, photoH);

    // 5. 骨相主导型与核心气场
    const section1Y = photoY + photoH + 40;
    ctx.setFillStyle("#B89058");
    ctx.setFontSize(26);
    ctx.fillText(`【 ${res.report.summary.archetype} 】`, paddingX, section1Y);

    ctx.setFillStyle("#111827");
    ctx.setFontSize(36);
    // 标题自动断行，防止超宽
    const titleNextY = drawWrappedText(ctx, res.report.summary.aura_title, paddingX, section1Y + 48, contentW, 44, 2);

    // 标签微胶囊
    ctx.setFillStyle("#747068");
    ctx.setFontSize(20);
    const tagsText = res.report.summary.tags.join("   ");
    ctx.fillText(tagsText, paddingX, titleNextY + 8);

    // 细分割线 1
    const div1Y = titleNextY + 32;
    ctx.setStrokeStyle("#EBE8E1");
    ctx.beginPath();
    ctx.moveTo(paddingX, div1Y);
    ctx.lineTo(W - paddingX, div1Y);
    ctx.stroke();

    // 6. 三庭黄金律与采听耳相 (带完整自动折行算法，彻底消除排版溢出截断！)
    const sec2Y = div1Y + 34;
    ctx.setFillStyle("#1F5B6A");
    ctx.setFontSize(22);
    ctx.fillText("三庭黄金律与采听耳相", paddingX, sec2Y);

    ctx.setFillStyle("#374151");
    ctx.setFontSize(23);
    const ratioFullText = `三庭比例：${res.report.structure.three_parts.ratio} · ${res.report.structure.three_parts.verdict}`;
    const afterRatioY = drawWrappedText(ctx, ratioFullText, paddingX, sec2Y + 36, contentW, 34, 2);

    ctx.setFillStyle("#4B5563");
    ctx.setFontSize(22);
    const earFullText = `采听耳相：${res.report.structure.ear_evidence.title} · ${res.report.structure.ear_evidence.analysis}`;
    const afterEarY = drawWrappedText(ctx, earFullText, paddingX, afterRatioY + 4, contentW, 32, 2);

    // 细分割线 2
    const div2Y = Math.max(afterEarY + 16, 950);
    ctx.setStrokeStyle("#EBE8E1");
    ctx.beginPath();
    ctx.moveTo(paddingX, div2Y);
    ctx.lineTo(W - paddingX, div2Y);
    ctx.stroke();

    // 7. 四维能量图谱 (采用 4 格雅致指标小卡片排布，清爽高级)
    const sec3Y = div2Y + 32;
    ctx.setFillStyle("#1F5B6A");
    ctx.setFontSize(22);
    ctx.fillText("面容高维能量图谱", paddingX, sec3Y);

    const scores = res.report.radar_scores;
    const radarItems = [
      { label: "智感洞察", val: scores.intellect },
      { label: "气场边界", val: scores.presence },
      { label: "蓄势吸金", val: scores.wealth_affinity },
      { label: "情绪自洽", val: scores.equanimity }
    ];

    const cardGap = 12;
    const cardW = (contentW - cardGap * 3) / 4;
    const cardH = 70;
    const cardTopY = sec3Y + 18;

    radarItems.forEach((item, idx) => {
      const cx = paddingX + idx * (cardW + cardGap);
      // 卡片底色
      ctx.setFillStyle("#F4F3EE");
      ctx.fillRect(cx, cardTopY, cardW, cardH);
      // 分数
      ctx.setFillStyle("#B89058");
      ctx.setFontSize(28);
      ctx.fillText(`${item.val}`, cx + 16, cardTopY + 36);
      // 标签
      ctx.setFillStyle("#6B7280");
      ctx.setFontSize(16);
      ctx.fillText(item.label, cx + 16, cardTopY + 58);
    });

    // 细分割线 3
    const div3Y = cardTopY + cardH + 28;
    ctx.setStrokeStyle("#EBE8E1");
    ctx.beginPath();
    ctx.moveTo(paddingX, div3Y);
    ctx.lineTo(W - paddingX, div3Y);
    ctx.stroke();

    // 8. 底部小程序二维码指引区 (严格水平对齐)
    const footerY = div3Y + 38;
    ctx.setFillStyle("#6B7280");
    ctx.setFontSize(20);
    ctx.fillText("扫码开启你的相度骨相解构之旅", paddingX, footerY);

    ctx.setFillStyle("#9CA3AF");
    ctx.setFontSize(16);
    ctx.fillText("客观几何量测 · 阅后即焚 · 严守隐私", paddingX, footerY + 28);

    // 小程序码方框 (右侧)
    const qrSize = 90;
    const qrX = W - paddingX - qrSize;
    const qrY = div3Y + 18;

    ctx.setStrokeStyle("#C6C1B4");
    ctx.setLineWidth(1);
    ctx.strokeRect(qrX, qrY, qrSize, qrSize);
    ctx.setFillStyle("#8C8880");
    ctx.setFontSize(16);
    ctx.fillText("小程序码", qrX + 13, qrY + 52);

    // 导出图像
    ctx.draw(false, () => {
      setTimeout(() => {
        uni.canvasToTempFilePath(
          {
            canvasId,
            success: (tempRes) => {
              uni.saveImageToPhotosAlbum({
                filePath: tempRes.tempFilePath,
                success: () => {
                  uni.showToast({ title: "海报已保存至相册", icon: "success" });
                  resolve(tempRes.tempFilePath);
                },
                fail: (err) => {
                  uni.showToast({ title: "保存失败或未授权相册", icon: "none" });
                  reject(err);
                }
              });
            },
            fail: reject
          },
          componentInstance
        );
      }, 350);
    });
  });
}
