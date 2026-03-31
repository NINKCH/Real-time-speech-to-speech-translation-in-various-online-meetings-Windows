"""
豆包实时同声传译应用核心
整合音频采集、WebSocket通信、虚拟音频输出
"""
import asyncio
import numpy as np
from typing import Optional
from modules.ast_client_protobuf import ASTClientProtobuf as ASTClient
from modules.audio_capture import AudioCapture
from modules.virtual_audio import VirtualAudioOutput
from utils.logger import get_logger

logger = get_logger(__name__)


class RealtimeTranslatorApp:
    """实时翻译应用"""
    
    def __init__(
        self,
        app_key: str,
        access_key: str,
        resource_id: str = "volc.service_type.10053",
        mode: str = "s2s",
        source_language: str = "zh",
        target_language: str = "en",
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5,
        reconnect_delay: float = 3.0,
        debug_mode: bool = False
    ):
        """
        初始化应用
        
        Args:
            app_key: API App Key
            access_key: API Access Key
            resource_id: 资源ID
            mode: 模式
            source_language: 源语言
            target_language: 目标语言
            auto_reconnect: 是否自动重连
            max_reconnect_attempts: 最大重连次数
            reconnect_delay: 重连延迟
            debug_mode: 调试模式
        """
        self.app_key = app_key
        self.access_key = access_key
        self.resource_id = resource_id
        
        # 组件
        self.ast_client: Optional[ASTClient] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.virtual_output: Optional[VirtualAudioOutput] = None
        
        # 状态
        self.is_running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_reconnecting = False
        
        # 配置
        self.source_language = source_language
        self.target_language = target_language
        self.mode = mode  # s2s模式自动包含零样本声音复刻
        
        # 自动重连配置
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay  # 秒
        
        # 回调函数
        self.on_source_text_callback = None
        self.on_translation_text_callback = None
        self.on_error_callback = None
        self.on_status_callback = None
        
        # 调试模式
        self.debug_mode = debug_mode
        if self.debug_mode:
            logger.info("🔍 调试模式已启用")
        
        logger.info("应用初始化完成")
    
    def set_config(
        self,
        source_language: str = None,
        target_language: str = None,
        mode: str = None
    ):
        """设置配置"""
        if source_language:
            self.source_language = source_language
        if target_language:
            self.target_language = target_language
        if mode:
            self.mode = mode
        logger.info(f"配置更新: {self.source_language} -> {self.target_language}, mode={self.mode}")
        if mode == "s2s":
            logger.info("✨ 零样本声音复刻已启用（S2S模式自动包含）")
    
    def _init_components(self):
        """初始化各组件"""
        # 创建AST客户端
        from config import AST_CONFIG
        self.ast_client = ASTClient(self.app_key, self.access_key, self.resource_id,
                                      ws_url=AST_CONFIG["ws_url"], debug_mode=self.debug_mode)
        self.ast_client.set_config(
            mode=self.mode,
            source_language=self.source_language,
            target_language=self.target_language,
            source_audio_rate=16000,
            target_audio_rate=48000,  # 改为48000Hz匹配CABLE设备，避免重采样
            target_audio_format="pcm"  # 或 "ogg_opus"
            # 注意：s2s模式自动启用零样本声音复刻，无需配置speaker_id
        )
        
        # 设置AST客户端回调
        self.ast_client.on_source_text = self._on_source_text
        self.ast_client.on_translation_text = self._on_translation_text
        self.ast_client.on_tts_audio = self._on_tts_audio
        self.ast_client.on_error = self._on_error
        self.ast_client.on_session_finished = self._on_session_finished
        
        # 创建音频采集器
        self.audio_capture = AudioCapture(sample_rate=16000, chunk_duration=0.08)
        self.audio_capture.register_callback(self._on_audio_chunk)
        
        # 创建虚拟音频输出
        if self.mode == "s2s":
            self.virtual_output = VirtualAudioOutput(
                device_name="CABLE Input",
                sample_rate=48000,
                debug_save_audio=self.debug_mode
            )
        
        if self.debug_mode:
            logger.info("🔍 调试模式已启用：将保存音频文件到 audio_debug/ 目录")
        
        logger.info("所有组件初始化完成")
    
    def _on_audio_chunk(self, audio_data: np.ndarray):
        """音频块回调"""
        if self.is_running and self.ast_client and self.ast_client.is_connected:
            # 在事件循环中发送音频
            asyncio.run_coroutine_threadsafe(
                self.ast_client.send_audio(audio_data),
                self.loop
            )
    
    def _on_source_text(self, text: str, is_final: bool = False):
        """原文回调"""
        logger.info(f"原文{'(完整)' if is_final else ''}: {text}")
        if self.on_source_text_callback:
            self.on_source_text_callback(text, is_final)
    
    def _on_translation_text(self, text: str, is_final: bool = False):
        """译文回调"""
        logger.info(f"译文{'(完整)' if is_final else ''}: {text}")
        if self.on_translation_text_callback:
            self.on_translation_text_callback(text, is_final)
    
    def _on_tts_audio(self, audio_bytes: bytes):
        """TTS音频回调"""
        if self.virtual_output and self.virtual_output.is_running():
            self.virtual_output.play_bytes(audio_bytes, format="pcm")
            logger.debug(f"播放TTS音频: {len(audio_bytes)} 字节")
    
    def _on_error(self, error_msg: str):
        """错误回调"""
        logger.error(f"错误: {error_msg}")
        
        # 检查是否是连接错误需要重连
        if self.auto_reconnect and self.is_running and not self.is_reconnecting:
            if any(keyword in error_msg.lower() for keyword in 
                   ['rst_stream', 'connection', 'timeout', '会话异常']):
                logger.warning("检测到连接错误，准备自动重连...")
                # 异步触发重连
                if self.loop:
                    asyncio.run_coroutine_threadsafe(
                        self._auto_reconnect(),
                        self.loop
                    )
        
        if self.on_error_callback:
            self.on_error_callback(error_msg)
    
    def _on_session_finished(self):
        """会话结束回调"""
        logger.info("会话结束")
        
        # 如果应用还在运行，可能是服务器主动结束，尝试重连
        if self.auto_reconnect and self.is_running and not self.is_reconnecting:
            logger.warning("会话意外结束，准备自动重连...")
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self._auto_reconnect(),
                    self.loop
                )
        
        if self.on_status_callback:
            self.on_status_callback("会话结束")
    
    async def _auto_reconnect(self):
        """自动重连"""
        if self.is_reconnecting:
            logger.info("已经在重连中，跳过")
            return
        
        self.is_reconnecting = True
        
        try:
            for attempt in range(1, self.max_reconnect_attempts + 1):
                logger.info(f"尝试重连 ({attempt}/{self.max_reconnect_attempts})...")
                
                if self.on_status_callback:
                    self.on_status_callback(f"重连中({attempt}/{self.max_reconnect_attempts})...")
                
                # 先关闭旧连接
                if self.ast_client and self.ast_client.is_connected:
                    try:
                        await self.ast_client.close()
                        await asyncio.sleep(1)
                    except:
                        pass
                
                # 等待一下再重连
                await asyncio.sleep(self.reconnect_delay)
                
                # 重新连接
                try:
                    if await self.ast_client.connect():
                        # 重启接收循环
                        asyncio.create_task(self.ast_client.receive_loop())
                        
                        logger.info("✅ 重连成功！")
                        if self.on_status_callback:
                            self.on_status_callback("运行中（已重连）")
                        
                        self.is_reconnecting = False
                        return
                    
                except Exception as e:
                    logger.error(f"重连失败: {e}")
                
            # 所有重连尝试都失败
            logger.error("所有重连尝试均失败")
            if self.on_error_callback:
                self.on_error_callback("连接丢失，自动重连失败，请重启应用")
            if self.on_status_callback:
                self.on_status_callback("连接失败")
            
        finally:
            self.is_reconnecting = False
    
    async def _start_async(self) -> bool:
        """异步启动"""
        try:
            # 连接AST服务
            if self.on_status_callback:
                self.on_status_callback("正在连接...")
            
            if not await self.ast_client.connect():
                logger.error("连接AST服务失败")
                return False
            
            # 启动虚拟音频输出
            if self.virtual_output:
                self.virtual_output.start()
            
            # 启动音频采集
            self.audio_capture.start()
            
            # 启动AST接收循环
            asyncio.create_task(self.ast_client.receive_loop())
            
            self.is_running = True
            
            if self.on_status_callback:
                self.on_status_callback("运行中")
            
            logger.info("✅ 应用启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动失败: {e}", exc_info=True)
            return False
    
    def start(self) -> bool:
        """
        启动应用
        
        Returns:
            是否成功启动
        """
        if self.is_running:
            logger.warning("应用已在运行")
            return False
        
        try:
            # 初始化组件
            self._init_components()
            
            # 创建事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # 在新线程中运行事件循环
            import threading
            
            def run_loop():
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
            
            loop_thread = threading.Thread(target=run_loop, daemon=True)
            loop_thread.start()
            
            # 启动应用
            future = asyncio.run_coroutine_threadsafe(
                self._start_async(),
                self.loop
            )
            
            return future.result(timeout=10.0)
            
        except Exception as e:
            logger.error(f"启动错误: {e}", exc_info=True)
            return False
    
    async def _stop_async(self):
        """异步停止"""
        try:
            # 停止音频采集
            if self.audio_capture:
                self.audio_capture.stop()
            
            # 停止虚拟音频输出
            if self.virtual_output:
                self.virtual_output.stop()
            
            # 关闭AST连接
            if self.ast_client:
                await self.ast_client.close()
            
            logger.info("应用已停止")
            
        except Exception as e:
            logger.error(f"停止错误: {e}", exc_info=True)
    
    def stop(self):
        """停止应用"""
        if not self.is_running:
            return
        
        logger.info("正在停止应用...")
        self.is_running = False
        
        if self.on_status_callback:
            self.on_status_callback("正在停止...")
        
        # 异步停止
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._stop_async(),
                self.loop
            )
            try:
                future.result(timeout=5.0)
            except Exception as e:
                logger.error(f"停止超时: {e}")
            
            # 停止事件循环
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.on_status_callback:
            self.on_status_callback("已停止")
        
        logger.info("✅ 应用已停止")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        if self.ast_client:
            return self.ast_client.get_stats()
        return {}


