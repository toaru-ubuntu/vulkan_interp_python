import os
import shutil
import subprocess
from multiprocessing import Pool
import threading
import time
import platform

def info(msg, queue=None):
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)

def convert_image(args):
    ffmpeg_path, final_jpg, output_jpg, filename = args
    input_path = os.path.join(final_jpg, filename)
    output_path = os.path.join(output_jpg, filename)
    cmd = [
        ffmpeg_path, "-nostdin",
        "-i", input_path,
        "-pix_fmt", "yuvj420p",
        "-q:v", "5",
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        info(f"[ERROR] 変換失敗: {filename} - {e}")

def monitor_progress(output_jpg, total_files, queue=None):
    info("yuvj420p形式に変換しています・・・。", queue)
    start_time = time.time()  # 追加
    prev_current = 0          # 追加（直近との差分でなく累積fps）
    while True:
        try:
            current = len([f for f in os.listdir(output_jpg) if f.lower().endswith(".jpg")])
        except FileNotFoundError:
            current = 0
        elapsed = time.time() - start_time
        fps = current / elapsed if elapsed > 0 else 0
        info(f"[PROGRESS] {current}/{total_files} (avg: {fps:.2f} fps)", queue)
        if current >= total_files:
            break
        time.sleep(0.5)


def convert_to_yuvj420p(
    ffmpeg_path,
    final_jpg,
    output_jpg,
    queue=None
):

    # 出力先フォルダがなければ作成（中身があったら消して空で作り直すのが安全）
    if os.path.exists(output_jpg):
        shutil.rmtree(output_jpg)
    os.makedirs(output_jpg, exist_ok=True)
    
    # ファイル一覧
    jpg_files = sorted([
        f for f in os.listdir(final_jpg)
        if f.lower().endswith(".jpg")
    ])
    total_files = len(jpg_files)

    # 進捗監視スレッド
    progress_thread = threading.Thread(target=monitor_progress, args=(output_jpg, total_files, queue))
    progress_thread.start()

    # 並列変換
    tasks = [
        (ffmpeg_path, final_jpg, output_jpg, filename)
        for filename in jpg_files
    ]
    with Pool() as pool:
        pool.map(convert_image, tasks)

    progress_thread.join()

    # フォルダをリネーム
    if os.path.exists(final_jpg):
        shutil.rmtree(final_jpg)
    shutil.move(output_jpg, final_jpg)
    info("yuvj420p形式に変換が完了しました。", queue)

