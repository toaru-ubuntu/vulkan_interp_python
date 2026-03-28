import os
import shutil
import subprocess
from multiprocessing import Pool
import threading
import time
import json
import platform

def info(msg, queue=None):
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)

def run_rife(args):
    result, file1, file2, padded_number, output_jpg, gpu, rife_path = args
    try:
        subprocess.run([
            rife_path,
            "-m", "rife-v4.6",
            "-s", f"{result:.4f}",
            "-0", file1,
            "-1", file2,
            "-o", f"{output_jpg}/{padded_number}.jpg",
            "-g", str(gpu)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, text=True, errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"RIFE error: {e.stderr}")

def progress_bar(output_jpg, total_files, queue=None, lang="en"):
    if lang == "ja":
        info("重複フレームを削除した分を補間中・・・。", queue)
    elif lang == "en":
        info("Interpolating for removed duplicate frames...", queue)
    initial_files = len([f for f in os.listdir(output_jpg) if f.endswith('.jpg')])
    start_time = time.time()
    interval = 0.5
    while True:
        current_files = len([f for f in os.listdir(output_jpg) if f.endswith('.jpg')])
        processed_files = current_files - initial_files
        elapsed_time = time.time() - start_time
        fps = processed_files / elapsed_time if elapsed_time > 0 else 0
        info(f"[PROGRESS] {current_files}/{total_files} (avg: {fps:.2f} fps)", queue)
        if current_files >= total_files:
            break
        time.sleep(interval)
    if lang == "ja":
        info("重複フレームを削除した分の補間が終わりました。", queue)
    elif lang == "en":
        info("Interpolation for removed duplicate frames finished.", queue)
    info(f"[PROGRESS] {current_files}/{total_files} (avg: {fps:.2f} fps)", queue)

def interpolate_frames(
    config_path,
    jpg_folder,
    output_jpg,
    gap_file,
    scene_change_frame_file,
    file_count_path,
    queue=None,
    lang="en"
):
    is_windows = platform.system().lower() == "windows"
    rife_path = os.path.join("rife", "rife-ncnn-vulkan.exe" if is_windows else "rife-ncnn-vulkan")

    # 設定ファイル読み込み (JSON形式)
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
        
        # JSONから値を取得し、数値(int)に変換。キーが無い場合はデフォルト値を設定
        gpu_value = int(config_data.get("gpu", "0"))
        num_processes = int(config_data.get("proc", "8"))
    except Exception:
        # 万が一のエラー時の安全策（デフォルト値）
        gpu_value = 0
        num_processes = 8

    os.makedirs(output_jpg, exist_ok=True)

    input_files = sorted([f for f in os.listdir(jpg_folder) if f.endswith('.jpg')])

    with open(gap_file, 'r', encoding='utf-8') as f:
        gap_values = [int(line.strip()) for line in f]

    with open(scene_change_frame_file, 'r', encoding='utf-8') as f:
        scene_change_frames = [f"{int(frame.strip()):08d}.jpg" for frame in f]

    with open(file_count_path, 'r', encoding='utf-8') as f:
        total_files = int(f.readline().strip())

    output_file_number = 1
    file_count = len(input_files)
    tasks = []

    for i in range(file_count - 1):
        file1 = os.path.join(jpg_folder, input_files[i])
        file2 = os.path.join(jpg_folder, input_files[i + 1])
        gap = gap_values[i]
        scene_change_detected = input_files[i + 1] in scene_change_frames

        if os.path.isfile(file1):
            padded_number = f"{output_file_number:08d}"
            shutil.copy(file1, f"{output_jpg}/{padded_number}.jpg")
            output_file_number += 1

        if os.path.isfile(file1) and os.path.isfile(file2):
            if scene_change_detected:
                for _ in range(1, gap + 1):
                    padded_number = f"{output_file_number:08d}"
                    shutil.copy(file1, f"{output_jpg}/{padded_number}.jpg")
                    output_file_number += 1
            else:
                for b in range(1, gap + 1):
                    result = 1 / (gap + 1) * b
                    padded_number = f"{output_file_number:08d}"
                    tasks.append((result, file1, file2, padded_number, output_jpg, gpu_value, rife_path))
                    output_file_number += 1

    # プログレスバーのスレッドを起動
    progress_thread = threading.Thread(target=progress_bar, args=(output_jpg, total_files, queue, lang))
    progress_thread.start()

    # 並列補間処理
    with Pool(processes=num_processes) as pool:
        pool.map(run_rife, tasks)

    # 最後のファイルをコピー
    file_last = os.path.join(jpg_folder, input_files[-1])
    if os.path.isfile(file_last):
        padded_number = f"{output_file_number:08d}"
        shutil.copy(file_last, f"{output_jpg}/{padded_number}.jpg")

    progress_thread.join()

