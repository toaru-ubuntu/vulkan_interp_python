import os
import platform
import subprocess
import shutil
import re
import time

def info(msg, queue=None):
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)

def encode_video(
    temp="temp",
    config_path="config",
    queue=None
):
    info("エンコード中・・・。", queue)

    is_os = platform.system().lower()
    if is_os == "windows":
        #info(f"OSは{is_os}", queue)
        ffmpeg_path = os.path.join("ffmpeg_bin", "ffmpeg.exe")
    elif is_os == "linux":
        #info(f"OSは{is_os}", queue)
        ffmpeg_path = "ffmpeg"
    else:
        raise RuntimeError("未対応のOSです")
    # ファイル定義
    base_file_count = os.path.join(temp, "file_count.txt")
    base_filename   = os.path.join(temp, "filename.txt")
    base_frate      = os.path.join(temp, "frate.txt")
    input_folder    = os.path.join(temp, "final_jpg", "%08d.jpg")

    # 各種ファイルから値を取得
    with open(base_filename, "r", encoding="utf-8") as f:
        filename = f.readline().strip()

    with open(base_frate, "r", encoding="utf-8") as f:
        frate = f.readline().strip()

    with open(base_file_count, "r", encoding="utf-8") as f:
        file_count_line = f.readline().strip()

    # configファイルから値取得
    with open(config_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    magnification = int(lines[0])
    video_codec  = lines[4]
    bitrate      = lines[5]
    temp_del = lines[8]

    # ファイル数補正
    file_count = int(file_count_line) * magnification

    # フレームレート補正
    Frate = round(float(frate), 3)
    Frate2 = round(Frate * magnification, 3)

    # 出力ファイル名
    filename2 = os.path.splitext(os.path.basename(filename))[0]
    video_output = "temp_output.mkv"
    audio_output = "temp_audio.wav"
    final_output = f"{filename2}_x{int(magnification)}.mkv"

    windows_codec_map = {
        "cpu_h264": "libx264",
        "cpu_h265": "libx265",
        "h264_nvenc":  "h264_nvenc",
        "hevc_nvenc": "hevc_nvenc",
        "av1_nvenc": "av1_nvenc",
        "h264_qsv": "h264_qsv",
        "hevc_qsv": "hevc_qsv",
        "av1_qsv": "av1_qsv",
        "h264_amf": "h264_amf",
        "hevc_amf": "hevc_amf",
        "av1_amf": "av1_amf"
    }
    linux_codec_map = {
        "cpu_h264": "libx264",
        "cpu_h265": "libx265",
        "cpu_av1":  "libsvtav1",
        "h264_vaapi": "h264_vaapi",
        "hevc_vaapi": "hevc_vaapi",
        "av1_vaapi": "av1_vaapi"
    }

    # configやGUIから取得するvideo_codecの値を想定通りにそろえる
    # 例: video_codec = "cpu_h264" など
    if is_os == "windows":
        codec = windows_codec_map.get(video_codec, "libx264")
        ffmpeg_command = [
            ffmpeg_path,
            '-framerate', str(Frate2),
            '-i', input_folder,
            '-c:v', codec,
            '-b:v', bitrate,
            '-pix_fmt', 'yuv420p',
            video_output
        ]
    elif is_os == "linux":
        codec = linux_codec_map.get(video_codec, "libx264")
        if codec in ["libx264", "libx265", "libsvtav1"]:
            ffmpeg_command = [
                ffmpeg_path,
                '-framerate', str(Frate2),
                '-i', input_folder,
                '-c:v', codec,
                '-b:v', bitrate,
                '-pix_fmt', 'yuv420p',
                video_output
            ]
        elif codec in ["h264_vaapi", "hevc_vaapi", "av1_vaapi"]:
            ffmpeg_command = [
                ffmpeg_path,
                "-vaapi_device", "/dev/dri/renderD128",
                '-framerate', str(Frate2),
                '-i', input_folder,
                '-vf', 'format=nv12,hwupload',
                '-c:v', codec,
                '-b:v', bitrate,
                '-pix_fmt', 'yuv420p',
                video_output
            ]
        else:
            # 未知コーデックはデフォルトlibx264で
            ffmpeg_command = [
                ffmpeg_path,
                '-framerate', str(Frate2),
                '-i', input_folder,
                '-c:v', "libx264",
                '-b:v', bitrate,
                '-pix_fmt', 'yuv420p',
                video_output
            ]
    else:
        # 万が一他OSだった場合もlibx264
        codec = "libx264"
        ffmpeg_command = [
            ffmpeg_path,
            '-framerate', str(Frate2),
            '-i', input_folder,
            '-c:v', codec,
            '-b:v', bitrate,
            '-pix_fmt', 'yuv420p',
            video_output
        ]


    # 進捗表示
    def show_progress(stderr, total_frames):
        progress_pattern = r'frame=\s*(\d+)'
        start_time = time.time()
        last_reported = 0
        for line in stderr:
            match_progress = re.search(progress_pattern, line)
            if match_progress:
                current_frames = int(match_progress.group(1))
                elapsed = time.time() - start_time
                fps = current_frames / elapsed if elapsed > 0 else 0.0
                info(f"[PROGRESS] {current_frames}/{total_frames} (avg: {fps:.2f} fps)", queue)
                last_reported = current_frames


    # エンコード実行
    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    show_progress(process.stderr, file_count)
    process.wait()

    # 音声抽出
    audio_extract_command = [
        ffmpeg_path,
        '-i', os.path.join("material", filename),
        '-vn',
        '-acodec', 'pcm_s16le',
        '-f', 'wav',
        audio_output
    ]
    try:
        subprocess.run(audio_extract_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        audio_exists = True
    except subprocess.CalledProcessError:
        info("音声ファイルはありません。動画のみ出力します。", queue)
        audio_exists = False

    # 音声・映像の結合
    final_merge_command = [
        ffmpeg_path,
        '-i', video_output,
        '-i', audio_output,
        '-c', 'copy',
        final_output
    ]
    if os.path.exists(final_output):
        os.remove(final_output)
    if audio_exists and os.path.exists(audio_output):
        try:
            subprocess.run(final_merge_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            os.remove(video_output)
            os.remove(audio_output)
        except subprocess.CalledProcessError:
            info("音声と動画の結合に失敗しました。動画のみ保存されます。", queue)
            shutil.move(video_output, final_output)
    else:
        shutil.move(video_output, final_output)

    info("エンコードが終了しました。", queue)
    info("[PROGRESS] エンコードが終了しました。", queue)

    # 一時フォルダ削除
    if temp_del == "0":
        shutil.rmtree(temp)
    else:
        info("tempフォルダを残します。", queue)

# --- 使い方 ---
# 例えば Tkinter ボタンから呼び出す場合
# encode_video(queue=progress_queue)

