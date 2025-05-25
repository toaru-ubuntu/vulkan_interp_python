import os
import platform
import urllib.request
import zipfile
import shutil

def info(msg, queue=None):
    """キューがあればqueue.put、なければprintする共通メッセージ関数"""
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)
        
def download_rife(rife_dest_dir="rife", queue=None):
    system = platform.system().lower()
    if system == "windows":
        zip_url = "https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-windows.zip"
        rife_binary = "rife-ncnn-vulkan.exe"
        extracted_folder_name = "rife-ncnn-vulkan-20221029-windows"
    elif system == "linux":
        zip_url = "https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-ubuntu.zip"
        rife_binary = "rife-ncnn-vulkan"
        extracted_folder_name = "rife-ncnn-vulkan-20221029-ubuntu"
    else:
        info(f"{system} は未対応です。",)
        return

    rife_bin_path = os.path.join(rife_dest_dir, rife_binary)
    
    #rife-ncnn-vulkanが存在するか確認
    if os.path.exists(rife_bin_path):
        info(f"{rife_binary}はダウンロード済みです。", queue)
        return
        
    zip_name = "rife.zip"
    temp_extract_dir = "rife_temp"

    os.makedirs(rife_dest_dir, exist_ok=True)

    info(f"{rife_binary} をダウンロードしています...", queue)
    try:
        urllib.request.urlretrieve(zip_url, zip_name)
    except Exception as e:
        info(f"{rife_binary}のダウンロード中にエラーが発生しました: {e}", queue)
        return
        
    info("展開中...", queue)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    extracted_root = os.path.join(temp_extract_dir, extracted_folder_name)
    if not os.path.exists(extracted_root):
        raise FileNotFoundError(f"展開後のフォルダが見つかりません: {extracted_root}")

    for item in os.listdir(extracted_root):
        src_path = os.path.join(extracted_root, item)
        dst_path = os.path.join(rife_dest_dir, item)
        shutil.move(src_path, dst_path)

    # Linuxの場合は実行権限を付与
    if system == "linux":
        os.chmod(rife_bin_path, 0o755)

    shutil.rmtree(temp_extract_dir)
    os.remove(zip_name)

    info(f"{rife_binary} のセットアップが完了しました。", queue)

