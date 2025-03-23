# extract_clips_by_template.py
import cv2
import os
import numpy as np
import sys
import subprocess
from typing import List, Tuple
from lib import get_scale_factor, create_red_mask, end


# 合并区间
def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        cur_start, cur_end = current
        if cur_start <= prev_end + 1:
            merged[-1] = (prev_start, max(prev_end, cur_end))
        else:
            merged.append(current)
    return merged


def find_template_and_extract_clips(video_path,
                                    template_path,
                                    output_dir,
                                    threshold=0.6,
                                    start_frame=0):
    print(
        f"[INFO] Video: {video_path}, Template: {template_path}, Threshold={threshold}"
    )

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # 默认值防止异常

    if not cap.isOpened():
        print(f"\u274c 无法打开视频: {video_path}")
        return

    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale_factor = get_scale_factor(video_width, video_height)
    print(f"[INFO] 使用 scale_factor = {scale_factor:.5f}")

    template_rgba = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template_rgba is None:
        print(f"\u274c 无法读取模板图像: {template_path}")
        return

    if template_rgba.shape[2] == 4:
        b, g, r, a = cv2.split(template_rgba)
        template_bgr = cv2.merge([b, g, r])
    else:
        template_bgr = template_rgba

    if scale_factor != 1.0:
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        template_bgr = cv2.resize(template_bgr, (new_w, new_h),
                                  interpolation=cv2.INTER_AREA)

    mask = create_red_mask(template_bgr)
    gray_template = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    t_h, t_w = gray_template.shape[:2]

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    match_intervals = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx < start_frame:
            continue

        if frame_idx % 13 != 0:
            continue
        else:
            print(f"[INFO] 正在处理第 {frame_idx} 帧...")

        if frame_idx % 100 == 0:
            sys.stdout.flush()

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_frame,
                                   gray_template,
                                   cv2.TM_CCOEFF_NORMED,
                                   mask=mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if np.isinf(max_val) or np.isnan(max_val):
            continue

        if max_val >= threshold:
            match_intervals.append((max(0, frame_idx - 200), frame_idx + 100))
            print(f"[MATCH] Frame={frame_idx}, val={max_val:.3f}")

    cap.release()

    sub_dir = f"{video_name}_scale{scale_factor:.5f}"
    output_path = os.path.join(output_dir, sub_dir)
    os.makedirs(output_path, exist_ok=True)
    # 合并区间并用 FFmpeg 剪切
    merged = merge_intervals(match_intervals)
    print("\n=== 总共剪辑区间 ===")
    for idx, (start_f, end_f) in enumerate(merged):
        start_sec = start_f / fps
        duration = (end_f - start_f) / fps
        out_file = os.path.join(output_path, f"clip_{idx+1:03d}.mp4")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-ss", f"{start_sec:.2f}", "-i", video_path, "-t",
            f"{duration:.2f}", "-c", "copy", out_file
        ]
        print("[FFmpeg]", " ".join(ffmpeg_cmd))
        subprocess.run(ffmpeg_cmd,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

    print("\n✅ 所有区间已保存至:", output_dir)


if __name__ == "__main__":
    video_path = "./video/van/4.mp4"
    template_path = "./terror_shock.png"
    output_dir = "./clips"
    threshold = 0.7
    start_frame = 0

    find_template_and_extract_clips(video_path,
                                    template_path,
                                    output_dir,
                                    threshold=threshold,
                                    start_frame=start_frame)

    end()
