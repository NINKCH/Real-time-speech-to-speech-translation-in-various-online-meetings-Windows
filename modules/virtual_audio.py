"""
虚拟音频输出模块
将TTS音频输出到虚拟麦克风设备（VB-Cable）
"""
import numpy as np
import sounddevice as sd
import queue
import threading
from typing import Optional
import wave
import os

class VirtualAudioOutput:
    """虚拟麦克风音频输出"""
    
    def __init__(self, device_name: str = "CABLE Input", sample_rate: int = 24000, device_index: int = None, debug_save_audio: bool = False):
        """
        初始化虚拟音频输出
        
        Args:
            device_name: 虚拟设备名称
            sample_rate: 采样率
            device_index: 指定设备索引（如果提供则直接使用，不按名称查找）
            debug_save_audio: 是否保存调试音频文件到audio_debug目录
        """
        self.device_name = device_name
        self.sample_rate = sample_rate
        self.buffer_size = 1024
        self.force_device_index = device_index
        self.device_index = None
        self.is_playing = False
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        self.debug_save_audio = debug_save_audio  # 调试开关
        
        print(f"\n{'='*60}")
        print(f"初始化虚拟音频输出模块")
        print(f"{'='*60}")
        if device_index is not None:
            print(f"强制使用设备索引: [{device_index}]")
        else:
            print(f"目标设备: {device_name}")
        print(f"采样率: {sample_rate}Hz")
        
        # 查找虚拟设备
        self.device_index = self._find_device()
        
        if self.device_index is None:
            print("⚠️ 未找到虚拟音频设备，请确保已安装 VB-Audio Virtual Cable")
        else:
            if device_index is not None:
                print(f"✅ 强制使用虚拟音频输出设备: [{self.device_index}] (采样率: {self.sample_rate}Hz)")
            else:
                print(f"✅ 找到虚拟音频输出设备: [{self.device_index}] {self.device_name} (采样率: {self.sample_rate}Hz)")
            
            if self.debug_save_audio:
                print(f"🔍 调试模式已启用：将保存音频到 audio_debug/ 目录")
        
        # 音频队列
        self.audio_queue = queue.Queue()
        
        # 流和线程
        self.stream = None
        self.is_playing = False
        self.playback_thread = None
        
        if self.device_index is not None:
            print(f"✅ 虚拟音频输出初始化成功: device=[{self.device_index}], rate={sample_rate}Hz")
        else:
            print(f"⚠️  警告: 未找到虚拟音频设备，将使用默认输出")
        print(f"{'='*60}\n")
    
    def _find_device(self) -> Optional[int]:
        """查找虚拟音频设备"""
        try:
            devices = sd.query_devices()
            
            # 如果指定了设备索引，直接使用
            if self.force_device_index is not None:
                if self.force_device_index >= len(devices):
                    print(f"❌ 错误：设备索引 [{self.force_device_index}] 超出范围（总共 {len(devices)} 个设备）")
                    return None
                
                device = devices[self.force_device_index]
                print(f"\n✅ 使用指定设备: [{self.force_device_index}] {device['name']}")
                print(f"   输出通道: {device['max_output_channels']}")
                print(f"   设备采样率: {device['default_samplerate']}Hz")
                
                # 自动调整采样率
                device_sample_rate = int(device['default_samplerate'])
                if device_sample_rate != self.sample_rate:
                    print(f"⚠️  设备默认采样率 {device_sample_rate}Hz 与程序采样率 {self.sample_rate}Hz 不匹配")
                    print(f"   自动调整为设备采样率: {device_sample_rate}Hz")
                    self.sample_rate = device_sample_rate
                
                return self.force_device_index
            
            # 否则按名称查找
            print(f"\n扫描音频输出设备...")
            
            # 列出所有输出设备
            output_devices = []
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    output_devices.append((i, device['name']))
                    print(f"  [{i}] {device['name']} (输出通道: {device['max_output_channels']})")
            
            print(f"\n查找目标设备: {self.device_name}")
            
            # 精确匹配（不区分大小写）
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    if self.device_name.lower() in device['name'].lower():
                        print(f"✅ 精确匹配找到设备: [{i}] {device['name']}")
                        # 使用设备的默认采样率
                        device_sample_rate = int(device['default_samplerate'])
                        if device_sample_rate != self.sample_rate:
                            print(f"⚠️  设备默认采样率 {device_sample_rate}Hz 与程序采样率 {self.sample_rate}Hz 不匹配")
                            print(f"   自动调整为设备采样率: {device_sample_rate}Hz")
                            self.sample_rate = device_sample_rate
                        return i
            
            # 部分匹配
            print(f"\n精确匹配失败，尝试关键词匹配...")
            keywords = ["CABLE", "Virtual", "VB-Audio"]
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:
                    for keyword in keywords:
                        if keyword.lower() in device['name'].lower():
                            print(f"✅ 关键词匹配找到设备: [{i}] {device['name']} (关键词: {keyword})")
                            # 使用设备的默认采样率
                            device_sample_rate = int(device['default_samplerate'])
                            if device_sample_rate != self.sample_rate:
                                print(f"⚠️  设备默认采样率 {device_sample_rate}Hz 与程序采样率 {self.sample_rate}Hz 不匹配")
                                print(f"   自动调整为设备采样率: {device_sample_rate}Hz")
                                self.sample_rate = device_sample_rate
                            return i
            
            print(f"\n⚠️  未找到虚拟音频设备: {self.device_name}")
            print(f"⚠️  将使用默认输出设备")
            print(f"\n💡 提示:")
            print(f"   1. 请确保已安装 VB-Audio Virtual Cable")
            print(f"   2. 下载地址: https://vb-audio.com/Cable/")
            print(f"   3. 安装后重启程序")
            return None
            
        except Exception as e:
            print(f"❌ 查找音频设备错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_output_devices(self) -> list:
        """列出可用的音频输出设备"""
        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_output_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_output_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices
    
    def print_devices(self):
        """打印可用设备"""
        print("\n可用音频输出设备:")
        print("-" * 60)
        for device in self.list_output_devices():
            marker = " ✓" if device['index'] == self.device_index else ""
            print(f"[{device['index']}] {device['name']}{marker}")
            print(f"     声道: {device['channels']}, 采样率: {device['sample_rate']}Hz")
        print("-" * 60)
    
    def _playback_callback(self, outdata, frames, time_info, status):
        """播放回调"""
        if status:
            print(f"⚠️ 播放流状态: {status}")
        
        try:
            # 从队列获取音频
            audio_chunk = self.audio_queue.get_nowait()
            
            # 调整大小
            if len(audio_chunk) < frames:
                audio_chunk = np.pad(audio_chunk, (0, frames - len(audio_chunk)))
            elif len(audio_chunk) > frames:
                audio_chunk = audio_chunk[:frames]
            
            # 输出音频
            outdata[:] = audio_chunk.reshape(-1, 1)
            
        except queue.Empty:
            # 队列为空，输出静音
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)
    
    def _playback_loop(self):
        """播放循环"""
        print("音频播放线程启动")
        
        while self.is_playing:
            try:
                threading.Event().wait(0.1)
            except Exception as e:
                print(f"❌ 播放循环错误: {e}")
        
        print("音频播放线程停止")
    
    def start(self):
        """启动音频输出"""
        if self.is_playing:
            print("⚠️ 音频输出已在运行")
            return
        
        try:
            print(f"\n启动虚拟音频输出流...")
            
            # 获取设备信息
            if self.device_index is not None:
                device_info = sd.query_devices(self.device_index)
                print(f"目标设备: [{self.device_index}] {device_info['name']}")
            else:
                print(f"使用默认输出设备")
            
            # 创建输出流
            self.stream = sd.OutputStream(
                device=self.device_index,
                channels=1,  # 单声道
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                callback=self._playback_callback,
                dtype=np.float32
            )
            
            # 启动流
            self.stream.start()
            print(f"✅ 音频输出流已启动")
            print(f"   设备索引: {self.device_index}")
            print(f"   采样率: {self.sample_rate}Hz")
            print(f"   缓冲区大小: {self.buffer_size}")
            
            # 启动播放线程
            self.is_playing = True
            self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self.playback_thread.start()
            
            print("✅ 虚拟音频输出已启动并准备就绪")
            print(f"\n💡 音频流向: 程序 → [{self.device_index}] → 虚拟线缆 → CABLE Output → 会议软件\n")
            
        except Exception as e:
            print(f"❌ 启动音频输出失败: {e}")
            import traceback
            traceback.print_exc()
            self.stop()
            raise
    
    def stop(self):
        """停止音频输出"""
        if not self.is_playing:
            return
        
        print("正在停止音频输出...")
        
        # 停止播放线程
        self.is_playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=2.0)
        
        # 停止并关闭流
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"关闭音频流错误: {e}")
            finally:
                self.stream = None
        
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        print("✅ 音频输出已停止")
    
    def play(self, audio_data: np.ndarray):
        """
        播放音频数据
        
        Args:
            audio_data: 音频数据（float32, mono）
        """
        if not self.is_playing:
            print("⚠️ 音频输出未启动")
            return
        
        if len(audio_data) == 0:
            return
        
        # 确保float32格式
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # 分块加入队列
        chunk_size = self.buffer_size
        num_chunks = int(np.ceil(len(audio_data) / chunk_size))
        
        for i in range(num_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(audio_data))
            chunk = audio_data[start:end]
            self.audio_queue.put(chunk)
    
    def play_bytes(self, audio_bytes: bytes, format: str = "pcm", source_sample_rate: int = 48000):
        """
        播放音频字节数据
        
        Args:
            audio_bytes: 音频字节数据
            format: 音频格式 (pcm, ogg_opus)
            source_sample_rate: 源音频的采样率（默认48000Hz，来自TTS）
        """
        if format == "pcm":
            # PCM格式：直接转换
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            
            print(f"📥 接收TTS音频: {len(audio_bytes)}字节, {len(audio_float)}样本, 原始采样率{source_sample_rate}Hz")
            
            # 检查原始音频
            original_max = np.max(np.abs(audio_float))
            original_rms = np.sqrt(np.mean(audio_float**2))
            print(f"   原始振幅: 最大={original_max:.4f}, RMS={original_rms:.4f}")
            
            # 保存原始音频用于调试（仅在debug模式下）
            timestamp = None
            if self.debug_save_audio:
                import wave
                import os
                os.makedirs("audio_debug", exist_ok=True)
                from datetime import datetime
                timestamp = datetime.now().strftime("%H%M%S%f")
                
                # 保存原始音频
                original_wav = f"audio_debug/1_original_{source_sample_rate//1000}k_{timestamp}.wav"
                with wave.open(original_wav, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(source_sample_rate)
                    wf.writeframes(audio_bytes)
                print(f"   💾 原始音频已保存: {original_wav}")
            
            # === 简化处理：只用scipy高质量重采样，不做增益 ===
            if self.debug_save_audio:
                print(f"⚠️  调试模式：只重采样，不增益")
            
            # 重采样（如果需要）
            if source_sample_rate != self.sample_rate:
                from scipy import signal
                original_length = len(audio_float)
                target_length = int(original_length * self.sample_rate / source_sample_rate)
                
                print(f"🔄 使用scipy重采样: {source_sample_rate}Hz → {self.sample_rate}Hz")
                audio_float = signal.resample(audio_float, target_length)
                
                # 保存重采样后的音频（仅在debug模式下）
                if self.debug_save_audio and timestamp:
                    import wave
                    resampled_wav = f"audio_debug/2_resampled_{self.sample_rate//1000}k_{timestamp}.wav"
                    audio_int16_resampled = (audio_float * 32767).astype(np.int16)
                    with wave.open(resampled_wav, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(self.sample_rate)
                        wf.writeframes(audio_int16_resampled.tobytes())
                    print(f"   💾 重采样音频已保存: {resampled_wav}")
                
                resampled_max = np.max(np.abs(audio_float))
                print(f"   重采样后振幅: {resampled_max:.4f}")
            
            # 不做任何增益或削波处理，直接播放
            self.play(audio_float)
            
            duration_ms = len(audio_float) / self.sample_rate * 1000
            print(f"🔊 直接输出（无增益）: {len(audio_float)}样本 ({duration_ms:.0f}ms) @ {self.sample_rate}Hz → 设备[{self.device_index}]")
            
            if self.debug_save_audio:
                print(f"   💡 提示：可用媒体播放器打开 audio_debug/ 中的WAV文件检查音质")
            
        else:
            # 其他格式需要解码
            print(f"⚠️ 不支持的音频格式: {format}")
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.is_playing
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.audio_queue.qsize()
    
    def clear_queue(self):
        """清空队列"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def __del__(self):
        """析构函数"""
        self.stop()


# 测试代码
if __name__ == "__main__":
    import time
    
    # 创建虚拟音频输出
    output = VirtualAudioOutput(device_name="CABLE Input", sample_rate=24000)
    
    # 打印可用设备
    output.print_devices()
    
    if output.device_index is None:
        print("\n⚠️ 警告: 未找到虚拟音频设备")
        print("请安装 VB-Audio Virtual Cable: https://vb-audio.com/Cable/")
        print("将使用默认输出设备进行测试\n")
    
    # 启动输出
    print("\n开始音频输出测试...")
    output.start()
    
    # 生成测试音（440Hz正弦波，2秒）
    print("播放测试音（440Hz，2秒）...")
    duration = 2.0
    sample_rate = 24000
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4音符
    test_audio = (np.sin(2 * np.pi * frequency * t) * 0.3).astype(np.float32)
    
    # 播放测试音
    output.play(test_audio)
    
    # 等待播放完成
    time.sleep(duration + 0.5)
    
    # 停止输出
    output.stop()
    
    print("\n✅ 测试完成")
    
    if output.device_index is None:
        print("\n💡 提示: 安装VB-Cable后，在会议软件中选择'CABLE Output'作为麦克风")
