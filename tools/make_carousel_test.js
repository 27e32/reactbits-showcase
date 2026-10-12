// 生成轮播预览页的测试副本（用本地 SVG 图替代 Unsplash 外链）
// 用法: node make_carousel_test.js <源html> <输出html> [mock|plain]
const fs = require('fs');
const src = process.argv[2];
const out = process.argv[3];
const mode = process.argv[4] || 'plain';

let h = fs.readFileSync(src, 'utf8');

const PHOTO_LINE = 'const photo = id => `https://images.unsplash.com/${id}?w=900&q=80&auto=format&fit=max&sat=-100`;';
if (!h.includes(PHOTO_LINE)) { console.error('未找到默认图片函数'); process.exit(1); }

const REPLACEMENT = [
  'let __ci = 0;',
  'const photo = id => {',
  '  const hue = (__ci++) * 36;',
  '  const svg = \'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900">\'',
  '    + \'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">\'',
  '    + \'<stop offset="0" stop-color="hsl(\' + hue + \',72%,58%)"/>\'',
  '    + \'<stop offset="1" stop-color="hsl(\' + ((hue + 40) % 360) + \',66%,34%)"/>\'',
  '    + \'</linearGradient></defs>\'',
  '    + \'<rect width="900" height="900" fill="url(#g)"/>\'',
  '    + \'<circle cx="450" cy="450" r="250" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="10"/>\'',
  '    + \'<circle cx="450" cy="450" r="120" fill="rgba(255,255,255,.18)"/>\'',
  '    + \'<text x="450" y="490" font-size="150" text-anchor="middle" fill="#fff" font-family="sans-serif">\' + (__ci) + \'</text>\'',
  '    + \'</svg>\';',
  '  return \'data:image/svg+xml,\' + encodeURIComponent(svg);',
  '};'
].join('\n');

h = h.replace(PHOTO_LINE, REPLACEMENT);

// 诊断：把内部状态写到左下角
h = h.replace(
  '`${items.length} 张 · 半径 ${Math.round(radius)}px · 缩放 ${fit.toFixed(2)} · ${fpsShown} FPS · 角度 ${Math.round(wrap(state.angle))}°`',
  '`图${items.length} ready=${ready} intro=${intro ? intro.type : "-"} done=${introDone} r=${Math.round(radius)} fit=${fit.toFixed(2)} 角度=${Math.round(wrap(state.angle))} 卡=${ringEl.children.length} slot=${document.querySelectorAll(".circular-carousel__card").length}`'
);
h = h.replace('if (fpsAcc > 0.5){', 'if (fpsAcc > 0.15){');

if (mode === 'mock') {
  const inject = [
    '  setItems(DEFAULT_ITEMS.slice());',
    '',
    '  /* ---- 自测：模拟用户上传 5 张本地图片 ---- */',
    '  setTimeout(function () {',
    '    try {',
    '      const mk = (label, hue) => {',
    '        const svg = \'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"><rect width="800" height="800" fill="hsl(\' + hue + \',72%,52%)\"/><text x="400" y="470" font-size="220" text-anchor="middle" fill="#fff" font-family="sans-serif">\' + label + \'</text></svg>\';',
    '        return new File([svg], \'upload-\' + label + \'.svg\', { type: \'image/svg+xml\' });',
    '      };',
    '      addFiles([mk("A", 200), mk("B", 300), mk("C", 40), mk("D", 120), mk("E", 260)]);',
    '      window.__mockUploaded = true;',
    '    } catch (err) { reportError("上传自测失败：" + err.message); }',
    '  }, 200);'
  ].join('\n');
  h = h.replace('  setItems(DEFAULT_ITEMS.slice());', inject);
}

fs.writeFileSync(out, h);
console.log('已生成 ' + out + '  (mode=' + mode + ', ' + h.length + ' 字节)');
