# 快速开始指南

## 🚀 5分钟上手

### 步骤1: 安装依赖（1分钟）

```bash
# 激活conda环境
conda activate rttdb

# 安装Python依赖
pip install -r requirements.txt
```

### 步骤2: 安装VB-Cable（2分钟）

1. 下载: https://vb-audio.com/Cable/
2. 双击安装（需要管理员权限）
3. 重启电脑

### 步骤3: 配置API密钥（1分钟）

1. 访问 https://console.volcengine.com/
2. 开通"同声传译"服务
3. 复制 App Key 和 Access Key
4. 创建 `.env` 文件:

```
DOUBAO_APP_KEY=你的App_Key
DOUBAO_ACCESS_KEY=你的Access_Key
DOUBAO_RESOURCE_ID=volc.service_type.10053
```

### 步骤4: 启动程序（1分钟）

```bash
python main.py
```

### 步骤5: 开始翻译

1. 选择翻译方向: 中文 → 英语
2. 选择模式: s2s (语音到语音)
3. 点击 **"▶ 开始翻译"**
4. 对着麦克风说话，即可看到翻译结果！

### 步骤6: 验证声音复刻（可选）

想验证零样本声音复刻是否真的复刻出了您的声音？

1. 点击 **"🔬 验证复刻"** 按钮（橙色）
2. 点击 **"🚀 开始测试"**
3. 朗读显示的测试文本（约10秒）
4. 点击 **"▶️ 播放复刻音频"** 听取效果
5. 如需保存样本，点击 **"💾 保存样本"**

详细说明请查看：`VOICE_CLONE_VERIFICATION_GUIDE.md`

## 🎤 在会议中使用

### Zoom配置

1. 打开Zoom
2. Settings → Audio
3. Microphone: 选择 **"CABLE Output (VB-Audio Virtual Cable)"**
4. 测试麦克风，确认能听到翻译语音
5. 开始会议 🎉

### Teams配置

1. 打开Teams
2. Settings → Devices
3. Microphone: 选择 **"CABLE Output"**

### Google Meet配置

1. 进入会议
2. 点击设置（齿轮图标）
3. 音频 → 麦克风: 选择 **"CABLE Output"**

## ✅ 测试检查清单

- [ ] Python环境: `python --version` 显示 3.12.7
- [ ] 依赖安装: `pip list` 显示 websockets, PyQt6, sounddevice
- [ ] VB-Cable: 系统声音设置中能看到 CABLE Input/Output
- [ ] API密钥: `.env` 文件已配置
- [ ] 程序启动: `python main.py` 能打开GUI
- [ ] 翻译测试: 点击开始，说话后能看到翻译
- [ ] 虚拟音频: 状态栏显示"运行中"

## 🐛 遇到问题？

### 问题1: 找不到CABLE设备
```bash
# 检查VB-Cable是否安装
# Windows声音设置 → 输入/输出设备列表中查找
```

### 问题2: API连接失败
```bash
# 检查.env文件
cat .env  # Linux/Mac
type .env  # Windows

# 确认密钥格式正确，无多余空格
```

### 问题3: 没有声音
```bash
# 测试虚拟音频
python modules/virtual_audio.py

# 应该能听到440Hz测试音
```

## 📚 更多帮助

- 完整文档: [README.md](README.md)
- 常见问题: README.md 的"常见问题"章节
- 日志文件: `logs/translator.log`

---

**准备好了吗？开始你的实时翻译之旅！** 🚀
