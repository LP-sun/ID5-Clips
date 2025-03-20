# lib.py
import os
import json
import cv2
import numpy as np
import sys
from datetime import datetime
# 全局常量：记录scale_factor数据的JSON文件
SCALE_FACTOR_FILE = "scale_factors.json"
"""
创建日志文件，返回文件名。
"""
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./log/output_{current_time}.log"
os.makedirs("./log", exist_ok=True)
f = open(log_filename, "w", encoding="utf-8")
print("日志文件:", log_filename)
sys.stdout = f


def load_scale_factors():
    """
    读取 scale_factors.json 以获取视频/图像分辨率与 scale_factor 的对应关系。
    若文件不存在，则返回空字典。
    """
    if os.path.exists(SCALE_FACTOR_FILE):
        with open(SCALE_FACTOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_scale_factors(scale_factors):
    """
    将传入的 scale_factors (dict) 写入 JSON 文件，保存分辨率 => scale_factor 的映射关系。
    """
    with open(SCALE_FACTOR_FILE, "w", encoding="utf-8") as f:
        json.dump(scale_factors, f, indent=4)


def get_scale_factor(video_width, video_height):
    """
    根据视频或图片的分辨率 (video_width x video_height)，
    获取与之对应的 scale_factor。
    若 JSON 文件里已存在该分辨率的记录，则直接返回；
    否则提示用户输入并写入 JSON。
    """
    scale_factors = load_scale_factors()
    key = f"{video_width}x{video_height}"

    if key in scale_factors:
        print(f"✅ 已找到 `{key}` 对应的 scale_factor: {scale_factors[key]}")
        return scale_factors[key]

    # 若未找到，提示用户手动输入
    print(f"⚠️ 未找到 `{key}` 的 scale_factor，请手动输入:")
    user_input = input("请输入 scale_factor(非0): ").strip()
    if not user_input:
        return None
    scale_value = float(user_input)
    if scale_value != 0:
        scale_factors[key] = scale_value
        save_scale_factors(scale_factors)
        return scale_value
    else:
        return None


def add_scale_factors(key, scale_factor):
    """
    手动添加或更新某个分辨率key对应的scale_factor，并写入JSON。
    key 例: "1280x720"
    """
    data = load_scale_factors()
    data[key] = scale_factor
    save_scale_factors(data)


def create_red_mask(template_bgr):
    """
    给定一幅BGR图像(template_bgr)，将其转换为HSV后，仅保留红色区域的像素(255)；
    其他部分置为0。可用于 cv2.matchTemplate(mask=...)。
    """
    hsv = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    return mask


def end():
    """
    结束时的清理工作：关闭日志文件。
    """
    f.close()
    sys.stdout = sys.__stdout__
    print("Done.")
    print("处理完成，日志文件:", log_filename)
