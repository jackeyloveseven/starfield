# Starfield 工具链与自动化探针索引 (Tools & Verification Suite)

本目录包含作品构建、自动化断言测试、独立模块引擎以及 3Blue1Brown 风格多媒体宣传片生成器。

---

## 目录索引与职责划分

### 1. 🧪 核心自动化断言探针 (Automated Probes)
每次修改核心代码后，必须通过本套探针的 100% 验证（亦在 GitHub Actions CI 中自动化运行）：

| 探针脚本 | 验证范围与核心断言 |
| :--- | :--- |
| [`verify_cores_and_ui.py`](verify_cores_and_ui.py) | 天象馆列表展开、天体核心孵化状态机、徽章计数实时更新与自适应 UI 状态 |
| [`verify_dilation.py`](verify_dilation.py) | 广义相对论史瓦西度规引力时间膨胀物理公式 $d = \sqrt{1 - r_s / r}$ 精度与专注时钟折算 |
| [`verify_skyevent.py`](verify_skyevent.py) | 伽马射线暴（GRB 0.34s 极亮闪光与 20s 环状余辉）与行星掩星的确定性光学推演 |
| [`verify_fps_and_telemetry.py`](verify_fps_and_telemetry.py) | 120Hz/144Hz 满血硬件高刷新率、性能 HUD 监视器与 Eco Cruise 巡航节能降温 |
| [`verify_thermal_and_retina.py`](verify_thermal_and_retina.py) | 移动端 2K Ultra 视网膜清晰度 (DPR 2.75x) 与黑洞着色器 GPU 负载降低 94.7% 验证 |
| [`verify_naming.py`](verify_naming.py) | 探索遭遇绑定、天象馆 3D 卡面翻转与星球自命名权 `localStorage` 原子持久化 |

---

### 2. 🎥 多媒体与数学宣传片引擎 (Multimedia & 3b1b Engine)

| 脚本 / 产物 | 功能说明 |
| :--- | :--- |
| [`generate_3b1b_promo_video.py`](generate_3b1b_promo_video.py) | **3Blue1Brown (Manim) 风格 1080p 数学宣传视频生成脚本**。基于 OpenCV + Pillow + Matplotlib MathText 渲染，自动生成 4 大数学乐章、发光公式、引力偏折光线与千纸鹤三维动力学。 |
| [`starfield_3b1b_promo.mp4`](starfield_3b1b_promo.mp4) | 生成完毕的 1080p 30fps 完整宣传视频（29.2 MB，支持在 GitHub 网页端与本地播放器直接播放）。 |

---

### 3. 🚀 构建与打包工具 (Build & Packaging)

| 工具 | 功能说明 |
| :--- | :--- |
| [`build_apk.ps1`](build_apk.ps1) | 本地一键同步 Web 资源并调用 Gradle 构建 Android Debug APK (`StarfieldFocus.apk`)。 |
| [`deploy_grok_blackhole_icon.py`](deploy_grok_blackhole_icon.py) | 部署并分发 Grok 风格黑洞视界自适应图标至 Web 清单与 Android 原生资源目录。 |
| [`generate_blackhole_icon.py`](generate_blackhole_icon.py) | 基于高斯光晕与事件视界几何生成深空奇点图标原图。 |

---

### 4. 📐 独立功能子引擎源文件 (Engine Modules)

| 模块 | 功能说明 |
| :--- | :--- |
| [`living_planet_engine.js`](living_planet_engine.js) | Three.js 3D 活体生态星球渲染引擎（大陆架多频 Simplex 噪声、双层折射水体、万木植被生态）。 |
| [`classical_music_engine.js`](classical_music_engine.js) | Web Audio API 物理建模声学合成器，演奏德彪西、萨蒂、贝多芬、巴赫、肖邦、施特劳斯等 6 大名曲。 |
| [`gamepad_touch.js`](gamepad_touch.js) | Xbox / PS5 游戏手柄 API 与移动端人体工学隐形浮动虚拟摇杆。 |
| [`fleet_customizer.js`](fleet_customizer.js) | 4 款 Procedural 折叠纸艺舰体与 4 款量子曲率尾迹定制坞。 |
| [`anomaly_scanner.js`](anomaly_scanner.js) | 15,000 空间单位巡天长程脉冲声呐雷达与示波器谐波共振破译系统。 |
| [`focus_engine.js`](focus_engine.js) | 深度融合引力时间膨胀数学模型的深空沉浸式挂机放置与专注番茄钟。 |

---

### 5. 📜 工程演进实录与历史补丁

- [`BUILD-LOG.md`](BUILD-LOG.md)：**星空核心构建与架构演进日志**，系统记录从 v1 初始脚手架至 v141 最新版本的美学升级、数学物理模型推演、性能优化与排错实录。
- `v*.py`：早期单次补丁脚本。
