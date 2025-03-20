import cv2
import os
import numpy as np
import sys
from datetime import datetime

import json
# 生成当前时间字符串
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./log/output_{current_time}.log"
f = open(log_filename, "w", encoding="utf-8")
print(log_filename)
sys.stdout = f
SCALE_FACTOR_FILE = "scale_factors.json"


def save_scale_factors(scale_factors):
    """ 保存 scale_factors.json """
    with open(SCALE_FACTOR_FILE, "w", encoding="utf-8") as f:
        json.dump(scale_factors, f, indent=4)


def get_scale_factor(video_width, video_height):
    """ 
    获取 `scale_factor`：
    - 如果 `scale_factors.json` 里有该分辨率，直接返回
    - 否则，提示用户手动输入，并记录到 JSON 
    """
    scale_factors = load_scale_factors()
    key = f"{video_width}x{video_height}"

    if key in scale_factors:
        print(f"✅ 已找到 `{key}` 对应的 scale_factor: {scale_factors[key]}")
        return scale_factors[key]

    print(f"⚠️ 未找到 `{key}` 对应的 scale_factor，请手动输入:")
    scale_factor = float(input("请输入 scale_factor: "))
    if scale_factor != 0:
        # 记录新值
        scale_factors[key] = scale_factor
        save_scale_factors(scale_factors)
    else:
        scale_factor = None
    return scale_factor


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


def load_scale_factors():
    """ 读取 scale_factors.json，如果文件不存在则返回空字典 """
    if os.path.exists(SCALE_FACTOR_FILE):
        with open(SCALE_FACTOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def add_scale_factors(key, scale_factor):
    """ 添加新的 scale_factor """
    """ 保存 scale_factors.json """
    scale_factors = load_scale_factors()
    scale_factors[key] = scale_factor
    with open(SCALE_FACTOR_FILE, "w", encoding="utf-8") as f:
        json.dump(scale_factors, f, indent=4)


def process_video(frame_path, template_path, output_dir, threshold):
    """
    **优化版本**
    - 只遍历视频一次，缓存所有帧，避免重复读取
    - 在 **缓存帧** 上执行不同 `scale_factor` 的模板匹配
    """
    frame_name = os.path.splitext(os.path.basename(frame_path))[0]
    output_path = os.path.join(output_dir, frame_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
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

    # **多缩放匹配**
    best_scale_factor = None
    best_max_val = -1.0
    frame = cv2.imread(frame_path)
    if frame is None:
        print(f"无法读取图像: {frame_path}")
        return

    # 获取视频尺寸
    video_width = int(frame.shape[1])
    video_height = int(frame.shape[0])

    tmp_scale_factors = get_scale_factor(video_width,
                                         video_height)  # 从 JSON 读取或手动输入
    # **缩放因子范围**
    scale_factors = np.linspace(
        tmp_scale_factors - 0.01, tmp_scale_factors +
        0.01, 100) if tmp_scale_factors != None else np.linspace(0, 1, 100)
    for scale_factor in scale_factors:
        print(scale_factor, end=", ", flush=True)
        # 处理模板缩放
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        template_scaled = cv2.resize(template_bgr, (new_w, new_h),
                                     interpolation=cv2.INTER_AREA)
        gray_template = cv2.cvtColor(template_scaled, cv2.COLOR_BGR2GRAY)

        mask = create_red_mask(template_scaled)

        # 遍历缓存的帧
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_frame,
                                   gray_template,
                                   cv2.TM_CCOEFF_NORMED,
                                   mask=mask)

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 在匹配区域处绘制方框
            top_left = max_loc
            bottom_right = (top_left[0] + new_w, top_left[1] + new_h)
            frame_copy = frame.copy()
            cv2.rectangle(frame_copy, top_left, bottom_right, (0, 0, 255),
                          2)  # 绘制红色矩形

            save_path = os.path.join(output_path,
                                     f"scale_{scale_factor:.5f}.jpg")
            cv2.imwrite(save_path, frame_copy)
            print(
                f"[MATCH] scale_factor={scale_factor:.5f}, 匹配值: {max_val:.5f}, 保存至 {save_path}"
            )

        # 更新最优匹配
        if max_val > best_max_val:
            best_max_val = max_val
            best_scale_factor = scale_factor

        sys.stdout.flush()  # 强制刷新日志

    # 输出最佳匹配结果
    print("\n=== 最优匹配结果 ===")
    print(f"最优 scale_factor = {best_scale_factor:.5f}")
    print(f"匹配值 = {best_max_val:.5f}")

    if best_max_val < threshold:
        print(f"❌ 未找到匹配结果，最大匹配值: {best_max_val:.5f}")  # 未找到匹配结果
    else:
        key = f"{video_width}x{video_height}"
        add_scale_factors(key, best_scale_factor)
        print(f"✅ 已保存 scale_factor: {best_scale_factor:.5f}")


if __name__ == "__main__":
    frame_path = "./matched_frames/short_scale0.42738/frame_320.jpg"
    template_path = "./terror_shock.png"
    output_dir = "./matched_frames"
    threshold_value = 0.7

    # **优化后的一次遍历**
    process_video(frame_path, template_path, output_dir, threshold_value)

f.close
sys.stdout = sys.__stdout__
print("Done.")
print("处理完成，日志文件:", log_filename)
