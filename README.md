# ID5-Clips 🎥

## 📖 项目简介 | Project Introduction
**ID5-Clips** 是一个用于**自动剪辑《第五人格》游戏录屏素材**的工具，基于 OpenCV 进行图像匹配，并支持自适应 `scale_factor` 计算，方便高效地提取关键画面。

---

## ✨ 功能 | Features
✅ **模板匹配**：自动识别录屏中指定的 UI 元素或特定画面  
✅ **自适应 `scale_factor`**：根据视频分辨率计算最佳 `scale_factor`  
✅ **日志记录**：自动生成日志，记录检测结果    

<!-- ---

## 🚀 安装 | Installation
### **1️ 克隆项目 | Clone the repository**
```sh
git clone https://github.com/LP-sun/ID5-Clips.git
cd ID5-Clips
```

## 🛠 使用 | Usage
### **1️⃣ 计算 `scale_factor` | Compute `scale_factor` for a specific resolution**
```sh
python calculate_scale_in_image.py --frame "matched_frames/sample.jpg" --template "template.png"
```

### **2️⃣ 在视频中查找特定模板 | Detect a template in a video**
```sh
python detect_template_in_video.py --video "video/gameplay.mp4" --template "template.png"
``` -->

---

## 📝 目录结构 | Project Structure
```
ID5-Clips/
├── lib.py                      # 公共函数（日志、scale_factor 计算等）
├── calculate_scale_in_image.py  # 在单张图片上计算最佳 scale_factor
├── detect_template_in_video.py  # 在视频中匹配模板
├── scale_factors.json          # 记录分辨率与 scale_factor 的映射
├── matched_frames/             # 生成的匹配帧
├── log/                        # 日志文件目录
└── video/                      # 存放视频素材
```

---

## 📌 未来计划 | Future Plans
计划在未来版本中添加更多功能，以提升 ID5-Clips 的可用性和性能：
- [ ] ✅ **支持 GPU 加速**：使用 OpenCV 的 CUDA 支持或 TensorFlow 进行更高效的匹配  
- [ ] ✅ **提升匹配准确性**：优化 `cv2.matchTemplate()` 的算法，提高检测准确率  
- [ ] ✅ **添加识别项目**：求生者恐惧值，搏命状态，双方技能状态等
- [ ] ✅ **辨别复杂情景**
- [ ] ✅ **改进日志系统**：支持更详细的日志级别（INFO、WARNING、ERROR）  
- [ ] ✅ **支持更多游戏**：扩展至《第五人格》以外的其他游戏  
- [ ] ✅ **插件化设计**：允许用户自定义模板匹配规则，适配不同游戏或需求  
- [ ] ✅ **添加 GUI 界面**：开发一个简单的图形用户界面（GUI），方便用户使用  