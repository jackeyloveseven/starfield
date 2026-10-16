# 致谢与第三方许可

## 黑洞着色器 — MIT License

`starfield.html` 里 `GLSL_HOLE` 那段着色器（史瓦西零测地线积分、自适应步长的踢-漂-踢积分器、
赤道面多次穿越的记录方式、以及 18 点径向亮度表）移植自：

**sayed1145 / glsl-black-hole** — https://github.com/sayed1145/glsl-black-hole

原项目是 5 个 pass + 多渲染目标的独立渲染器；本作品只取了其中的物理与亮度表，
改写成一个嵌在 Canvas2D 场景里的单 pass 精灵。以下为原许可全文，按 MIT 条款要求随作品分发：

```
MIT License

Copyright (c) 2026 sayed1145

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 参考过、但未使用其代码的项目

以下项目在制作过程中作为**观感参考**读过，没有复制任何代码：

- **Haskely / Gargantua** — https://github.com/Haskely/Gargantua
  该仓库未附许可文件，因此只研究了做法，未采用其代码。
- **TheKeyDU / cosmic-flight** — https://github.com/TheKeyDU/cosmic-flight
  读了 README。其中「行星带彩色环」的思路被借鉴（思路不受版权保护，代码未使用）。
- 用户提供的 Dyson Sphere Program 官方宣传截图、星际穿越剧照、以及四张星云摄影作品，
  仅作为美术方向的参照。

## 原创部分

画面、程序化生成的全部天体与星云、折纸飞船舰队、五区带调色板、全帧后期层、
以及 `tools/` 里的整套构建与校验工具链，均为原创。

六首配乐为本地合成、内嵌在文件里，无外链、无采样素材。
