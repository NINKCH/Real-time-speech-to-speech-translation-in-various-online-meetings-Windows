"""
音频采集模块
从麦克风实时采集音频数据
"""
import numpy as np
import sounddevice as sd
import queue
import threading
from typing import Callable, Optional


class AudioCapture:
    """麦克风音频采集"""
    
    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 0.08):
        """
        初始化音频采集
        
        Args:
            sample_rate: 采样率（Hz）
            chunk_duration: 音频块时长（秒），建议80ms
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        
        # 音频队列
        self.audio_queue = queue.Queue()
        
        # 流和线程
        self.stream = None
        self.is_capturing = False
        self.capture_thread = None
        
        # 回调函数
        self.on_audio_chunk: Optional[Callable] = None
        
        print(f"音频采集初始化: {sample_rate}Hz, {chunk_duration*1000:.0f}ms/块")
    
    def list_devices(self) -> list:
        """列出可用的音频输入设备"""
        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices
    
    def print_devices(self):
        """打印可用设备"""
        print("\n可用音频输入设备:")
        print("-" * 60)
        for device in self.list_devices():
            print(f"[{device['index']}] {device['name']}")
            print(f"     声道: {device['channels']}, 采样率: {device['sample_rate']}Hz")
        print("-" * 60)
    
    def _audio_callback(self, indata, frames, time_info, status):
        """音频流回调"""
        if status:
            print(f"⚠️ 音频流状态: {status}")
        
        # 转换为numpy数组并放入队列
        audio_data = indata.copy().flatten()
        self.audio_queue.put(audio_data)
    
    def _capture_loop(self):
        """采集循环（在独立线程中运行）"""
        print("音频采集线程启动")
        
        while self.is_capturing:
            try:
                # 从队列获取音频块
                audio_chunk = self.audio_queue.get(timeout=1.0)
                
                # 调用回调函数
                if self.on_audio_chunk:
                    self.on_audio_chunk(audio_chunk)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 音频采集错误: {e}")
        
        print("音频采集线程停止")
    
    def start(self, device_index: Optional[int] = None):
        """
        开始采集音频
        
        Args:
            device_index: 设备索引（None=默认设备）
        """
        if self.is_capturing:
            print("⚠️ 音频采集已在运行")
            return
        
        try:
            # 创建音频输入流
            self.stream = sd.InputStream(
                device=device_index,
                channels=1,  # 单声道
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            
            # 启动流
            self.stream.start()
            print(f"✅ 音频流已启动: 设备={device_index}, 采样率={self.sample_rate}Hz")
            
            # 启动采集线程
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            print("✅ 音频采集已启动")
            
        except Exception as e:
            print(f"❌ 启动音频采集失败: {e}")
            self.stop()
            raise
    
    def stop(self):
        """停止音频采集"""
        if not self.is_capturing:
            return
        
        print("正在停止音频采集...")
        
        # 停止采集线程
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
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
        
        print("✅ 音频采集已停止")
    
    def register_callback(self, callback: Callable):
        """注册音频回调函数"""
        self.on_audio_chunk = callback
    
    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """获取音频音量（RMS）"""
        rms = np.sqrt(np.mean(audio_data**2))
        return float(rms)
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.is_capturing
    
    def __del__(self):
        """析构函数"""
        self.stop()


# 测试代码
if __name__ == "__main__":
    import time
    
    # 创建音频采集器
    capture = AudioCapture(sample_rate=16000, chunk_duration=0.08)
    
    # 打印可用设备
    capture.print_devices()
    
    # 音频块计数
    chunk_count = [0]
    
    def on_audio(audio_data):
        chunk_count[0] += 1
        level = capture.get_audio_level(audio_data)
        print(f"音频块 #{chunk_count[0]}: 长度={len(audio_data)}, 音量={level:.4f}")
    
    capture.register_callback(on_audio)
    
    # 开始采集
    print("\n开始采集音频（持续5秒）...")
    capture.start()
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        capture.stop()
    
    print(f"\n✅ 测试完成，共采集 {chunk_count[0]} 个音频块")
