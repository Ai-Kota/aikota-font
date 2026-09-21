# aikota-font · 爱成

**aikota (爱成)** 中文开源字体库。4 种风格 · GB2312 全量 6763 字 · 曲线笔形 · 内置 hinting。

> 这是**字体库**，clone 下来直接用 `fonts/` 里的 TTF/WOFF2 即可，**无需构建、无需 Python**。
> 仓里的 `toolchain/`（生成器）是"制作这些字体的工具"，普通用户可完全忽略。

---

## 一、直接用（最常用）

字体文件都在 `fonts/`，按场景选：

| 风格 | 文件 | 特征 | 适合 |
|---|---|---|---|
| 楷体 | `fonts/aikota-c-kaiso.ttf` / `.woff2` | 起尖收顿，书法笔锋 | 正文字幕（默认） |
| 瘦金体 | `fonts/aikota-c-shouljin.ttf` / `.woff2` | 细劲笔锋 | 文艺 / 古典 |
| 圆体 | `fonts/aikota-c-yuan.ttf` / `.woff2` | 圆头笔画 | 卡通 / 儿童 |
| 美术字 | `fonts/aikota-c-art.ttf` / `.woff2` | 方正粗体 | 标题 / 封面 |

每个风格都有 `.ttf`（桌面文档/视频）和 `.woff2`（网页）两种。

### 1. 安装到系统（Windows / macOS / Linux）

把 `fonts/*.ttf` 拷进系统字体目录，安装后任意应用可选：

```bash
# Windows
copy fonts\*.ttf C:\Windows\Fonts\
# macOS
cp fonts/*.ttf ~/Library/Fonts/
# Linux
cp fonts/*.ttf ~/.local/share/fonts/ && fc-cache -fv
```

安装后字体族名：`aikota-C-Kai` / `aikota-C-Shoujin` / `aikota-C-Yuan` / `aikota-C-Art`。

### 2. 网页嵌入（WOFF2）

```html
<link rel="stylesheet" href="fonts/aikota-c-kaiso.woff2">
```

或自托管：

```css
@font-face {
  font-family: 'aikota-kaiso';
  src: url('fonts/aikota-c-kaiso.woff2') format('woff2');
  font-display: swap;
}
body { font-family: 'aikota-kaiso', sans-serif; }
```

### 3. 短视频字幕（ffmpeg / libass）

ASS 字幕的 `Fontname` 填**字体 basename（无扩展名）**：

```bash
ffmpeg -i input.mp4 -vf "subtitles=sub.ass:fontsdir=<fonts/ 路径>" output.mp4
```

ASS 示例（60px 字幕，9:16 短视频）：

```
[V4+ Styles]
Style: Default, aikota-c-kaiso, 60, &H00FFFFFF, &H00000000, 3, 0, 2
```

### 4. 文档 / 设计软件

把 `fonts/*.ttf` 拖进 Word / Figma / PS / 剪映等，或拷入系统字体目录后直接选族名。

---

## 二、许可与所有权

- **免费使用**（个人 + 商业），可嵌入分发、可派生修改。
- **禁止**：单独把字体文件当商品卖；去除 / 伪造版权声明。
- 完整条款见 [LICENSE](LICENSE) / [EULA.md](EULA.md)。
- 字体内置**隐形所有权水印**（坐标级指纹，肉眼不可见），用于泄露溯源。

---

## 三、重新生成字体（可选，开发者）

普通用户跳过这一节。仓的 `toolchain/` 是字体**生成工具**（不是字体库本身）：

```bash
pip install fonttools
python toolchain/gen_c_gb_styles.py   # 重新生成 4 风格 GB2312 全量
```

> 生成器依赖数据源 `hw_all.json`（不在仓内，见 `.gitignore`）。
> 直接使用者**不需要**这步 —— `fonts/` 里的成品已带水印，开箱即用。

### 仓目录

```
fonts/      字体库本体（直接使用）
LICENSE     自定义字体许可（所有权保留 + 有限使用）
EULA.md     版权保留条款
RELEASE.md  发版声明 + 版本时间线
brush_shape.py / layout.py / radicals.py / _patch_fix.py   笔形引擎（自有 IP 核心）
toolchain/  生成器 + 校准 + 探针（开发工具，可忽略）
data/       字表 + SHA256 清单 + 校准数据
```

---

## 四、快速核对

- 字数：GB2312 全量 6763 / 风格
- 格式：TTF + WOFF2（woff2 浏览器兼容）
- 权重：regular（hinting 优化，60px 场景 PPEM 16–72）
- 版权：权利人独有，见 LICENSE
