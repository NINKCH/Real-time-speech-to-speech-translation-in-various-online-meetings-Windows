# 快速开始指南

## 5分钟上手

### 步骤1: 安装依赖

```bash
conda activate rttdb
pip install -r requirements.txt
```

### 步骤2: 安装VB-Cable

1. 下载: https://vb-audio.com/Cable/
2. 以管理员身份安装
3. 重启电脑

### 步骤3: 配置API密钥

1. 访问 https://console.volcengine.com/
2. 开通"同声传译"服务
3. 复制 App Key 和 Access Key
4. 启动程序后点击"设置"填入密钥

或创建 `.env` 文件:
```
DOUBAO_APP_KEY=你的App_Key
DOUBAO_ACCESS_KEY=你的Access_Key
```

### 步骤4: 启动程序

```bash
python main.py
```

### 步骤5: 开始翻译

1. 选择翻译方向: 中文 → 英语
2. 选择模式: s2s (语音到语音)
3. 点击 **"开始翻译"**
4. 对着麦克风说话

### 步骤6: 在会议中使用

会议软件麦克风选择 **"CABLE Output (VB-Audio Virtual Cable)"**

## 配置要点

### 三层配置原则

1. **Windows输入**: 保持真实麦克风（不要选CABLE Output）
2. **程序**: 自动采集真实麦克风，输出到CABLE Input
3. **会议软件**: 麦克风选择 CABLE Output

### 音频流向

```
[真实麦克风] → [程序翻译] → [CABLE Input] → [VB-Cable] → [CABLE Output] → [会议软件]
```

## 功能说明

### S2S模式（语音到语音）

- 自动启用零样本声音复刻
- 用你的声音说出翻译结果
- 适用于会议、通话等场景

### S2T模式（语音到文本）

- 仅输出文本
- 不生成语音
- 适用于字幕等场景

## 验证声音复刻

1. 点击 **"验证复刻"** 按钮
2. 点击 **"开始测试"**
3. 朗读测试文本
4. 点击 **"播放复刻音频"** 听取效果

## 检查清单

- [ ] Python 3.12.7 已安装
- [ ] 依赖已安装 (websockets, PyQt6, sounddevice)
- [ ] VB-Cable 已安装
- [ ] API密钥已配置
- [ ] 程序能正常启动
- [ ] 翻译测试成功

## 遇到问题？

查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 故障排除指南

## 更多信息

- [README.md](README.md) - 完整项目说明
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目技术总结
