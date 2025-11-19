"""
豆包同声传译 2.0 API WebSocket客户端
实现实时音频翻译（STT + 翻译 + TTS 一体化）
"""
import asyncio
import json
import uuid
import websockets
import numpy as np
from typing import Optional, Callable
from protos.ast_pb2 import (
    EventType,
    create_start_session_message,
    create_task_request_message,
    create_finish_session_message,
    get_event_name
)


class ASTClient:
    """豆包同声传译WebSocket客户端"""
    
    def __init__(self, app_key: str, access_key: str, resource_id: str = "volc.service_type.10053"):
        """
        初始化客户端
        
        Args:
            app_key: API App Key
            access_key: API Access Key
            resource_id: 资源ID（默认值即可）
        """
        self.app_key = app_key
        self.access_key = access_key
        self.resource_id = resource_id
        
        # WebSocket连接
        self.ws = None
        self.session_id = None
        self.is_connected = False
        self.is_running = False
        
        # 配置
        self.mode = "s2s"  # s2s 或 s2t
        self.source_language = "zh"
        self.target_language = "en"
        self.source_audio_rate = 16000
        self.target_audio_rate = 24000
        
        # 回调函数
        self.on_source_text: Optional[Callable] = None  # 原文回调
        self.on_translation_text: Optional[Callable] = None  # 译文回调
        self.on_tts_audio: Optional[Callable] = None  # TTS音频回调
        self.on_error: Optional[Callable] = None  # 错误回调
        self.on_session_finished: Optional[Callable] = None  # 会话结束回调
        
        # 统计信息
        self.stats = {
            "source_segments": 0,
            "translation_segments": 0,
            "tts_chunks": 0,
            "errors": 0
        }
    
    def set_config(
        self,
        mode: str = None,
        source_language: str = None,
        target_language: str = None,
        source_audio_rate: int = None,
        target_audio_rate: int = None
    ):
        """设置配置"""
        if mode:
            self.mode = mode
        if source_language:
            self.source_language = source_language
        if target_language:
            self.target_language = target_language
        if source_audio_rate:
            self.source_audio_rate = source_audio_rate
        if target_audio_rate:
            self.target_audio_rate = target_audio_rate
    
    async def connect(self) -> bool:
        """
        建立WebSocket连接
        
        Returns:
            是否成功连接
        """
        try:
            # WebSocket URL
            url = "wss://openspeech.bytedance.com/api/v4/ast/v2/translate"
            
            # 鉴权头
            headers = {
                "X-Api-App-Key": self.app_key,
                "X-Api-Access-Key": self.access_key,
                "X-Api-Resource-Id": self.resource_id
            }
            
            print(f"正在连接到 {url}...")
            
            # 建立WebSocket连接
            self.ws = await websockets.connect(url, additional_headers=headers)
            
            # 生成session_id
            self.session_id = str(uuid.uuid4())
            
            # 发送建联请求
            start_message = create_start_session_message(
                session_id=self.session_id,
                mode=self.mode,
                source_language=self.source_language,
                target_language=self.target_language,
                source_audio_rate=self.source_audio_rate,
                target_audio_rate=self.target_audio_rate
            )
            
            # 发送JSON消息
            await self.ws.send(json.dumps(start_message))
            print(f"✅ 已发送建联请求 (session_id: {self.session_id})")
            
            # 等待SessionStarted响应
            response = await self.ws.recv()
            
            # 检查响应类型
            print(f"收到响应类型: {type(response)}")
            print(f"响应前20字节: {response[:20] if isinstance(response, bytes) else response[:100]}")
            
            # 如果是二进制数据，尝试解码
            if isinstance(response, bytes):
                print("⚠️ 收到二进制Protobuf数据，当前版本暂不支持")
                print("💡 提示：豆包AST 2.0 API使用Protobuf格式，需要编译proto文件")
                return False
            
            response_data = json.loads(response)
            
            if response_data.get("event") == EventType.SessionStarted:
                self.is_connected = True
                print("✅ 会话建立成功！")
                return True
            else:
                print(f"❌ 建联失败: {response_data}")
                return False
                
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            if self.on_error:
                self.on_error(f"连接错误: {e}")
            return False
    
    async def send_audio(self, audio_data: np.ndarray):
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据 (float32, 16kHz, mono)
        """
        if not self.is_connected or not self.ws:
            print("⚠️ 未连接，无法发送音频")
            return
        
        try:
            # 转换为int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            
            # 创建TaskRequest消息
            task_message = create_task_request_message(audio_bytes)
            
            # 发送音频数据（二进制格式）
            # 注意：实际的protobuf应该使用二进制序列化
            # 这里简化处理，使用JSON + base64
            import base64
            task_message["source_audio"]["data"] = base64.b64encode(audio_bytes).decode('utf-8')
            
            await self.ws.send(json.dumps(task_message))
            
        except Exception as e:
            print(f"❌ 发送音频错误: {e}")
            if self.on_error:
                self.on_error(f"发送音频错误: {e}")
    
    async def finish_session(self):
        """结束会话"""
        if not self.is_connected or not self.ws:
            return
        
        try:
            finish_message = create_finish_session_message()
            await self.ws.send(json.dumps(finish_message))
            print("✅ 已发送结束会话请求")
        except Exception as e:
            print(f"❌ 结束会话错误: {e}")
    
    async def _handle_message(self, message_data: dict):
        """处理接收到的消息"""
        event_type = message_data.get("event")
        event_name = get_event_name(event_type)
        
        # 原文字幕
        if event_type == EventType.SourceSubtitleResponse:
            text = message_data.get("text", "")
            if text and self.on_source_text:
                self.on_source_text(text)
            self.stats["source_segments"] += 1
        
        elif event_type == EventType.SourceSubtitleEnd:
            text = message_data.get("text", "")
            if text and self.on_source_text:
                self.on_source_text(text, is_final=True)
        
        # 译文字幕
        elif event_type == EventType.TranslationSubtitleResponse:
            text = message_data.get("text", "")
            if text and self.on_translation_text:
                self.on_translation_text(text)
            self.stats["translation_segments"] += 1
        
        elif event_type == EventType.TranslationSubtitleEnd:
            text = message_data.get("text", "")
            if text and self.on_translation_text:
                self.on_translation_text(text, is_final=True)
        
        # TTS音频
        elif event_type == EventType.TTSResponse:
            audio_data = message_data.get("data")
            if audio_data and self.on_tts_audio:
                # 解码base64音频数据
                import base64
                audio_bytes = base64.b64decode(audio_data)
                self.on_tts_audio(audio_bytes)
            self.stats["tts_chunks"] += 1
        
        # 计量计费
        elif event_type == EventType.UsageResponse:
            meta = message_data.get("response_meta", {})
            billing = meta.get("billing", {})
            print(f"💰 计费信息: {billing}")
        
        # 会话结束
        elif event_type == EventType.SessionFinished:
            print("✅ 会话正常结束")
            if self.on_session_finished:
                self.on_session_finished()
        
        # 会话失败
        elif event_type == EventType.SessionFailed:
            meta = message_data.get("response_meta", {})
            error_msg = meta.get("message", "未知错误")
            print(f"❌ 会话失败: {error_msg}")
            if self.on_error:
                self.on_error(f"会话失败: {error_msg}")
            self.stats["errors"] += 1
        
        # 静音事件
        elif event_type == EventType.AudioMuted:
            duration = message_data.get("muted_duration_ms", 0)
            print(f"🔇 检测到静音: {duration}ms")
    
    async def receive_loop(self):
        """接收消息循环"""
        print("开始接收消息...")
        self.is_running = True
        
        try:
            while self.is_running and self.ws:
                try:
                    # 接收消息
                    message = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
                    
                    # 解析JSON
                    message_data = json.loads(message)
                    
                    # 处理消息
                    await self._handle_message(message_data)
                    
                except asyncio.TimeoutError:
                    # 超时，发送心跳或继续等待
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("⚠️ WebSocket连接已关闭")
                    break
                    
        except Exception as e:
            print(f"❌ 接收消息错误: {e}")
            if self.on_error:
                self.on_error(f"接收消息错误: {e}")
        finally:
            self.is_running = False
            self.is_connected = False
    
    async def close(self):
        """关闭连接"""
        print("正在关闭连接...")
        self.is_running = False
        
        if self.ws:
            try:
                await self.finish_session()
                await asyncio.sleep(0.5)
                await self.ws.close()
            except Exception as e:
                print(f"关闭连接错误: {e}")
            finally:
                self.ws = None
        
        self.is_connected = False
        print("✅ 连接已关闭")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()


# 测试代码
async def test_client():
    """测试客户端"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app_key = os.getenv("DOUBAO_APP_KEY", "")
    access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
    
    if not app_key or not access_key:
        print("❌ 请在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY")
        return
    
    # 创建客户端
    client = ASTClient(app_key, access_key)
    
    # 设置回调
    def on_source(text, is_final=False):
        prefix = "【原文-完整】" if is_final else "【原文】"
        print(f"{prefix} {text}")
    
    def on_translation(text, is_final=False):
        prefix = "【译文-完整】" if is_final else "【译文】"
        print(f"{prefix} {text}")
    
    def on_audio(audio_bytes):
        print(f"【TTS音频】 收到 {len(audio_bytes)} 字节")
    
    client.on_source_text = on_source
    client.on_translation_text = on_translation
    client.on_tts_audio = on_audio
    
    # 连接
    if await client.connect():
        # 启动接收循环
        receive_task = asyncio.create_task(client.receive_loop())
        
        # 模拟发送音频（这里需要真实的音频数据）
        print("\n提示：需要真实的音频数据进行完整测试")
        
        # 等待一段时间
        await asyncio.sleep(5)
        
        # 关闭
        await client.close()
        await receive_task


if __name__ == "__main__":
    asyncio.run(test_client())
