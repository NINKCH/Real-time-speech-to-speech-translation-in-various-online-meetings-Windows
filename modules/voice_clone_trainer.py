"""
声音复刻训练模块
用于上传音频训练声音复刻模型
"""
import os
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Callable
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceCloneTrainer:
    """声音复刻训练器"""
    
    # 模型类型
    MODEL_TYPE_MEGA = 0  # 不推荐
    MODEL_TYPE_ICL_1_0 = 1  # ICL 1.0
    MODEL_TYPE_DIT_STANDARD = 2  # DiT标准版
    MODEL_TYPE_DIT_RESTORE = 3  # DiT还原版
    MODEL_TYPE_ICL_2_0 = 4  # ICL 2.0 (推荐)
    
    # 语种
    LANGUAGE_CN = 0  # 中文
    LANGUAGE_EN = 1  # 英文
    LANGUAGE_JA = 2  # 日语
    LANGUAGE_ES = 3  # 西班牙语
    LANGUAGE_ID = 4  # 印尼语
    LANGUAGE_PT = 5  # 葡萄牙语
    LANGUAGE_DE = 6  # 德语 (仅model_type=2)
    LANGUAGE_FR = 7  # 法语 (仅model_type=2)
    
    def __init__(self, app_key: str, access_token: str):
        """
        初始化训练器
        
        Args:
            app_key: AppID
            access_token: Access Token
        """
        self.app_key = app_key
        self.access_token = access_token
        self.base_url = "https://openspeech.bytedance.com"
        
        # 回调函数
        self.on_progress: Optional[Callable] = None
        self.on_success: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    def upload_and_train(
        self,
        speaker_id: str,
        audio_file_path: str,
        model_type: int = MODEL_TYPE_ICL_2_0,
        language: int = LANGUAGE_CN,
        text: Optional[str] = None,
        enable_denoise: bool = False,
        resource_id: str = "seed-icl-2.0"
    ) -> dict:
        """
        上传音频并训练声音复刻模型
        
        Args:
            speaker_id: 唯一音色代号 (从控制台获取，格式：S_xxxx)
            audio_file_path: 音频文件路径 (wav/mp3/ogg/m4a/aac/pcm)
            model_type: 模型类型 (0-4)
            language: 语种 (0-7)
            text: 录音文本（可选，用于验证）
            enable_denoise: 是否开启降噪
            resource_id: 资源ID
                - seed-icl-1.0: 声音复刻1.0
                - seed-icl-2.0: 声音复刻2.0
        
        Returns:
            响应字典
        """
        try:
            logger.info(f"开始上传音频训练: {speaker_id}")
            if self.on_progress:
                self.on_progress("正在读取音频文件...")
            
            # 读取音频文件
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
            
            # 检查文件大小（限制10MB）
            file_size = audio_path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                raise ValueError(f"音频文件过大: {file_size / 1024 / 1024:.2f}MB，最大支持10MB")
            
            # 读取并编码音频
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # 获取音频格式
            audio_format = audio_path.suffix.lstrip('.')
            if audio_format not in ['wav', 'mp3', 'ogg', 'm4a', 'aac', 'pcm']:
                raise ValueError(f"不支持的音频格式: {audio_format}")
            
            logger.info(f"音频文件: {audio_path.name}, 大小: {file_size / 1024:.2f}KB, 格式: {audio_format}")
            
            if self.on_progress:
                self.on_progress("正在上传到服务器...")
            
            # 构建请求
            url = f"{self.base_url}/api/v1/mega_tts/audio/upload"
            headers = {
                "Authorization": f"Bearer;{self.access_token}",
                "Resource-Id": resource_id,
                "Content-Type": "application/json"
            }
            
            # 构建额外参数
            extra_params = {
                "enable_audio_denoise": enable_denoise
            }
            
            # 构建请求体
            data = {
                "appid": self.app_key,
                "speaker_id": speaker_id,
                "audios": [{
                    "audio_bytes": audio_base64,
                    "audio_format": audio_format
                }],
                "source": 2,  # 固定值
                "language": language,
                "model_type": model_type,
                "extra_params": json.dumps(extra_params)
            }
            
            # 如果提供了文本，添加到请求中
            if text:
                data["audios"][0]["text"] = text
            
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查响应
            if result.get("BaseResp", {}).get("StatusCode") == 0:
                logger.info(f"训练请求提交成功: {speaker_id}")
                if self.on_success:
                    self.on_success(f"训练已开始，Speaker ID: {speaker_id}")
                if self.on_progress:
                    self.on_progress("训练已开始，请等待...")
                return result
            else:
                error_msg = result.get("BaseResp", {}).get("StatusMessage", "未知错误")
                logger.error(f"训练请求失败: {error_msg}")
                if self.on_error:
                    self.on_error(error_msg)
                raise Exception(f"训练失败: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}", exc_info=True)
            if self.on_error:
                self.on_error(f"网络错误: {e}")
            raise
        except Exception as e:
            logger.error(f"训练失败: {e}", exc_info=True)
            if self.on_error:
                self.on_error(str(e))
            raise
    
    def check_status(
        self,
        speaker_id: str,
        resource_id: str = "seed-icl-2.0"
    ) -> dict:
        """
        查询训练状态
        
        Args:
            speaker_id: 音色ID
            resource_id: 资源ID
        
        Returns:
            状态信息字典
        """
        try:
            url = f"{self.base_url}/api/v1/mega_tts/status"
            headers = {
                "Authorization": f"Bearer;{self.access_token}",
                "Resource-Id": resource_id,
                "Content-Type": "application/json"
            }
            
            data = {
                "appid": self.app_key,
                "speaker_id": speaker_id
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("BaseResp", {}).get("StatusCode") == 0:
                status = result.get("status")
                status_text = {
                    0: "未找到",
                    1: "训练中",
                    2: "成功",
                    3: "失败",
                    4: "已激活"
                }.get(status, "未知状态")
                
                logger.info(f"Speaker ID {speaker_id} 状态: {status_text}")
                
                # 如果训练成功，返回demo音频
                if status == 2 or status == 4:
                    demo_audio = result.get("demo_audio", "")
                    if demo_audio:
                        logger.info(f"Demo音频: {demo_audio}")
                
                return result
            else:
                error_msg = result.get("BaseResp", {}).get("StatusMessage", "未知错误")
                logger.error(f"查询状态失败: {error_msg}")
                raise Exception(f"查询失败: {error_msg}")
                
        except Exception as e:
            logger.error(f"查询状态失败: {e}", exc_info=True)
            raise
    
    def get_status_text(self, status_code: int) -> str:
        """获取状态文本"""
        status_map = {
            0: "未找到 - 音色尚未训练",
            1: "训练中 - 请稍候...",
            2: "成功 - 可以使用",
            3: "失败 - 训练失败",
            4: "已激活 - 可以使用"
        }
        return status_map.get(status_code, "未知状态")


# 测试代码
if __name__ == "__main__":
    # 测试配置
    from dotenv import load_dotenv
    load_dotenv()
    
    app_key = os.getenv("DOUBAO_APP_KEY", "")
    access_token = os.getenv("DOUBAO_ACCESS_KEY", "")
    
    if not app_key or not access_token:
        print("❌ 请在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY")
        exit(1)
    
    # 创建训练器
    trainer = VoiceCloneTrainer(app_key, access_token)
    
    # 设置回调
    trainer.on_progress = lambda msg: print(f"📝 {msg}")
    trainer.on_success = lambda msg: print(f"✅ {msg}")
    trainer.on_error = lambda msg: print(f"❌ {msg}")
    
    print("\n声音复刻训练器测试")
    print("=" * 60)
    print("注意：实际训练需要:")
    print("1. 从控制台获取 Speaker ID (格式: S_xxxx)")
    print("2. 准备音频文件 (建议20秒以上，清晰无噪音)")
    print("3. 等待训练完成 (通常几分钟)")
    print("=" * 60)
