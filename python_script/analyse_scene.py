import os

def info(msg, queue=None):
    """キューがあればqueue.put、なければprintする共通メッセージ関数"""
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)
        
# 中央値を求める関数
def median(data):
    if not data:
        raise ValueError("空のリストです")
    data_sorted = sorted(data)
    n = len(data_sorted)
    mid = n // 2
    if n % 2 == 0:
        return (data_sorted[mid - 1] + data_sorted[mid]) / 2
    else:
        return data_sorted[mid]

def analyse_scene_calculate(config_path, psnr_file_path, psnr_ratio_file_path, scene_change_frame_file, scene_threshold_file, queue=None):
    #thinning_ratioを読み取り
    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        thinning_ratio_line = lines[7]  # 7行目が「間引き係数」
        thinning_ratio = float(thinning_ratio_line.split()[0]) 

        
    # PSNR値と比率を読み込む
    with open(psnr_file_path, "r") as f:
        psnr_values = [float(line.strip()) for line in f if line.strip()]

    with open(psnr_ratio_file_path, "r") as f:
        psnr_ratios = [float(line.strip()) for line in f if line.strip()]

    with open(scene_change_frame_file, "r") as f:
        scene_frames = [int(line.strip()) for line in f if line.strip()]


    # 最初のシーンを含めるため先頭に0を追加
    scene_frames = [0] + scene_frames
    scene_threshold_dict = {}

    # 各シーンごとに処理
    for i in range(len(scene_frames) - 1):
        start = scene_frames[i]
        end = scene_frames[i + 1] - 2  # PSNRインデックスに合わせて -2

        if end < start:
            continue
        
        scene_psnr = psnr_values[start:end + 1]
        scene_ratio = psnr_ratios[start:end + 1]

        # PSNRレシオが 0.9～1.1 の範囲外のみ使用
        filtered_psnr = [
            val for val, ratio in zip(scene_psnr, scene_ratio)
            if ratio < 0.9 or ratio > 1.1
        ]

        if not filtered_psnr:
            continue

        med = median(filtered_psnr)
        threshold = med * thinning_ratio  # しきい値 = 中央値 × 1

        scene_change_frame = scene_frames[i + 1]
        scene_threshold_dict[scene_change_frame] = round(threshold, 6)
        
    #info(f"間引き係数：{thinning_ratio}", queue)


    # 結果を書き出す
    with open(scene_threshold_file, "w", encoding="utf-8") as f:
        for frame, threshold in scene_threshold_dict.items():
            f.write(f"{frame} {threshold}\n")

