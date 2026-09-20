# aikota-font · 爱成

**aikota (爱成)** 是一套可直接使用的中文开源字体库 + 自研笔形引擎。
4 种风格 · GB2312 全量 6763 字 · 曲线笔形 · hinting 优化。

## 直接拿来用（无需任何构建）

字体文件在 `fonts/` 目录，clone 后即可使用：

| 风格 | 文件 | 特征 | 适用 |
|---|---|---|---|
| 楷体 | `fonts/aikota-c-kaiso.ttf` | 起尖收顿，书法笔锋 | 正文字幕（默认） |
| 瘦金体 | `fonts/aikota-c-shouljin.ttf` | 细劲笔锋 | 文艺/古典 |
| 圆体 | `fonts/aikota-c-yuan.ttf` | 圆头笔画 | 卡通/儿童 |
| 美术字 | `fonts/aikota-c-art.ttf` | 方正粗体 | 标题/封面 |

每个风格都有 `.ttf`（文档/视频）和 `.woff2`（网页）两种格式。

### 网页嵌入

```html
<link rel="stylesheet" href="fonts/aikota-c-kaiso.woff2">
```

### 字幕烧录（ffmpeg/libass）

ASS 字幕 `Fontname` 填 `aikota-c-kaiso`（字体 basename，无扩展名）。

### 安装到系统

把 `fonts/*.ttf` 拷入系统字体目录（Windows: `C:\Windows\Fonts`），
安装后即可在任何应用里选 `aikota-C-Kai` / `aikota-C-Shoujin` 等族名。

## 许可

**aikota B/C 路线字体为自研字体**，许可见 [EULA.md](EULA.md)：

- 允许：个人/商业免费使用、嵌入文档视频网页、修改派生
- 禁止：字体文件单独作为商品出售
- 派生作品须保留本声明

> 与 Arphic/A 路线（文鼎楷书数据，Arphic Public License）区分：
> 本库**不依赖** Arphic 轮廓数据，轮廓由本引擎自有算法生成。

## 知识产权（第一性原理边界）

| 层 | 性质 | 权利 |
|---|---|---|
| 汉字结构 / 部件拆分 | 公共知识 | 无版权 |
| 笔画几何事实（位置/角度/长度） | 公共信息 | 无版权 |
| **笔形 taper 算法** (`brush_shape.py`) | **自有表达** | 自有 IP |
| **摆位公式** (`layout.py`) | **自有表达** | 自有 IP |
| 字体文件（TTF/WOFF2 轮廓） | 本引擎输出 | 自有 IP |

**证据链**：本仓 git 历史（commit 时间戳 + 代码演进）即版权证据。
- `f09e208` 核心引擎（brush_shape + layout + 4 风格生成器）
- `f914494` 完整源码链 + 校准数据 + SHA256 清单

## 目录

```
fonts/                  字体库本体（直接可用）
brush_shape.py          曲线笔形引擎（4 风格 taper）
layout.py               摆位公式
radicals.py             部件骨架坐标
_patch_fix.py           几何均值 + 笔画类型管线
gen_c_gb_styles.py      4 风格全量生成器
manifest_*.json         SHA256 校验清单
EULA.md                 许可协议
hw_all.json             (gitignore, 生成器数据源, 用户用 fonts/ 无需此文件)
```

## 重新生成字体（可选）

```bash
pip install fonttools
# 需数据源 hw_all.json (生成器依赖)
python gen_c_gb_styles.py
```

普通使用者直接用 `fonts/` 里的成品即可，无需重新生成。
