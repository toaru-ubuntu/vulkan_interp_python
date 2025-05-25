def main():
    import tkinter as tk
    from tkinter import messagebox, ttk
    import threading
    import os
    import platform
    import shutil
    import time
    from queue import Queue, Empty
    from threading import Event
    from python_script.definition import all_definition
    from python_script.config_gui import open_settings_window
    from python_script.ffmpeg_download import download_ffmpeg_windows
    from python_script.rife_download import download_rife
    from python_script.setting_information import setting_information
    from python_script.convert_to_image import convert_video_to_images
    from python_script.calculate_psnr import calculate_psnr
    from python_script.psnr_ratio import calculate_psnr_ratio
    from python_script.scene_change_detection import value_definitions
    from python_script.analyse_scene import analyse_scene_calculate
    from python_script.frame_thinning import frame_thinning
    from python_script.calculate_gaps import calculate_gaps
    from python_script.frame_interp_1 import interpolate_frames
    from python_script.frame_interp_2 import interpolate_final_frames
    from python_script.noise_reduction import noise_reduction
    from python_script.convert_to_yuvj420p import convert_to_yuvj420p
    from python_script.encode_and_merge import encode_video

    progress_queue = Queue()
    stop_event = Event()

    is_os = platform.system().lower()
    temp_folder = "temp"
    config_path = "config"
    ffmpeg_dest_dir = "ffmpeg_bin"
    rife_dest_dir = "rife"
    material_folder = "material"
    jpg_folder = os.path.join(temp_folder, "jpg")
    output_jpg = os.path.join(temp_folder, "output_jpg")
    final_jpg = os.path.join("temp", "final_jpg")
    filename_path = os.path.join(temp_folder, "filename.txt")
    file_count_path = os.path.join(temp_folder, "file_count.txt")
    psnr_file_path = os.path.join(temp_folder, "psnr_values.txt")
    psnr_ratio_file_path = os.path.join(temp_folder, "psnr_ratio.txt")
    scene_change_frame_file = os.path.join(temp_folder, "scene_change_frame.txt")
    file_count_file = os.path.join(temp_folder, "file_count.txt")
    scene_threshold_file = os.path.join(temp_folder, "scene_threshold.txt")
    gap_file = os.path.join(temp_folder, "gaps.txt")

    is_windows = is_os == "windows"
    ffmpeg_path = os.path.join("ffmpeg_bin", "ffmpeg.exe") if is_windows else "ffmpeg"
    ffprobe_path = os.path.join("ffmpeg_bin", "ffprobe.exe") if is_windows else "ffprobe"

    root = tk.Tk()
    root.title("vulkan_interp_python_ver0.60")
    root.geometry("650x700")

    tk.Label(root, text="処理を選択してください").pack(pady=10)

    run_button = tk.Button(root, text="START!", command=lambda: run_main_py_async())
    run_button.pack(pady=5)

    stop_button = tk.Button(root, text="STOP", command=lambda: stop_event.set())
    stop_button.pack(pady=5)

    settings_button = tk.Button(
        root, text="設定を変更",
        command=lambda: open_settings_window(config_path, is_os, parent=root)
    )
    settings_button.pack(pady=5)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    log_frame = tk.Frame(main_frame)
    log_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    log_text = tk.Text(log_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=25)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_text.tag_config("error", foreground="red")
    scrollbar.config(command=log_text.yview)

    progress_var = tk.DoubleVar()
    progress_text_var = tk.StringVar()
    progress_frame = tk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=10)
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=350)
    progress_bar.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=False)
    progress_label = tk.Label(progress_frame, textvariable=progress_text_var, fg="green", anchor="w",
                             font=("Meiryo", 12, "bold"), width=32)
    progress_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def poll_progress_queue():
        try:
            while True:
                line = progress_queue.get_nowait()
                if line.startswith("[PROGRESS]"):
                    import re
                    clean_line = line.replace("[PROGRESS]", "").strip()
                    match = re.search(r"(\d+)\s*/\s*(\d+)(?:\s*\(avg:\s*([\d.]+)\s*fps\))?", clean_line)
                    if match:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        percent = (current / total) * 100 if total > 0 else 0
                        progress_var.set(percent)
                        fps = match.group(3)
                        if fps:
                            progress_text_var.set(f"{current} / {total}   ({float(fps):.2f} fps)")
                        else:
                            progress_text_var.set(f"{current} / {total}")
                    else:
                        progress_text_var.set(clean_line)
                elif line.startswith("[ERROR]"):
                    log_text.insert(tk.END, line, "error")
                else:
                    log_text.insert(tk.END, line)
                log_text.see(tk.END)
        except Empty:
            pass
        root.after(100, poll_progress_queue)

    def initial_check():
        if not os.path.exists(config_path):
            progress_queue.put("[ERROR] configファイルが見つかりません。\n設定変更から、一度「設定を保存」して下さい。\n")
        if not os.path.exists(material_folder):
            progress_queue.put("[ERROR] materialフォルダが見つかりません\n")
            progress_queue.put("materialフォルダを作成します。\n")
            os.makedirs(material_folder, exist_ok=True)

    def run_main_py_async():
        stop_event.clear()

        def worker():
            log_text.delete("1.0", tk.END)
            result = all_definition(temp_folder, config_path, material_folder, progress_queue)
            if result == "no_file" or stop_event.is_set(): return

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                python_path = lines[3].strip().split()[0]
            except Exception as e:
                progress_queue.put(f"[ERROR] configファイル読み込みエラー: {e}\n")
                return

            setting_information(config_path, progress_queue)
            if stop_event.is_set(): return

            start_time = time.time()
            download_ffmpeg_windows(ffmpeg_dest_dir, progress_queue)
            if stop_event.is_set(): return

            download_rife(rife_dest_dir, progress_queue)
            if stop_event.is_set(): return

            convert_video_to_images(ffmpeg_path, ffprobe_path, temp_folder, jpg_folder, material_folder, filename_path, progress_queue)
            if stop_event.is_set(): return

            calculate_psnr(jpg_folder, file_count_path, ffmpeg_path, psnr_file_path, progress_queue)
            if stop_event.is_set(): return

            calculate_psnr_ratio(psnr_file_path, psnr_ratio_file_path, progress_queue)
            if stop_event.is_set(): return

            value_definitions(config_path, psnr_file_path, file_count_file, scene_change_frame_file, progress_queue)
            if stop_event.is_set(): return

            analyse_scene_calculate(config_path, psnr_file_path, psnr_ratio_file_path, scene_change_frame_file, scene_threshold_file, progress_queue)
            if stop_event.is_set(): return

            frame_thinning(psnr_file_path, psnr_ratio_file_path, scene_threshold_file, jpg_folder, output_jpg, progress_queue)
            if stop_event.is_set(): return

            calculate_gaps(jpg_folder, gap_file, progress_queue)
            if stop_event.is_set(): return

            interpolate_frames(config_path, jpg_folder, output_jpg, gap_file, scene_change_frame_file, file_count_path, progress_queue)
            if stop_event.is_set(): return

            interpolate_final_frames(config_path, jpg_folder, output_jpg, final_jpg, progress_queue)
            if stop_event.is_set(): return

            noise_reduction(config_path, scene_change_frame_file, final_jpg, progress_queue)
            if stop_event.is_set(): return

            convert_to_yuvj420p(ffmpeg_path, final_jpg, output_jpg, progress_queue)
            if stop_event.is_set(): return

            encode_video(queue=progress_queue)
            if stop_event.is_set(): return

            elapsed_time = time.time() - start_time
            msg = f"処理時間: {elapsed_time:.2f} 秒\n"
            progress_queue.put(msg)

        threading.Thread(target=worker, daemon=True).start()

    root.after(100, poll_progress_queue)
    root.after(100, initial_check)
    root.mainloop()

if __name__ == "__main__":
    main()