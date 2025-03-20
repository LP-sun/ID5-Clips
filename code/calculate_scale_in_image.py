# calculate_scale_in_image.py
import cv2
import os
import numpy as np
import sys
import json
from datetime import datetime
from lib import (load_scale_factors, save_scale_factors, get_scale_factor,
                 create_red_mask, add_scale_factors, end)

# 日志文件写入
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./log/output_{current_time}.log"
os.makedirs("./log", exist_ok=True)
f = open(log_filename, "w", encoding="utf-8")
print("日志文件:", log_filename)
sys.stdout = f


def process_image_find_scale(frame_path,
                             template_path,
                             output_dir,
                             threshold=0.7):
    """
    在一张图片 frame_path 上，通过多种 scale_factor 的尝试来匹配 template_path。
    目的是在已有 scale_factor 基础上微调，找到最优匹配值的 scale_factor 并保存到 JSON。
    """
    frame_name = os.path.splitext(os.path.basename(frame_path))[0]
    output_path = os.path.join(output_dir, frame_name)
    os.makedirs(output_path, exist_ok=True)

    # 读取模板
    template_rgba = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template_rgba is None:
        print(f"❌ 无法读取模板图像: {template_path}")
        return

    # 去除Alpha通道(若有)
    if template_rgba.shape[2] == 4:
        b, g, r, a = cv2.split(template_rgba)
        template_bgr = cv2.merge([b, g, r])
    else:
        template_bgr = template_rgba

    # 读取输入图
    frame = cv2.imread(frame_path)
    if frame is None:
        print(f"❌ 无法读取图像: {frame_path}")
        return

    # 获取分辨率
    video_width = frame.shape[1]
    video_height = frame.shape[0]

    # 尝试从 JSON 中获取已有 scale_factor，若没有则让用户输入
    tmp_scale = get_scale_factor(video_width, video_height)
    if tmp_scale is None:
        print("❌ 用户未提供有效scale_factor，无法进行微调。")
        return

    # 在 tmp_scale 附近小范围搜索 0.01
    scale_list = np.linspace(tmp_scale - 0.01, tmp_scale + 0.01, 50)

    best_scale_factor = None
    best_max_val = -1.0

    # 灰度化输入图
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for scale_factor in scale_list:
        # 防止无效 scale_factor
        if scale_factor <= 0:
            continue

        # 缩放模板
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        if new_w <= 1 or new_h <= 1:
            continue

        template_scaled = cv2.resize(template_bgr, (new_w, new_h),
                                     interpolation=cv2.INTER_AREA)
        gray_template = cv2.cvtColor(template_scaled, cv2.COLOR_BGR2GRAY)

        mask = create_red_mask(template_scaled)

        # matchTemplate
        result = cv2.matchTemplate(gray_frame,
                                   gray_template,
                                   cv2.TM_CCOEFF_NORMED,
                                   mask=mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 若匹配成功超过阈值，保存可视化结果
        if max_val >= threshold:
            frame_copy = frame.copy()
            top_left = max_loc
            bottom_right = (top_left[0] + new_w, top_left[1] + new_h)
            cv2.rectangle(frame_copy, top_left, bottom_right, (0, 0, 255), 2)
            save_path = os.path.join(output_path,
                                     f"scale_{scale_factor:.5f}.jpg")
            cv2.imwrite(save_path, frame_copy)
            print(
                f"[MATCH] scale_factor={scale_factor:.5f}, val={max_val:.5f}, {save_path}"
            )

        # 更新最佳
        if max_val > best_max_val:
            best_max_val = max_val
            best_scale_factor = scale_factor

    print("\n=== 最优结果 ===")
    print(f"最优 scale_factor = {best_scale_factor:.5f}")
    print(f"匹配值 = {best_max_val:.5f}")

    # 若找到有效匹配，则更新 JSON
    if best_max_val >= threshold:
        key = f"{video_width}x{video_height}"
        add_scale_factors(key, best_scale_factor)
        print(f"已更新 scale_factor={best_scale_factor:.5f} 到 JSON文件。")


if __name__ == "__main__":
    frame_path = "./matched_frames/short_scale0.42738/frame_320.jpg"
    template_path = "./terror_shock.png"
    output_dir = "./matched_frames"
    threshold_value = 0.7

    process_image_find_scale(frame_path, template_path, output_dir,
                             threshold_value)

end()
