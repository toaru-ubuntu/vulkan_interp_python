import os
import tkinter as tk
from tkinter import ttk, messagebox

# メッセージ辞書
MESSAGES = {
    "en": {
        "title": "Settings",
        "save": "Save Settings",
        "saved": "Settings saved.",
        "error": "Error",
        "save_error": "Error occurred while saving settings:",
        "bitrate_label": "Bitrate",
        "scene_thresh_label": "Scene Change Threshold",
        "scene_thresh_desc": "Larger value detects more easily (Normal: 12-22, Default: 19)",
        "thin_label": "Thinning Factor",
        "thin_desc": "Lower value means stricter thinning (Normal: 0.8-1.2, Default: 1.05)",
        "no_thin_chk": "Check for no thinning",
        "keep_temp": "Keep temp folder",
        "save_error_num": "Please enter a number for bitrate.",
        "magnification_label": "magnification",
        "gpu_label": "GPU Index",
        "proc_label": "Processes",
        "python_label": "Python Cmd",
        "codec_label": "Video Codec",
        "lang_label": "Language",
        "japanese": "Japanese",
        "english": "English",
        "restart_needed": "Language setting has changed.\nPlease restart the app for the language change to take effect.",
    },
    "ja": {
        "title": "設定の変更",
        "save": "設定を保存",
        "saved": "設定が保存されました。",
        "error": "エラー",
        "save_error": "設定の保存中にエラーが発生しました:",
        "bitrate_label": "ビットレート",
        "scene_thresh_label": "シーンチェンジしきい値",
        "scene_thresh_desc": "大きいほど検出しやすくなります(通常:12〜22, デフォルト:19)",
        "thin_label": "間引き係数",
        "thin_desc": "低いほど厳しく間引きます（通常:0.8〜1.2, デフォルト:1.05）",
        "no_thin_chk": "間引きしない場合はチェック",
        "keep_temp": "tempフォルダを残す",
        "save_error_num": "ビットレートには数字のみ入力してください。",
        "magnification_label": "倍率",
        "gpu_label": "GPU番号",
        "proc_label": "プロセス数",
        "python_label": "Pythonコマンド",
        "codec_label": "ビデオコーデック",
        "lang_label": "言語",
        "japanese": "日本語",
        "english": "English",
        "restart_needed": "言語設定が変更されました。\n反映するにはアプリを再起動してください。",
    }
}

