import os
import time

def info(msg, queue=None):
    """キューがあればqueue.put、なければprintする共通メッセージ関数"""
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)

def value_definitions(config_path, psnr_file_path, file_count_file, scene_change_frame_file, queue=None, lang="en"):
    if lang == "ja":
        info("シーンチェンジを検出しています・・・。", queue)
    elif lang == "en":
        info("Detecting scene changes...", queue)
    
    # シーンチェンジのしきい値の設定
    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        scene_change_threshold_line = lines[6]  # 7行目がシーンチェンジしきい値
        scene_change_threshold = float(scene_change_threshold_line.split()[0]) 

    # PSNR値の読み込み
    with open(psnr_file_path, "r", encoding="utf-8") as f:
        psnr_values = [float(line.strip()) for line in f if line.strip()]

    # フレーム数の読み込み
    with open(file_count_file, "r", encoding="utf-8") as f:
        file_count = int(f.readline().strip())

    threshold = scene_change_threshold

    scene_change_filenames = []
    last_time = time.time()

    for i, psnr in enumerate(psnr_values):
        if psnr < threshold:
            scene_change_filenames.append(i + 2)

        current_time = time.time()
        if current_time - last_time >= 1:
            if lang == "ja":
                info(f"[PROGRESS] {i + 2}/{file_count}", queue)
            elif lang == "en":
                info(f"[PROGRESS] {i + 2}/{file_count}", queue)
            last_time = current_time

    if lang == "ja":
        info("シーンチェンジのフレームの調査が終了しました。", queue)
    elif lang == "en":
        info("Scene change frame detection finished.", queue)
    info(f"[PROGRESS] {file_count}/{file_count}", queue)

    # 出力
    with open(scene_change_frame_file, "w", encoding="utf-8") as f:
        for value in scene_change_filenames:
            f.write(f"{value}\n")

