import os
import tkinter as tk
from tkinter import ttk, messagebox

def open_settings_window(CONFIG_PATH, is_os, parent=None):
    def save_config_and_close(widget_dict, window):
        try:
            scale = widget_dict["倍率"].get()
            gpu = widget_dict["GPU番号"].get()
            proc = widget_dict["プロセス数"].get()
            python_path = widget_dict["Pythonコマンド"].get()
            video_codec = widget_dict["ビデオコーデック"].get()
            bitrate = widget_dict["ビットレート"].get().strip()
            threshold = widget_dict["しきい値"].get()
            coef = widget_dict["間引き係数"].get()
            if widget_dict["特別値チェック"].get():
                coef = "1000"
            temp_keep_flag = widget_dict["tempフォルダを残す"].get()

            # ビットレートの入力チェック
            if not bitrate.isdigit():
                messagebox.showerror("エラー", "ビットレートには数字のみ入力してください。")
                return
            bitrate += "k"

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(f"{scale}\n{gpu}\n{proc}\n{python_path}\n{video_codec}\n{bitrate}\n{threshold}\n{coef}\n{int(temp_keep_flag)}")
            messagebox.showinfo("保存完了", "設定が保存されました。")
            window.destroy()
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存中にエラーが発生しました:\n{e}")

    settings_win = tk.Toplevel(parent)
    settings_win.title("設定の変更")
    settings_win.geometry("600x500")
    widget_dict = {}

    if is_os == "linux":
        config_options = [
            ("倍率", ["1", "2", "3", "4", "6", "8", "16"], "2"),
            ("GPU番号", ["0", "1", "2"], "0"),
            ("プロセス数", ["1", "2", "4", "6", "8", "12", "16", "32", "64"], "8"),
            ("Pythonコマンド", ["python", "python3"], "python3"),
            ("ビデオコーデック", ["h264", "h265", "av1", "h264_vaapi", "hevc_vaapi", "av1_vaapi"], "h264"),
        ]
    else:
        config_options = [
            ("倍率", ["1", "2", "3", "4", "6", "8", "16"], "2"),
            ("GPU番号", ["0", "1", "2"], "0"),
            ("プロセス数", ["1", "2", "4", "6", "8", "12", "16", "32", "64"], "8"),
            ("Pythonコマンド", ["python", "python3"], "python"),
            ("ビデオコーデック", [
                "cpu_h264", "cpu_h265",
                "h264_nvenc", "hevc_nvenc", "av1_nvenc",
                "h264_qsv", "hevc_qsv", "av1_qsv",
                "h264_amf", "hevc_amf", "av1_amf"
            ], "cpu_h264"),
        ]

    config_values = []
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_values = [line.strip() for line in f.readlines()]

    main_frame = tk.Frame(settings_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for i, (label_text, choices, default) in enumerate(config_options):
        tk.Label(left_frame, text=label_text, anchor="center").pack(pady=(8 if i==0 else 12, 0), anchor="center")
        combo = ttk.Combobox(left_frame, values=choices, state="readonly", justify="center", width=10)
        combo.set(config_values[i] if i < len(config_values) and config_values[i] in choices else default)
        combo.pack(anchor="center")
        widget_dict[label_text] = combo

    tk.Label(right_frame, text="ビットレート", anchor="w").pack(pady=(8, 0), anchor="w")
    bitrate_frame = tk.Frame(right_frame)
    bitrate_frame.pack(anchor="w")
    bitrate_entry = ttk.Entry(bitrate_frame, justify="center", width=10)
    default_bitrate = "3000"
    if len(config_values) >= 6 and config_values[5]:
        val = config_values[5]
        if val.endswith("k"):
            val = val[:-1]
        bitrate_entry.insert(0, val)
    else:
        bitrate_entry.insert(0, default_bitrate)
    bitrate_entry.pack(side=tk.LEFT)
    tk.Label(bitrate_frame, text="k", font=("Meiryo", 10)).pack(side=tk.LEFT, padx=(5,0))
    widget_dict["ビットレート"] = bitrate_entry

    tk.Label(right_frame, text="シーンチェンジしきい値", anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text="大きいほど検出しやすくなります(通常:12〜22, デフォルト:18)", font=("Meiryo", 10), fg="gray").pack(anchor="w")
    threshold_entry = ttk.Entry(right_frame, justify="center", width=14)
    default_threshold = "18"
    if len(config_values) >= 7 and config_values[6]:
        threshold_entry.insert(0, config_values[6])
    else:
        threshold_entry.insert(0, default_threshold)
    threshold_entry.pack(anchor="w")
    widget_dict["しきい値"] = threshold_entry

    tk.Label(right_frame, text="間引き係数", anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text="低いほど厳しく間引きます（通常:0.8〜1.2, デフォルト:1.05）", font=("Meiryo", 10), fg="gray").pack(anchor="w")
    coef_frame = tk.Frame(right_frame)
    coef_frame.pack(pady=(2, 0), anchor="w")
    coef_entry = ttk.Entry(coef_frame, justify="center", width=10)
    coef_val = "1.05"
    if len(config_values) >= 8 and config_values[7]:
        coef_val = config_values[7]
    coef_entry.insert(0, coef_val)
    coef_entry.pack(side=tk.LEFT)
    special_var = tk.BooleanVar()
    def on_special_toggle():
        if special_var.get():
            coef_entry.config(state="normal")
            coef_entry.delete(0, tk.END)
            coef_entry.insert(0, "1000")
            coef_entry.config(state="readonly")
        else:
            coef_entry.config(state="normal")
            coef_entry.delete(0, tk.END)
            coef_entry.insert(0, coef_val)
    special_chk = tk.Checkbutton(coef_frame, text="間引きしない場合はチェック", variable=special_var, command=on_special_toggle)
    special_chk.pack(side=tk.LEFT, padx=10)
    widget_dict["間引き係数"] = coef_entry
    widget_dict["特別値チェック"] = special_var

    # tempフォルダを残す チェックボックス
    keep_temp_var = tk.BooleanVar()
    if len(config_values) >= 9:
        keep_temp_var.set(config_values[8] == "1")
    tk.Checkbutton(right_frame, text="tempフォルダを残す", variable=keep_temp_var).pack(pady=(20, 0), anchor="w")
    widget_dict["tempフォルダを残す"] = keep_temp_var

    save_button = tk.Button(
        settings_win,
        text="設定を保存",
        font=("Meiryo", 12, "bold"),
        width=18,
        command=lambda: save_config_and_close(widget_dict, settings_win)
    )
    save_button.pack(pady=16)

    settings_win.grab_set()
    settings_win.wait_window()
