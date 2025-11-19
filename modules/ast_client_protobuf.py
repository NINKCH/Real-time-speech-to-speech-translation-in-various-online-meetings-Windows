"""
豆包同声传译 2.0 API WebSocket客户端 - Protobuf版本
基于官方Demo实现
"""
import asyncio
import uuid
import websockets
import numpy as np
import sys
import os
from typing import Optional, Callable
from pathlib import Path

# 添加python_protogen到路径
current_dir = Path(__file__).parent.parent
protogen_dir = current_dir / "python_protogen"
sys.path.insert(0, str(protogen_dir))

# 导入Protobuf生成的代码
from products.understanding.ast.ast_service_pb2 import TranslateRequest, TranslateResponse
from common.events_pb2 import Type


class ASTClientProtobuf:
    """AST WebSocket客户端 - 使用Protobuf协议"""
    
    def __init__(self, app_key: str, access_key: str, resource_id: str = "volc.service_type.10053", debug_mode: bool = False):
        """
        初始化客户端
        
        Args:
            app_key: API App Key
            access_key: API Access Key
            resource_id: 资源ID
            debug_mode: 是否启用调试模式（打印详细的TTS响应信息）
        """
        self.app_key = app_key
        self.access_key = access_key
        self.resource_id = resource_id
        self.debug_mode = debug_mode
        
        # WebSocket连接
        self.ws = None
        self.is_connected = False
        self.session_id = None
        self.conn_id = None
        
        # 配置
        self.mode = "s2s"  # s2s模式自动包含零样本声音复刻
        self.source_language = "zh"
        self.target_language = "en"
        self.source_audio_rate = 16000
        self.target_audio_rate = 24000
        self.target_audio_format = "pcm"  # 或 "ogg_opus"
        self.speaker_id = ""  # 保留用于传统声音复刻1.0（可选，同传2.0不需要）
        
        # 回调函数
        self.on_source_text: Optional[Callable] = None
        self.on_translation_text: Optional[Callable] = None
        self.on_tts_audio: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_session_finished: Optional[Callable] = None
        
        # 统计
        self.stats = {
            "audio_chunks_sent": 0,
            "source_text_received": 0,
            "translation_text_received": 0,
            "tts_chunks": 0,
            "errors": 0
        }
    
    def set_config(
        self,
        mode: str = None,
        source_language: str = None,
        target_language: str = None,
        source_audio_rate: int = None,
        target_audio_rate: int = None,
        target_audio_format: str = None,
        speaker_id: str = None
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
        if target_audio_format:
            self.target_audio_format = target_audio_format
        if speaker_id is not None:
            self.speaker_id = speaker_id
    
    async def connect(self) -> bool:
        """
        建立WebSocket连接并启动会话
        
        Returns:
            是否成功连接
        """
        try:
            url = "wss://openspeech.bytedance.com/api/v4/ast/v2/translate"
            
            # 生成连接ID
            self.conn_id = str(uuid.uuid4())
            
            # 构建Headers
            headers = {
                "X-Api-App-Key": self.app_key,
                "X-Api-Access-Key": self.access_key,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-Connect-Id": self.conn_id
            }
            
            print(f"正在连接到 {url}...")
            
            # 建立WebSocket连接
            self.ws = await websockets.connect(
                url,
                additional_headers=headers,
                max_size=1000000000,  # 1GB
                ping_interval=None
            )
            
            # 获取Log ID（用于调试）
            log_id = self.ws.response.headers.get('X-Tt-Logid')
            print(f"✅ 已连接到服务器 (Log ID: {log_id})")
            
            # 生成Session ID
            self.session_id = str(uuid.uuid4())
            
            # 发送StartSession请求
            start_request = self._create_start_session_request()
            await self.ws.send(start_request.SerializeToString())
            print(f"✅ 已发送建联请求 (Session ID: {self.session_id})")
            
            # 等待SessionStarted响应
            response_bytes = await self.ws.recv()
            response = TranslateResponse()
            response.ParseFromString(response_bytes)
            
            if response.event == Type.SessionStarted:
                self.is_connected = True
                print(f"✅ 会话建立成功！")
                return True
            else:
                print(f"❌ 建联失败: event={response.event}, message={response.response_meta.Message}")
                if self.on_error:
                    self.on_error(f"建联失败: {response.response_meta.Message}")
                return False
                
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            if self.on_error:
                self.on_error(f"连接错误: {e}")
            return False
    
    def _create_start_session_request(self) -> TranslateRequest:
        """创建StartSession请求"""
        request = TranslateRequest()
        
        # 设置元数据
        request.request_meta.SessionID = self.session_id
        request.event = Type.StartSession
        
        # 设置用户信息
        request.user.uid = "realtime_ast_translator"
        request.user.did = "windows_pc"
        
        # 设置源音频参数
        request.source_audio.format = "wav"
        request.source_audio.rate = self.source_audio_rate
        request.source_audio.bits = 16
        request.source_audio.channel = 1
        
        # 设置目标音频参数
        request.target_audio.format = self.target_audio_format
        request.target_audio.rate = self.target_audio_rate
        
        # 设置翻译参数
        request.request.mode = self.mode
        request.request.source_language = self.source_language
        request.request.target_language = self.target_language
        
        # 打印配置信息用于调试
        print(f"\n{'='*70}")
        print(f"📋 StartSession 配置详情")
        print(f"{'='*70}")
        print(f"  Mode: {self.mode}")
        print(f"  Source Language: {self.source_language}")
        print(f"  Target Language: {self.target_language}")
        print(f"  Source Audio: format={request.source_audio.format}, rate={request.source_audio.rate}Hz, bits={request.source_audio.bits}, channel={request.source_audio.channel}")
        print(f"  Target Audio: format={request.target_audio.format}, rate={request.target_audio.rate}Hz")
        print(f"{'='*70}\n")
        
        # 设置声音克隆ID（仅用于传统声音复刻1.0，同传2.0的S2S模式自动包含零样本声音复刻）
        if self.speaker_id:
            request.request.speaker_id = self.speaker_id
            print(f"✨ 使用传统声音复刻: {self.speaker_id}")
        else:
            if self.mode == "s2s":
                print(f"✨ 零样本声音复刻已启用（S2S模式自动包含）")
        
        return request
    
    async def send_audio(self, audio_data: np.ndarray):
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据 (float32, mono)
        """
        if not self.is_connected or not self.ws:
            print("⚠️ 未连接，无法发送音频")
            return
        
        try:
            # 转换为int16 PCM格式
            audio_int16 = (audio_data * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            
            # 创建TaskRequest
            request = TranslateRequest()
            request.request_meta.SessionID = self.session_id
            request.event = Type.TaskRequest
            request.source_audio.binary_data = audio_bytes
            
            # 发送
            await self.ws.send(request.SerializeToString())
            self.stats["audio_chunks_sent"] += 1
            
        except Exception as e:
            print(f"❌ 发送音频错误: {e}")
            self.stats["errors"] += 1
            if self.on_error:
                self.on_error(f"发送音频错误: {e}")
    
    async def receive_loop(self):
        """接收消息循环"""
        if not self.is_connected or not self.ws:
            print("⚠️ 未连接，无法接收消息")
            return
        
        print("开始接收消息循环...")
        
        try:
            while self.is_connected:
                try:
                    # 接收消息
                    response_bytes = await self.ws.recv()
                    response = TranslateResponse()
                    response.ParseFromString(response_bytes)
                    
                    # 处理消息
                    await self._handle_response(response)
                    
                    # 如果会话结束，退出循环
                    if response.event == Type.SessionFinished:
                        print("✅ 会话正常结束")
                        break
                    
                    # 如果会话失败或取消
                    if response.event in [Type.SessionFailed, Type.SessionCanceled]:
                        print(f"❌ 会话异常结束: {response.response_meta.Message}")
                        if self.on_error:
                            self.on_error(f"会话异常: {response.response_meta.Message}")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    print("连接已关闭")
                    break
                except Exception as e:
                    print(f"❌ 接收消息错误: {e}")
                    self.stats["errors"] += 1
                    if self.on_error:
                        self.on_error(f"接收消息错误: {e}")
                    break
        finally:
            self.is_connected = False
            print("接收消息循环结束")
    
    async def _handle_response(self, response: TranslateResponse):
        """处理响应消息"""
        event = response.event
        
        # 源文本（STT结果）
        if event == Type.SourceSubtitleResponse:
            text = response.text
            self.stats["source_text_received"] += 1
            print(f"【原文】 {text}")
            if self.on_source_text:
                self.on_source_text(text, is_final=False)
        
        # 翻译文本
        elif event == Type.TranslationSubtitleResponse:
            text = response.text
            self.stats["translation_text_received"] += 1
            print(f"【译文】 {text}")
            if self.on_translation_text:
                self.on_translation_text(text, is_final=False)
        
        # TTS音频
        elif event == Type.TTSResponse:
            audio_data = None
            
            # === 调试模式：检查TTS响应结构 ===
            if self.debug_mode:
                import sys
                print("\n" + "="*70, file=sys.stderr)
                print("🔍 调试：TTS响应详情", file=sys.stderr)
                print("="*70, file=sys.stderr)
            
            # 尝试1：response.data
            if hasattr(response, 'data') and response.data:
                audio_data = response.data
                if self.debug_mode:
                    print(f"✅ 使用 response.data: {len(audio_data)} 字节", file=sys.stderr)
                    print(f"   前20字节: {audio_data[:20].hex()}", file=sys.stderr)
            
            # 尝试2：response.target_audio.binary_data
            elif hasattr(response, 'target_audio') and hasattr(response.target_audio, 'binary_data'):
                audio_data = response.target_audio.binary_data
                if self.debug_mode:
                    print(f"✅ 使用 response.target_audio.binary_data: {len(audio_data)} 字节", file=sys.stderr)
                    print(f"   前20字节: {audio_data[:20].hex()}", file=sys.stderr)
            
            # 尝试3：response.audio
            elif hasattr(response, 'audio') and response.audio:
                audio_data = response.audio
                if self.debug_mode:
                    print(f"✅ 使用 response.audio: {len(audio_data)} 字节", file=sys.stderr)
                    print(f"   前20字节: {audio_data[:20].hex()}", file=sys.stderr)
            
            else:
                if self.debug_mode:
                    print("❌ 未找到音频数据字段！", file=sys.stderr)
                    print("response对象的字段：", file=sys.stderr)
                    for field_desc in response.DESCRIPTOR.fields:
                        field_name = field_desc.name
                        if hasattr(response, field_name):
                            field_value = getattr(response, field_name)
                            if isinstance(field_value, bytes) and field_value:
                                print(f"  {field_name}: bytes, {len(field_value)} 字节", file=sys.stderr)
                            elif field_value:
                                print(f"  {field_name}: {type(field_value).__name__}", file=sys.stderr)
            
            if self.debug_mode:
                print("="*70 + "\n", file=sys.stderr)
            # === 调试结束 ===
            
            if audio_data:
                self.stats["tts_chunks"] += 1
                if self.on_tts_audio:
                    self.on_tts_audio(audio_data)
        
        # 使用统计
        elif event == Type.UsageResponse:
            print(f"【使用统计】 Sequence: {response.response_meta.Sequence}")
        
        # 会话结束
        elif event == Type.SessionFinished:
            if self.on_session_finished:
                self.on_session_finished()
    
    async def finish_session(self):
        """结束会话"""
        if not self.is_connected or not self.ws:
            return
        
        try:
            # 发送FinishSession请求
            request = TranslateRequest()
            request.request_meta.SessionID = self.session_id
            request.event = Type.FinishSession
            
            await self.ws.send(request.SerializeToString())
            print("✅ 已发送结束会话请求")
            
        except Exception as e:
            print(f"❌ 结束会话错误: {e}")
    
    async def close(self):
        """关闭连接"""
        if self.is_connected:
            await self.finish_session()
            # 等待一小段时间让服务器处理
            await asyncio.sleep(0.5)
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        self.is_connected = False
        print("✅ 连接已关闭")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()


# 测试代码
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app_key = os.getenv("DOUBAO_APP_KEY", "")
    access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
    
    if not app_key or not access_key:
        print("❌ 请在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY")
        exit(1)
    
    async def test():
        # 创建客户端
        client = ASTClientProtobuf(app_key, access_key)
        client.set_config(
            mode="s2s",
            source_language="zh",
            target_language="en"
        )
        
        # 设置回调
        def on_source(text, is_final=False):
            print(f">>> 原文回调: {text}")
        
        def on_translation(text, is_final=False):
            print(f">>> 译文回调: {text}")
        
        def on_tts(audio_bytes):
            print(f">>> TTS音频回调: {len(audio_bytes)} 字节")
        
        client.on_source_text = on_source
        client.on_translation_text = on_translation
        client.on_tts_audio = on_tts
        
        # 连接
        if await client.connect():
            print("\n✅ 连接成功，开始接收消息...")
            
            # 启动接收循环
            receive_task = asyncio.create_task(client.receive_loop())
            
            # 模拟发送音频（实际应该从麦克风采集）
            print("\n发送测试音频...")
            for i in range(5):
                # 生成测试音频（静音）
                test_audio = np.zeros(1280, dtype=np.float32)  # 80ms @ 16kHz
                await client.send_audio(test_audio)
                await asyncio.sleep(0.1)
            
            # 等待几秒钟接收响应
            await asyncio.sleep(5)
            
            # 关闭连接
            await client.close()
            
            # 等待接收任务完成
            await receive_task
            
            # 打印统计
            print(f"\n统计信息: {client.get_stats()}")
        else:
            print("❌ 连接失败")
    
    # 运行测试
    asyncio.run(test())
