# detect_template_in_video.py
import cv2
import os
import numpy as np
import sys
from lib import (load_scale_factors, save_scale_factors, get_scale_factor,
                 create_red_mask, end)


def find_template_in_video(video_path,
                           template_path,
                           output_dir,
                           threshold=0.6,
                           start_frame=0):
    """
    在指定视频(video_path)的每帧中搜索 template_path 的图案，
    并对匹配值 >= threshold 的帧保存到 output_dir。
    同时，会尝试根据视频的分辨率自动获取 scale_factor (若无记录则用户输入)。
    """

    print(f"[INFO] Video: {video_path}, Template: {template_path}, "
          f"Threshold={threshold}, StartFrame={start_frame}")

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频: {video_path}")
        return

    # 获取分辨率
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale_factor = get_scale_factor(video_width, video_height)
    print(f"[INFO] 使用 scale_factor={scale_factor:.5f}")

    # 读取模板
    template_rgba = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template_rgba is None:
        print(f"❌ 无法读取模板图像: {template_path}")
        return

    # 去掉Alpha通道
    if template_rgba.shape[2] == 4:
        b, g, r, a = cv2.split(template_rgba)
        template_bgr = cv2.merge([b, g, r])
    else:
        template_bgr = template_rgba

    # 若 scale_factor != 1.0，则缩放模板
    if scale_factor != 1.0:
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        template_bgr = cv2.resize(template_bgr, (new_w, new_h),
                                  interpolation=cv2.INTER_AREA)

    # 生成 mask
    mask = create_red_mask(template_bgr)

    # 转灰度
    gray_template = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    t_h, t_w = gray_template.shape[:2]

    # 输出目录
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    sub_dir = f"{video_name}_scale{scale_factor:.5f}"
    output_path = os.path.join(output_dir, sub_dir)
    os.makedirs(output_path, exist_ok=True)

    maxmax = 0.0
    max_frame_idx = -1
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx < start_frame:
            continue

        # 每10帧打印一次处理信息
        if frame_idx % 10 == 0:
            print(f"Processing frame #{frame_idx} ...")

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # matchTemplate
        result = cv2.matchTemplate(gray_frame,
                                   gray_template,
                                   cv2.TM_CCOEFF_NORMED,
                                   mask=mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # 更新最大匹配值
        if max_val > maxmax:
            maxmax = max_val
            max_frame_idx = frame_idx

        # 保存匹配到的帧
        if max_val >= threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + t_w, top_left[1] + t_h)
            cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 2)

            save_path = os.path.join(output_path, f"frame_{frame_idx}.jpg")
            cv2.imwrite(save_path, frame)
            print(
                f"[MATCH] Frame={frame_idx}, val={max_val:.3f}, => {save_path}"
            )

    cap.release()

    print("\n=== 检测完成 ===")
    print(f"全局最高匹配值: {maxmax:.3f}, 出现在帧: {max_frame_idx}")


if __name__ == "__main__":
    video_path = "./video/van/short.mp4"
    template_path = "./terror_shock.png"
    output_dir = "./matched_frames"
    threshold_value = 0.7
    start_frame_value = 0

    find_template_in_video(video_path,
                           template_path,
                           output_dir,
                           threshold=threshold_value,
                           start_frame=start_frame_value)

end()
