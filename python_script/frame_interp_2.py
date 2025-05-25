import os
import time
import shutil
import subprocess
import platform
import sys
from threading import Thread

def info(msg, queue=None):
    """進捗やエラーをqueue経由で送信。なければprint。"""
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)

def interpolate_final_frames(
    config_path,
    jpg_folder,
    output_jpg,
    final_jpg,
    queue=None
):
    # rifeのパスの定義
    is_windows = platform.system().lower() == "windows"
    rife_path = os.path.join("rife", "rife-ncnn-vulkan.exe" if is_windows else "rife-ncnn-vulkan")

    # 倍率設定を読み込む
    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        magnification_line = lines[0]
        magnification = int(magnification_line.split()[0])

    if magnification == 1:
        if os.path.exists(jpg_folder):
            shutil.rmtree(jpg_folder)
        shutil.move(output_jpg, final_jpg)
        info("最終フレーム補間なし。", queue)
        return

    info("最終フレーム補完をしています・・・。", queue)
    os.makedirs(final_jpg, exist_ok=True)
    if os.path.exists(jpg_folder):
        shutil.rmtree(jpg_folder)
    shutil.move(output_jpg, jpg_folder)

    file_count = len([entry.name for entry in os.scandir(jpg_folder) if entry.is_file()])
    file_count2 = file_count * magnification
    interval = 0.5

    stop_thread = {"flag": False}
    shared_data = {"fps": 0.0}

    def count_files():
        previous_count = 0
        start_time = time.time()
        while not stop_thread["flag"]:
            file_count3 = len(os.listdir(final_jpg))
            current_time = time.time()
            elapsed_time = current_time - start_time
            frame_diff = file_count3 - previous_count
            fps = frame_diff / elapsed_time if elapsed_time > 0 else 0
            shared_data["fps"] = fps
            # ↓ここを統一
            info(f"[PROGRESS] {file_count3}/{file_count2} (avg: {fps:.2f} fps)", queue)
            previous_count = file_count3
            start_time = current_time
            time.sleep(interval)


    counter_thread = Thread(target=count_files, daemon=True)
    counter_thread.start()

    frame = file_count * magnification
    command = [
        rife_path,
        '-m', 'rife-v4.6',
        '-n', str(frame),
        '-i', jpg_folder,
        '-o', final_jpg,
        '-f', '/%08d.jpg',
        '-g', '0'
    ]
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, text=True)
    except subprocess.CalledProcessError as e:
        info(f"[ERROR] RIFEエラー: {e.stderr}", queue)

    # 終了
    stop_thread["flag"] = True
    counter_thread.join()

    final_count = len([entry.name for entry in os.scandir(final_jpg) if entry.is_file()])
    fps = shared_data["fps"]
    info("最終フレーム補完が完了しました。", queue)
    info(f"[PROGRESS] {final_count}/{file_count2} (avg: {fps:.2f} fps)", queue)


    if os.path.exists(jpg_folder):
        shutil.rmtree(jpg_folder)