# 测试代码
if __name__ == "__main__":
    import os
    import time
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app_key = os.getenv("DOUBAO_APP_KEY", "")
    access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
    
    if not app_key or not access_key:
        print("❌ 请在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY")
        exit(1)
    
    print("=" * 60)
    print("豆包实时同声传译应用测试")
    print("=" * 60)
    
    # 创建应用
    app = RealtimeTranslatorApp(app_key, access_key)
    app.set_config(source_language="zh", target_language="en", mode="s2s")
    
    # 设置回调
    def on_source(text, is_final=False):
        print(f"{'【原文-完整】' if is_final else '【原文】'} {text}")
    
    def on_translation(text, is_final=False):
        print(f"{'【译文-完整】' if is_final else '【译文】'} {text}")
    
    def on_error(error):
        print(f"【错误】 {error}")
    
    def on_status(status):
        print(f"【状态】 {status}")
    
    app.on_source_text_callback = on_source
    app.on_translation_text_callback = on_translation
    app.on_error_callback = on_error
    app.on_status_callback = on_status
    
    # 启动
    print("\n启动应用...")
    if app.start():
        print("✅ 应用已启动，请对着麦克风说话...")
        print("按 Ctrl+C 停止\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n用户中断")
    else:
        print("❌ 启动失败")
    
    # 停止
    app.stop()
    
    # 打印统计
    stats = app.get_stats()
    print(f"\n统计信息: {stats}")
    print("\n✅ 测试完成")
