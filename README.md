# vulkan_interp_python

# Important Notice

This script automatically downloads and uses the [gyan.dev FFmpeg build](https://www.gyan.dev/ffmpeg/builds/).  
**This build cannot be used for commercial purposes. It is intended for personal and educational use only.**
If you need commercial use, please download FFmpeg from the official site [ffmpeg.org](https://ffmpeg.org/download.html).

This script also downloads the [rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan) executable and AI models directly from the official release page ([20221029](https://github.com/nihui/rife-ncnn-vulkan/releases/tag/20221029)).  
**While the rife-ncnn-vulkan executable is under the MIT License, the AI model files (.bin, .param, etc.) are prohibited from commercial use and redistribution.**  
This script does not include the model files in the repository, but instead downloads them directly from the official source.  
Please be sure to check the [rife-ncnn-vulkan license and usage conditions](https://github.com/nihui/rife-ncnn-vulkan#license).

This script itself is licensed under the MIT License.  
However, please always check and comply with the license terms for the FFmpeg binaries and other external tools.


# 注意事項

このスクリプトは [gyan.devのffmpegビルド](https://www.gyan.dev/ffmpeg/builds/) を自動ダウンロードして利用します。  
**このビルドは商用利用できません。個人利用・学習用途専用です。**
商用利用を希望する場合は、公式サイト [ffmpeg.org](https://ffmpeg.org/download.html) などから入手してください。

また、[rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan) の本体およびAIモデルを、公式リリースページ（[20221029](https://github.com/nihui/rife-ncnn-vulkan/releases/tag/20221029)）から自動ダウンロードする仕組みになっています。  
**rife-ncnn-vulkan本体はMIT Licenseですが、AIモデルファイル（.binや.paramなど）は商用利用・再配布が禁止されています。**  
本スクリプトでは、これらのモデルファイルをリポジトリに同梱せず、利用者が公式ページから直接取得する方式を採用しています。  
必ず[rife-ncnn-vulkanのライセンス・利用条件](https://github.com/nihui/rife-ncnn-vulkan#license)もご確認ください。

スクリプト自体のライセンスは MIT License です。  
ただし、ffmpegバイナリおよびrife-ncnn-vulkan等の外部ツールの利用条件を必ずご確認ください。


