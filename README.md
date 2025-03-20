# ID5-Clips 🎥

## 📖 项目简介 | Project Introduction
**ID5-Clips** 是一个用于**自动剪辑《第五人格》游戏录屏素材**的工具，基于 OpenCV 进行图像匹配，并支持自适应 `scale_factor` 计算，方便高效地提取关键画面。

---

## ✨ 功能 | Features
✅ **模板匹配**：自动识别录屏中指定的 UI 元素或特定画面  
✅ **自适应 `scale_factor`**：根据视频分辨率计算最佳 `scale_factor`  
✅ **日志记录**：自动生成日志，记录检测结果  
✅ **多种优化**：支持 `mask` 过滤、Git LFS 处理大文件  

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
