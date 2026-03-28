import os
import json
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
        "scene_thresh_desc": "With PySceneDetect, the optimal value is 3.0",
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
        "scene_thresh_desc": "PySceneDetectの導入により適正値は3.0になります",
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
    # --- 設定読み込み（辞書型へ変更） ---
    config_dict = {}
    lang = "en"  # デフォルト

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_dict = json.load(f) # 辞書型として読み込み
            lang = config_dict.get("lang", "en")
        except json.JSONDecodeError:
            # 既に旧バージョン（行番号方式）を使っているユーザー環境への配慮
            # エラーが出た場合は一旦空の辞書として扱い、再保存時に新形式(JSON)で上書きさせます
            print("旧形式の設定ファイルが検出されたため、初期値で起動します。")
            config_dict = {}

    def getmsg(key):
        return MESSAGES[lang][key]

    def save_config_and_close(widget_dict, window, original_lang):
        try:
            # --- 画面の入力欄(ウィジェット)から現在の値を取得 ---
            scale = widget_dict["scale"].get()
            gpu = widget_dict["gpu"].get()
            proc = widget_dict["proc"].get()
            python_path = widget_dict["python_path"].get()
            video_codec = widget_dict["video_codec"].get()
            bitrate = widget_dict["bitrate"].get()
            scene_thresh = widget_dict["scene_thresh"].get()
            thin = widget_dict["thin"].get()
            keep_temp = widget_dict["keep_temp"].get() # BooleanVarなのでTrue/Falseが返る
            new_lang = lang_var.get()
            # ------------------------------------------------
            
            if not bitrate.isdigit():
                messagebox.showerror(getmsg("error"), getmsg("save_error_num"))
                return
            bitrate += "k"
            
            # 辞書型（JSONデータ）としてまとめる
            new_config = {
                "scale": scale,
                "gpu": gpu,
                "proc": proc,
                "python_path": python_path,
                "video_codec": video_codec,
                "bitrate": bitrate,
                "scene_thresh": scene_thresh,
                "thin": thin,
                "keep_temp": int(keep_temp), # True/False を 1/0 に変換して保存
                "lang": new_lang
            }
            
            # JSON形式でテキストファイルに保存 (indent=4 で見やすく改行・インデントする)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)

            messagebox.showinfo(getmsg("save"), getmsg("saved"))
            
            # 言語が変更された場合は再起動を促すメッセージ
            if original_lang != new_lang:
                messagebox.showinfo(getmsg("title"), getmsg("restart_needed"))
                
            window.destroy()
            
        except Exception as e:
            messagebox.showerror(getmsg("error"), f"{getmsg('save_error')} {e}")

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
        
        # 辞書からキー名で取得（存在しない場合はdefaultを使用）
        saved_val = config_dict.get(key, default)
        combo.set(saved_val if saved_val in choices else default)
        
        combo.pack(anchor="center")
        widget_dict[key] = combo

    # 右フレーム：その他
    # ビットレート
    tk.Label(right_frame, text=getmsg("bitrate_label"), anchor="w").pack(pady=(8, 0), anchor="w")
    bitrate_frame = tk.Frame(right_frame)
    bitrate_frame.pack(anchor="w")
    bitrate_entry = ttk.Entry(bitrate_frame, justify="center", width=10)
    
    default_bitrate = "3000"
    saved_bitrate = config_dict.get("bitrate", "")
    if saved_bitrate:
        if str(saved_bitrate).endswith("k"):
            saved_bitrate = str(saved_bitrate)[:-1]
        bitrate_entry.insert(0, saved_bitrate)
    else:
        bitrate_entry.insert(0, default_bitrate)
        
    bitrate_entry.pack(side=tk.LEFT)
    tk.Label(bitrate_frame, text="k").pack(side=tk.LEFT, padx=(5,0))
    widget_dict["bitrate"] = bitrate_entry

    # シーンチェンジしきい値
    tk.Label(right_frame, text=getmsg("scene_thresh_label"), anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text=getmsg("scene_thresh_desc"), font=("Meiryo", 10), fg="gray").pack(anchor="w")
    threshold_entry = ttk.Entry(right_frame, justify="center", width=14)
    
    default_threshold = "3"
    saved_thresh = config_dict.get("scene_thresh", default_threshold)
    threshold_entry.insert(0, str(saved_thresh))
    threshold_entry.pack(anchor="w")
    widget_dict["scene_thresh"] = threshold_entry

    # 間引き係数
    tk.Label(right_frame, text=getmsg("thin_label"), anchor="w").pack(pady=(16, 0), anchor="w")
    tk.Label(right_frame, text=getmsg("thin_desc"), font=("Meiryo", 10), fg="gray").pack(anchor="w")
    coef_frame = tk.Frame(right_frame)
    coef_frame.pack(pady=(2, 0), anchor="w")
    coef_entry = ttk.Entry(coef_frame, justify="center", width=10)
    
    # "thin"キーで取得（デフォルトは"1.05"）
    coef_val = str(config_dict.get("thin", "1.05"))
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
    # 辞書から取得し、1(または"1", True)ならチェックを入れる
    saved_keep_temp = config_dict.get("keep_temp", 0)
    keep_temp_var.set(str(saved_keep_temp) in ("1", "True"))
    
    tk.Checkbutton(right_frame, text=getmsg("keep_temp"), variable=keep_temp_var).pack(pady=(20, 0), anchor="w")
    widget_dict["keep_temp"] = keep_temp_var

    # 保存ボタン
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
