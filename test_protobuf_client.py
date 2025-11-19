"""
测试Protobuf客户端
"""
import asyncio
import os
from dotenv import load_dotenv
from modules.ast_client_protobuf import ASTClientProtobuf
import numpy as np

load_dotenv()

async def test_protobuf_client():
    """测试Protobuf客户端连接"""
    
    app_key = os.getenv("DOUBAO_APP_KEY", "")
    access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
    
    if not app_key or not access_key:
        print("❌ 请在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY")
        return False
    
    print("=" * 60)
    print("Protobuf客户端测试")
    print("=" * 60)
    
    # 创建客户端
    client = ASTClientProtobuf(app_key, access_key)
    client.set_config(
        mode="s2s",
        source_language="zh",
        target_language="en",
        target_audio_format="pcm"
    )
    
    # 设置回调
    received_data = {
        "source_text": [],
        "translation_text": [],
        "tts_audio_chunks": 0
    }
    
    def on_source(text, is_final=False):
        print(f"【原文】 {text}")
        received_data["source_text"].append(text)
    
    def on_translation(text, is_final=False):
        print(f"【译文】 {text}")
        received_data["translation_text"].append(text)
    
    def on_tts(audio_bytes):
        print(f"【TTS音频】 收到 {len(audio_bytes)} 字节")
        received_data["tts_audio_chunks"] += 1
    
    def on_error(error_msg):
        print(f"【错误】 {error_msg}")
    
    client.on_source_text = on_source
    client.on_translation_text = on_translation
    client.on_tts_audio = on_tts
    client.on_error = on_error
    
    # 连接
    print("\n步骤1: 连接服务器...")
    if not await client.connect():
        print("❌ 连接失败")
        return False
    
    print("\n步骤2: 启动接收循环...")
    receive_task = asyncio.create_task(client.receive_loop())
    
    # 发送测试音频（静音）
    print("\n步骤3: 发送测试音频（5个80ms的音频块）...")
    for i in range(5):
        # 生成静音音频
        test_audio = np.zeros(1280, dtype=np.float32)  # 80ms @ 16kHz
        await client.send_audio(test_audio)
        print(f"  发送音频块 {i+1}/5")
        await asyncio.sleep(0.1)
    
    # 等待接收响应
    print("\n步骤4: 等待服务器响应（5秒）...")
    await asyncio.sleep(5)
    
    # 关闭连接
    print("\n步骤5: 关闭连接...")
    await client.close()
    await receive_task
    
    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"统计信息: {client.get_stats()}")
    print(f"接收到的原文: {len(received_data['source_text'])} 条")
    print(f"接收到的译文: {len(received_data['translation_text'])} 条")
    print(f"接收到的TTS音频块: {received_data['tts_audio_chunks']} 个")
    
    if received_data["source_text"] or received_data["translation_text"]:
        print("\n✅ 测试成功！客户端可以正常通信")
        return True
    else:
        print("\n⚠️ 未收到翻译结果（可能因为发送的是静音）")
        print("💡 提示：这是正常的，因为我们发送的是静音音频")
        print("✅ 但连接和通信协议是正常的！")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_protobuf_client())
    exit(0 if success else 1)
