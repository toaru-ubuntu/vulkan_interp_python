import os
import shutil
import platform

def info(msg, queue=None):
    """キューがあればqueue.put、なければprintする共通メッセージ関数"""
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)
        
def all_definition(temp_folder, config_path, material_folder, queue=None):
    # tempフォルダ削除
    if os.path.exists(temp_folder):
        try:
            shutil.rmtree(temp_folder)
            info("前回の temp フォルダを削除しました。", queue)
        except Exception as e:
            info(f"[ERROR] temp フォルダ削除中にエラー: {e}", queue)

    # temp_output.mkv と temp_audio.wav の削除
    for temp_file in ["temp_output.mkv", "temp_audio.wav"]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                info(f"{temp_file} を削除しました。", queue)
            except Exception as e:
                info(f"[ERROR] {temp_file} 削除中にエラー: {e}", queue)
            
    # configファイルの有無を確認
    if not os.path.exists(config_path):
        info("[ERROR] configファイルが見つかりません。", queue)
        info("設定変更ウィンドウから、一度「設定の保存」をして下さい。", queue)
        return None
                
    # materialフォルダの有無を確認
    if not os.path.exists(material_folder):
        info("[ERROR] material フォルダが見つかりません。", queue)
        info("materialフォルダを作成します。", queue)
        os.makedirs(material_folder, exist_ok=True)
        return None

    file_list = [entry.name for entry in os.scandir(material_folder) if entry.is_file()]
    if not file_list:
        info("[ERROR] material フォルダに動画ファイルが見つかりません。", queue)
        info("[ERROR] material フォルダに動画ファイルを置いて下さい。", queue)
        return "no_file"
    


