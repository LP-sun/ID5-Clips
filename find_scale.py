import cv2
import os
import numpy as np
import sys
from datetime import datetime

# 生成当前时间字符串
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./log/output_{current_time}.log"
f = open(log_filename, "w", encoding="utf-8")
print(log_filename)
sys.stdout = f


def create_red_mask(template_bgr):
    """ 生成 mask，仅保留红色区域 """
    hsv = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    return mask


def process_video(video_path, template_path, output_dir, threshold,
                  scale_factors, start_frame):
    """
    **优化版本**
    - 只遍历视频一次，缓存所有帧，避免重复读取
    - 在 **缓存帧** 上执行不同 `scale_factor` 的模板匹配
    """

    # 创建输出目录
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, video_name)
    os.makedirs(output_path, exist_ok=True)

    # 读取模板
    template_rgba = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template_rgba is None:
        print(f"无法读取模板图像: {template_path}")
        return

    # 处理模板：去除 Alpha 通道，生成 mask
    if template_rgba.shape[2] == 4:
        b, g, r, a = cv2.split(template_rgba)
        template_bgr = cv2.merge([b, g, r])
    else:
        template_bgr = template_rgba

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        return

    # 缓存视频帧（避免多次遍历）
    frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count >= start_frame:
            frames.append(frame)

    cap.release()
    print(f"视频缓存完成，共 {len(frames)} 帧")

    # **多缩放匹配**
    best_scale_factor = None
    best_max_val = -1.0
    best_frame_idx = -1

    for scale_factor in scale_factors:
        # 处理模板缩放
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        template_scaled = cv2.resize(template_bgr, (new_w, new_h),
                                     interpolation=cv2.INTER_AREA)
        gray_template = cv2.cvtColor(template_scaled, cv2.COLOR_BGR2GRAY)

        mask = create_red_mask(template_scaled)

        maxmax = 0.0
        max_frame_idx = -1

        # 遍历缓存的帧
        for i, frame in enumerate(frames, start=start_frame):
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(gray_frame,
                                       gray_template,
                                       cv2.TM_CCOEFF_NORMED,
                                       mask=mask)

            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > maxmax:
                maxmax = max_val
                max_frame_idx = i

            if max_val >= threshold:
                save_path = os.path.join(
                    output_path, f"scale_{scale_factor:.5f}_frame_{i}.jpg")
                cv2.imwrite(save_path, frame)
                print(
                    f"[MATCH] scale_factor={scale_factor:.5f}, 帧 {i}, 匹配值: {max_val:.5f}, 保存至 {save_path}"
                )

        # 更新最优匹配
        if maxmax > best_max_val:
            best_max_val = maxmax
            best_scale_factor = scale_factor
            best_frame_idx = max_frame_idx

        sys.stdout.flush()  # 强制刷新日志

    # 输出最佳匹配结果
    print("\n=== 最优匹配结果 ===")
    print(f"最优 scale_factor = {best_scale_factor:.5f}")
    print(f"匹配值 = {best_max_val:.5f}")
    print(f"出现帧 = {best_frame_idx}")

    sys.stdout.close()
    sys.stdout = sys.__stdout__
    print("处理完成，日志文件:", log_filename)


if __name__ == "__main__":
    video_path = "./van/1.mp4"
    template_path = "./terror_shock.png"
    output_dir = "./matched_frames"
    threshold_value = 0.7

    # **缩放因子范围**
    scale_factors = np.linspace(0.4, 0.6, 20)

    # **优化后的一次遍历**
    process_video(video_path,
                  template_path,
                  output_dir,
                  threshold_value,
                  scale_factors,
                  start_frame=990)

f.close
sys.stdout = sys.__stdout__
print("Done.")
print(log_filename)
