"""
调试TTS原始数据
检查从服务器收到的TTS响应包含什么
"""

# 在 ast_client_protobuf.py 的 _handle_response 方法中
# 第295-300行，添加调试代码：

"""
# TTS音频
elif event == Type.TTSResponse:
    # === 添加调试 ===
    print("\n" + "="*70)
    print("🔍 调试：TTS响应详情")
    print("="*70)
    
    # 打印response的所有字段
    print(f"Response对象类型: {type(response)}")
    print(f"Event类型: {event}")
    
    # 尝试不同的字段名
    print("\n检查可能的音频字段：")
    
    # 方式1：response.data
    if hasattr(response, 'data'):
        print(f"  response.data: 存在, 长度={len(response.data)} 字节")
        print(f"    前20字节: {response.data[:20]}")
    else:
        print(f"  response.data: 不存在 ❌")
    
    # 方式2：response.audio_data
    if hasattr(response, 'audio_data'):
        print(f"  response.audio_data: 存在, 长度={len(response.audio_data)} 字节")
        print(f"    前20字节: {response.audio_data[:20]}")
    else:
        print(f"  response.audio_data: 不存在 ❌")
    
    # 方式3：response.target_audio
    if hasattr(response, 'target_audio'):
        print(f"  response.target_audio: 存在")
        if hasattr(response.target_audio, 'binary_data'):
            print(f"    target_audio.binary_data: 长度={len(response.target_audio.binary_data)} 字节")
            print(f"    前20字节: {response.target_audio.binary_data[:20]}")
    else:
        print(f"  response.target_audio: 不存在 ❌")
    
    # 方式4：列出所有字段
    print("\nresponse对象的所有字段：")
    for field in dir(response):
        if not field.startswith('_'):
            try:
                value = getattr(response, field)
                if not callable(value):
                    if isinstance(value, bytes):
                        print(f"  {field}: bytes, 长度={len(value)}")
                    else:
                        print(f"  {field}: {type(value).__name__}")
            except:
                pass
    
    print("="*70 + "\n")
    # === 调试结束 ===
    
    audio_data = response.data
    if audio_data:
        self.stats["tts_chunks"] += 1
        if self.on_tts_audio:
            self.on_tts_audio(audio_data)
"""

print(__doc__)
print("\n请将上面的代码添加到 modules/ast_client_protobuf.py 的第295行位置")
print("然后重新运行程序，观察TTS响应的详细信息")
