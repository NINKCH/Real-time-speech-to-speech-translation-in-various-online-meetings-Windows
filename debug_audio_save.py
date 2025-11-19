"""
调试工具：保存TTS音频数据用于分析
在 modules/virtual_audio.py 的 play_bytes 方法中临时添加
"""

import numpy as np
import wave
import struct
import os
from datetime import datetime

def save_audio_debug(audio_data, sample_rate, prefix="debug"):
    """
    保存音频数据为WAV文件用于调试
    
    Args:
        audio_data: numpy数组，float32格式
        sample_rate: 采样率
        prefix: 文件名前缀
    """
    # 创建调试目录
    debug_dir = "audio_debug"
    os.makedirs(debug_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%H%M%S")
    filename = os.path.join(debug_dir, f"{prefix}_{timestamp}.wav")
    
    # 转换为int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # 保存为WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    
    print(f"📁 调试音频已保存: {filename}")
    return filename


# 使用示例：在 modules/virtual_audio.py 的 play_bytes 方法中添加

"""
在 play_bytes 方法中添加以下代码：

第311行之后（PCM转换后）：
    audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
    audio_float = audio_int16.astype(np.float32) / 32768.0
    
    # === 添加这里 ===
    import sys
    sys.path.insert(0, '.')
    from debug_audio_save import save_audio_debug
    save_audio_debug(audio_float, source_sample_rate, "1_original")
    # ===============

在重采样之后（第333行之后）：
    print(f"🔄 重采样: {source_sample_rate}Hz → {self.sample_rate}Hz ...")
    
    # === 添加这里 ===
    save_audio_debug(audio_float, self.sample_rate, "2_resampled")
    # ===============

在增强之后（第357行之后）：
    print(f"🔊 音频增强: ...")
    
    # === 添加这里 ===
    save_audio_debug(audio_float, self.sample_rate, "3_enhanced")
    # ===============
"""

print("""
使用方法：
1. 这个文件提供了 save_audio_debug 函数
2. 在 modules/virtual_audio.py 中临时添加调用
3. 运行程序翻译
4. 在 audio_debug/ 目录下会生成WAV文件
5. 用音频播放器听这些文件，找出哪一步出了问题
""")