def open_settings_window(CONFIG_PATH, is_os, parent=None):
    # --- 設定読み込み ---
    config_values = []
    lang = "en"  # デフォルト
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_values = [line.strip() for line in f.readlines()]
        if len(config_values) > 9 and config_values[-1] in ["ja", "en"]:
            lang = config_values[-1]
            config_values = config_values[:-1]  # 言語以外の設定値

    def getmsg(key):
        return MESSAGES[lang][key]

    def save_config_and_close(widget_dict, window, original_lang):
        try:
            scale = widget_dict["scale"].get()
            gpu = widget_dict["gpu"].get()
            proc = widget_dict["proc"].get()
            python_path = widget_dict["python_path"].get()
            video_codec = widget_dict["video_codec"].get()
            bitrate = widget_dict["bitrate"].get().strip()
            scene_thresh = widget_dict["scene_thresh"].get()
            thin = widget_dict["thin"].get()
            if widget_dict["no_thin_chk"].get():
                thin = "1000"
            keep_temp = widget_dict["keep_temp"].get()
            new_lang = lang_var.get()
            if not bitrate.isdigit():
                messagebox.showerror(getmsg("error"), getmsg("save_error_num"))
                return
            bitrate += "k"
            lines = [
                scale, gpu, proc, python_path, video_codec,
                bitrate, scene_thresh, thin, str(int(keep_temp)), new_lang
            ]
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write('\n'.join(lines))
            messagebox.showinfo(getmsg("save"), getmsg("saved"))
            if new_lang != original_lang:
                window.destroy()
                # 言語変更時のみ警告
                messagebox.showwarning(getmsg("save"), getmsg("restart_needed"))
            window.destroy()
        except Exception as e:
            messagebox.showerror(getmsg("error"), f"{getmsg('save_error')}\n{e}")

    def on_lang_change():
        nonlocal lang
        lang = lang_var.get()
        settings_win.title(getmsg("title"))
        # ※ラベルの再描画などはここでは省略

    settings_win = tk.Toplevel(parent)
    lang_var = tk.StringVar(value=lang)
    original_lang = lang  # 最初の言語を記憶
    settings_win.title(getmsg("title"))
    settings_win.geometry("600x500")
    widget_dict = {}

    # 言語選択ラジオボタン
    lang_frame = tk.Frame(settings_win)
    lang_frame.pack(pady=5)
    tk.Label(lang_frame, text=getmsg("lang_label")).pack(side=tk.LEFT)
    tk.Radiobutton(lang_frame, text=getmsg("japanese"), variable=lang_var, value="ja", command=on_lang_change).pack(side=tk.LEFT)
    tk.Radiobutton(lang_frame, text=getmsg("english"), variable=lang_var, value="en", command=on_lang_change).pack(side=tk.LEFT)

    # 設定項目
    if is_os == "linux":
        config_options = [
            ("scale", getmsg("magnification_label"), ["1", "2", "3", "4", "6", "8", "16"], "2"),
            ("gpu", getmsg("gpu_label"), ["0", "1", "2"], "0"),
            ("proc", getmsg("proc_label"), ["1", "2", "4", "6", "8", "12", "16", "32", "64"], "8"),
            ("python_path", getmsg("python_label"), ["python", "python3"], "python3"),
            ("video_codec", getmsg("codec_label"), ["h264", "h265", "av1", "h264_vaapi", "hevc_vaapi", "av1_vaapi"], "h264"),
        ]
    else:
        config_options = [
            ("scale", getmsg("magnification_label"), ["1", "2", "3", "4", "6", "8", "16"], "2"),
            ("gpu", getmsg("gpu_label"), ["0", "1", "2"], "0"),
            ("proc", getmsg("proc_label"), ["1", "2", "4", "6", "8", "12", "16", "32", "64"], "8"),
            ("python_path", getmsg("python_label"), ["python", "python3"], "python"),
            ("video_codec", getmsg("codec_label"), [
                "cpu_h264", "cpu_h265",
                "h264_nvenc", "hevc_nvenc", "av1_nvenc",
                "h264_qsv", "hevc_qsv", "av1_qsv",
                "h264_amf", "hevc_amf", "av1_amf"
            ], "cpu_h264"),
        ]

    main_frame = tk.Frame(settings_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 左フレーム：combo項目
    for i, (key, label_text, choices, default) in enumerate(config_options):
        tk.Label(left_frame, text=label_text, anchor="center").pack(pady=(8 if i==0 else 12, 0), anchor="center")
        combo = ttk.Combobox(left_frame, values=choices, state="readonly", justify="center", width=10)
        combo.set(config_values[i] if i < len(config_values) and config_values[i] in choices else default)
        combo.pack(anchor="center")
        widget_dict[key] = combo

    # 右フレーム：その他
    # ビットレート
    tk.Label(right_frame, text=getmsg("bitrate_label"), anchor="w").pack(pady=(8, 0), anchor="w")
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
    tk.Label(bitrate_frame, text="k").pack(side=tk.LEFT, padx=(5,0))
    widget_dict["bitrate"] = bitrate_entry

    # シーンチェンジしきい値
    tk.Label(right_frame, text=getmsg("scene_thresh_label"), anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text=getmsg("scene_thresh_desc"), font=("Meiryo", 10), fg="gray").pack(anchor="w")
    threshold_entry = ttk.Entry(right_frame, justify="center", width=14)
    default_threshold = "19"
    if len(config_values) >= 7 and config_values[6]:
        threshold_entry.insert(0, config_values[6])
    else:
        threshold_entry.insert(0, default_threshold)
    threshold_entry.pack(anchor="w")
    widget_dict["scene_thresh"] = threshold_entry

    # 間引き係数
    tk.Label(right_frame, text=getmsg("thin_label"), anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text=getmsg("thin_desc"), font=("Meiryo", 10), fg="gray").pack(anchor="w")
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
    special_chk = tk.Checkbutton(coef_frame, text=getmsg("no_thin_chk"), variable=special_var, command=on_special_toggle)
    special_chk.pack(side=tk.LEFT, padx=10)
    widget_dict["thin"] = coef_entry
    widget_dict["no_thin_chk"] = special_var

    # tempフォルダを残す チェックボックス
    keep_temp_var = tk.BooleanVar()
    if len(config_values) >= 9:
        keep_temp_var.set(config_values[8] == "1")
    tk.Checkbutton(right_frame, text=getmsg("keep_temp"), variable=keep_temp_var).pack(pady=(20, 0), anchor="w")
    widget_dict["keep_temp"] = keep_temp_var

    save_button = tk.Button(
        settings_win,
        text=getmsg("save"),
        font=("Meiryo", 12, "bold"),
        width=18,
        command=lambda: save_config_and_close(widget_dict, settings_win, original_lang)
    )
    save_button.pack(pady=16)

    settings_win.grab_set()
    settings_win.wait_window()

