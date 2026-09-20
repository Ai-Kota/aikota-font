# aikota-font · 发版声明

**aikota (爱成)** 中文开源字体库 + 自研曲线笔形引擎

## 发版信息

- **首次发布**: 2026-09-20
- **权利人**: aikota 字体权利人
- **版本**: 1.0
- **仓库**: https://github.com/Ai-Kota/aikota-font （公开）
- **许可**: 自定义字体许可（所有权保留 + 有限使用许可），见 [LICENSE](LICENSE) / [EULA.md](EULA.md)

## 版本时间线（git 提交顺序 = 创作在先证据）

```
f09e208  核心引擎        brush_shape + layout + 4 风格生成器   (2026-09-20)
f914494  完整源码链      校准数据 + 几何均值管线 + SHA256 清单
5035982  探针结果        部件码点覆盖度证据
a09b096  字体库本体      fonts/ 4 风格 TTF + WOFF2 (GB2312 全量 6763 字)
44c8bdc  EULA v2.0      版权保留条款 (不可剥夺所有权)
<后续>     隐形水印       坐标级所有权指纹 (防盗溯源)
```

> 提交时间戳 + 演进顺序 = "权利人先创作、持续演进"的公开时间线。
> 任何主张"我先做的"或"开源即公有"的抗辩，与本时间线冲突。

## 内容清单

```
fonts/                    字体库本体 (直接可用, 无需构建)
├── aikota-c-kaiso.ttf/woff2     楷体   (书法笔锋, 正文字幕默认)
├── aikota-c-shouljin.ttf/woff2  瘦金体 (细劲笔锋, 文艺/古典)
├── aikota-c-yuan.ttf/woff2      圆体   (圆头笔画, 卡通/儿童)
└── aikota-c-art.ttf/woff2       美术字 (方正粗体, 标题/封面)

brush_shape.py            曲线笔形引擎 (4 风格 taper + 隐形水印)
layout.py                 摆位公式
radicals.py               部件骨架坐标
gen_c_gb_styles.py        4 风格全量生成器
EULA.md / LICENSE         许可 + 版权保留
```

## 使用方式

- **直接拿用**: `fonts/` 里的 TTF/WOFF2，安装系统字体或嵌入网页/视频即可
- **网页**: `<link rel="stylesheet" href="fonts/aikota-c-kaiso.woff2">`
- **字幕**: ffmpeg/libass，ASS 的 `Fontname` 填 `aikota-c-kaiso`
- **重新生成**（可选）: `python gen_c_gb_styles.py`（需数据源 `hw_all.json`）

## 所有权声明

aikota 字体家族全部知识产权为**权利人独有**。本许可授予的是**有限使用
许可**（免费使用、嵌入分发、派生修改），**不是所有权**。字体内置隐形
所有权水印用于泄露溯源。详见 LICENSE / EULA.md。

---
aikota (爱成) · 字体为表达，结构为公共 · 2026-09-20
