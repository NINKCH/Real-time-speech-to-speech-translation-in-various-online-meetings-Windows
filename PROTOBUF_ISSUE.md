# Protobuf格式问题说明

## 问题现状

豆包同声传译 2.0 API使用 **Protobuf二进制格式**，当前项目使用JSON格式无法正常通信。

### 错误信息
```
收到响应类型: <class 'bytes'>
响应前20字节: b'\nX\x18\xc0\xf7\x9c\x1a"Qunmarshal p'
```

说明：
- 服务器返回Protobuf二进制数据
- "Unmarshal" 错误表明服务器无法解析我们发送的JSON

## 解决方案

### 方案1: 使用官方SDK（强烈推荐）⭐⭐⭐

火山引擎应该提供了官方Python SDK：

```bash
# 尝试安装
pip install volcengine-python-sdk
pip install volcenginesdkarkruntime
pip install volc-sdk-python
```

然后查找官方示例代码：
- 访问：https://console.volcengine.com/
- 进入"同声传译"服务
- 查找"SDK下载"或"示例代码"

### 方案2: 联系技术支持

1. 登录火山引擎控制台
2. 提交工单询问："同声传译2.0 API的Python WebSocket示例代码"
3. 说明需要：
   - Protobuf格式的消息构造方法
   - 完整的Python SDK或示例代码
   - .proto文件和使用说明

### 方案3: 手动编译Protobuf

如果拿到了完整的.proto文件：

```bash
# 1. 安装protobuf编译器
pip install protobuf grpcio-tools

# 2. 编译proto文件
python -m grpc_tools.protoc -I./protos --python_out=./protos ./protos/ast_service.proto

# 3. 使用生成的Python代码
from protos import ast_service_pb2

# 4. 序列化消息
message = ast_service_pb2.StartSessionRequest()
message.session_id = "xxx"
binary_data = message.SerializeToString()

# 5. 反序列化响应
response = ast_service_pb2.Response()
response.ParseFromString(binary_data)
```

### 方案4: 使用其他API（备用方案）

如果WebSocket太复杂，考虑：

1. **分模块使用**：
   - STT: 使用语音识别API（可能支持HTTP+JSON）
   - 翻译: 使用翻译API  
   - TTS: 使用语音合成API

2. **其他服务商**：
   - Azure Speech Services（有完整Python SDK）
   - Google Cloud Speech-to-Speech
   - AWS Transcribe + Translate + Polly

## 当前项目状态

### 已完成
✅ 项目结构创建
✅ 音频采集模块（完整可用）
✅ 虚拟音频输出模块（完整可用）
✅ GUI界面（完整可用）
✅ WebSocket连接（可以连接，但无法通信）

### 待完成
❌ Protobuf消息序列化/反序列化
❌ 正确的API通信协议

## 建议的下一步

### 立即行动
1. **联系火山引擎技术支持**获取官方SDK或示例代码
2. 或在控制台查找"SDK下载"区域
3. 查看是否有Java/Go SDK，参考其实现逻辑

### 临时方案
如果急需功能，可以：
1. 使用分模块的HTTP API（虽然延迟会高2-3秒）
2. 参考之前的 `RealTimeTranslator` 项目（使用HTTP API）
3. 等待获取官方SDK后再切换到WebSocket版本

## 参考资料

- 火山引擎控制台：https://console.volcengine.com/
- 火山翻译：https://translate.volcengine.com/
- Protobuf官方文档：https://protobuf.dev/
- Python Protobuf指南：https://protobuf.dev/getting-started/pythontutorial/

## 技术细节

### Protobuf Wire Format
当前服务器返回的数据：`b'\nX\x18\xc0\xf7\x9c\x1a"Qunmarshal p'`

解析：
- `\n` = 字段标记（field number）
- `X` = 长度
- 后续是实际数据

这需要完整的.proto文件定义才能正确解析。

## 结论

**当前项目代码质量很高，但受限于API协议**。建议：

1. **最优解**：获取官方SDK或完整proto文件
2. **次优解**：使用HTTP API实现相同功能
3. **学习解**：手动实现Protobuf协议（耗时且容易出错）

等您获取到官方SDK或proto文件后，只需要替换 `modules/ast_client.py` 中的消息序列化部分即可。

其他模块（音频采集、虚拟输出、GUI）都是完整可用的！
