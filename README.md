### **README.md（双语，双版本）**
以下是适用于 **ID5-Clips** 项目的 `README.md`，包含中英文双版本，涵盖 **项目简介、功能、安装使用方法、贡献指南** 等。

---

## **📌 `README.md`（双语）**
```markdown
# ID5-Clips 🎥

## 📖 项目简介 | Project Introduction
**ID5-Clips** 是一个用于**自动剪辑《第五人格》游戏录屏素材**的工具，基于 OpenCV 进行图像匹配，并支持自适应 `scale_factor` 计算，方便高效地提取关键画面。

**ID5-Clips** is a tool designed for **automatically clipping Identity V gameplay recordings**. It uses OpenCV for image matching and supports adaptive `scale_factor` calculation, making it easy to extract key frames efficiently.

---

## ✨ 功能 | Features
✅ **模板匹配**：自动识别录屏中指定的 UI 元素或特定画面  
✅ **自适应 `scale_factor`**：根据视频分辨率计算最佳 `scale_factor`  
✅ **日志记录**：自动生成日志，记录检测结果  
✅ **多种优化**：支持 `mask` 过滤、Git LFS 处理大文件  

✅ **Template Matching**: Automatically detect specific UI elements or frames in gameplay recordings  
✅ **Adaptive `scale_factor` Calculation**: Computes the best `scale_factor` based on video resolution  
✅ **Logging System**: Generates logs automatically for tracking results  
✅ **Optimizations**: Supports `mask` filtering and Git LFS for large file handling  

---

## 🚀 安装 | Installation
### **1️⃣ 克隆项目 | Clone the repository**
```sh
git clone https://github.com/LP-sun/ID5-Clips.git
cd ID5-Clips
```

### **2️⃣ 创建虚拟环境（可选） | Create a virtual environment (optional)**
```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

### **3️⃣ 安装依赖 | Install dependencies**
```sh
pip install -r requirements.txt
```

---

## 🛠 使用 | Usage
### **1️⃣ 计算 `scale_factor` | Compute `scale_factor` for a specific resolution**
```sh
python calculate_scale_in_image.py --frame "matched_frames/sample.jpg" --template "template.png"
```

### **2️⃣ 在视频中查找特定模板 | Detect a template in a video**
```sh
python detect_template_in_video.py --video "video/gameplay.mp4" --template "template.png"
```

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

## 🤝 贡献 | Contributing
欢迎提交 PR、Issue，帮助改进 ID5-Clips！  
Welcome to contribute via PRs or Issues to improve ID5-Clips!

1. Fork 本仓库 | Fork this repository  
2. 创建新分支 | Create a new branch  
   ```sh
   git checkout -b feature-xyz
   ```
3. 提交更改 | Commit your changes  
   ```sh
   git commit -m "Added feature XYZ"
   ```
4. 推送分支 | Push the branch  
   ```sh
   git push origin feature-xyz
   ```
5. 提交 PR | Create a Pull Request  

---

## 📜 许可证 | License
本项目采用 **MIT License**，详情见 [`LICENSE`](LICENSE) 文件。  
This project is licensed under the **MIT License** - see the [`LICENSE`](LICENSE) file for details.

---

## ✨ 致谢 | Acknowledgments
感谢 OpenCV、GitHub 社区以及所有贡献者！  
Thanks to OpenCV, the GitHub community, and all contributors! 🎉
```

---

## **📌 README 结构概览**
1. **项目介绍（双语）**
2. **功能特点（双语）**
3. **安装步骤（双语）**
4. **使用方法（双语）**
5. **目录结构（双语）**
6. **贡献指南（双语）**
7. **许可证（双语）**
8. **致谢（双语）**

---

### **🎯 这样你的 `README.md` 既清晰直观，又能方便不同语言的用户使用！🚀**