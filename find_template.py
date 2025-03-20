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


def load_scale_factors():
    """ 读取 scale_factors.json，如果文件不存在则返回空字典 """
    if os.path.exists(SCALE_FACTOR_FILE):
        with open(SCALE_FACTOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


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
    """
    将 BGR 模板图转为 HSV，并根据红色区间生成一个二值 mask。
    红色区域为255，其他颜色为0。
    """

    # 1) 转到 HSV
    hsv = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2HSV)

    # 2) 定义红色在 HSV 中的范围（分两段）
    #    下列值只是常见的红色区间，可能要根据实际素材调参
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])

    # 3) inRange() 得到两个红色区间的 mask
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # 4) 合并，得到完整的红色区域
    mask = cv2.bitwise_or(mask1, mask2)

    # 5) 这里 mask 是 0 or 255，与模板同样尺寸 (height, width)
    #  若模板像素是红色 => mask=255, 否则 0
    #  可选：做一些形态学操作，清除噪点
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    return mask


def find_template_in_video(video_path,
                           template_path,
                           output_dir,
                           threshold=0.6,
                           scale_factor=1,
                           start_frame=0):
    """
    从 video_path 所指向的视频逐帧匹配 template_path 的图样，
    当匹配值大于 threshold 时，保存对应帧到 output_dir。

    :param video_path: 视频文件的路径
    :param template_path: 模板图像的路径
    :param output_dir: 存储匹配成功的帧的输出文件夹
    :param threshold: 匹配阈值，越接近1表示匹配度越严格
    :param scale_factor: 对模板进行缩放的因子，1.0 表示不缩放
    :param start_frame: 从视频的第几帧开始分析，默认为0
    """
    print(
        f"video_path: {video_path}, template_path: {template_path}, output_dir: {output_dir}, threshold: {threshold}, scale_factor: {scale_factor}, start_frame: {start_frame}"
    )
    # 3) 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        return
        # 获取视频尺寸
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 获取 scale_factor
    scale_factor = get_scale_factor(video_width, video_height)

    # 2) 读取模板图像 (4 通道: BGRA 或 3 通道: BGR)
    template_rgba = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template_rgba is None:
        print(f"无法读取模板图像: {template_path}")
        return

    # 分离通道（若为3通道，这里 a 会是 None）
    if template_rgba.shape[2] == 4:
        b, g, r, a = cv2.split(template_rgba)
        # 仅保留 BGR，用于后续灰度匹配
        template_bgr = cv2.merge([b, g, r])
        # 可选：基于alpha做mask，若要使用 cv2.matchTemplate(mask=mask)
        # mask = np.where(a > 0, 255, 0).astype(np.uint8)
    else:
        template_bgr = template_rgba

    # 如果需要对模板缩放
    if scale_factor != 1.0:
        new_w = int(template_bgr.shape[1] * scale_factor)
        new_h = int(template_bgr.shape[0] * scale_factor)
        template_bgr = cv2.resize(template_bgr, (new_w, new_h),
                                  interpolation=cv2.INTER_AREA)

    # 转灰度用于 matchTemplate
    gray_template = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    t_h, t_w = gray_template.shape[:2]

    # 生成只保留“红色部分”的 mask
    mask = create_red_mask(template_bgr)

    template_height, template_width = template_bgr.shape[:2]
    # 1) 创建输出目录（带上视频名与scale_factor）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    sub_dir = f"{video_name}_scale{scale_factor:.5f}"
    output_path = os.path.join(output_dir, sub_dir)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 记录最大匹配值 & 其帧号
    maxmax = 0.0
    max_frame_idx = -1

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            # 视频读取完毕或发生错误
            break
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"正在处理第 {frame_count} 帧...")
        else:
            continue

        if frame_count % 100 == 0:
            sys.stdout.flush()  # 手动刷新缓冲区
        # 如果需要从指定帧开始
        if frame_count < start_frame:
            continue
        # cv2.imshow("11", frame)
        # # 按下“q”键退出
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        # cv2.destroyAllWindows
        # 4) 转灰度
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 5) 模板匹配
        # 这里使用TM_CCOEFF_NORMED，数值越接近1表明越相似
        result = cv2.matchTemplate(gray_frame,
                                   gray_template,
                                   cv2.TM_CCOEFF_NORMED,
                                   mask=mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(max_val)
        # 更新全局最大匹配值
        if max_val > maxmax:
            maxmax = max_val
            max_frame_idx = frame_count

        # 6) 判断匹配值是否超过阈值
        if max_val >= threshold or frame_count == start_frame + 1:
            # 在匹配区域处绘制方框
            top_left = max_loc
            bottom_right = (top_left[0] + template_width,
                            top_left[1] + template_height)
            cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255),
                          2)  # 绘制红色矩形

            save_path = os.path.join(output_path, f"frame_{frame_count}.jpg")
            cv2.imwrite(save_path, frame)
            print(
                f"[MATCH] 帧 {frame_count} (max_val={max_val:.3f}) 已保存: {save_path}"
            )

    cap.release()
    return maxmax, max_frame_idx


if __name__ == "__main__":
    video_path = "./video/van/short.mp4"  # 待检测的视频文件
    template_path = "./terror_shock.png"  # 要匹配的图样（模板）
    output_dir = "./matched_frames"  # 存放匹配结果帧的目录
    threshold_value = 0.7  # 可以根据实际情况调整阈值
    maxmax, max_frame_idx = find_template_in_video(video_path,
                                                   template_path,
                                                   output_dir,
                                                   threshold=threshold_value,
                                                   start_frame=0,
                                                   scale_factor=0.77879)
    print(maxmax, max_frame_idx)
f.close
sys.stdout = sys.__stdout__
print("Done.")

print(log_filename)
