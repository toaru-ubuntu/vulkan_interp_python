import os

def info(msg, queue=None):
    if queue is not None:
        queue.put(msg + "\n")
    else:
        print(msg)
        
def setting_information(config_path, queue=None):
    # configファイルから値取得
    with open(config_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    magnification = lines[0]
    process = lines[2]
    video_codec = lines[4]
    bitrate = lines[5]
    scene_chanege = lines[6]
    ratio = lines[7]
    
    info(f"補間倍率{magnification}倍。", queue)
    info(f"プロセス数{process}。", queue)
    info(f"{video_codec}でエンコードします。", queue)
    info(f"ビットレートは{bitrate}。", queue)
    info(f"シーンチェンジのしきい値は{scene_chanege}。", queue)
    info(f"間引き係数は{ratio}。", queue)
