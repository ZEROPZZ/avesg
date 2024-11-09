import pyttsx3 # type: ignore
import os
from typing import Optional

class SpeechSynthesizer:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voice_speed = 150
        self.voice_volume = 1.0
        
    def configure_voice(self, speed: Optional[int] = None, volume: Optional[float] = None):
        """配置语音参数"""
        if speed is not None:
            self.voice_speed = speed
            self.engine.setProperty('rate', speed)
        if volume is not None:
            self.voice_volume = volume
            self.engine.setProperty('volume', volume)
            
    def text_to_speech(self, text: str) -> None:
        """将文本转换为语音"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"语音合成错误: {str(e)}")
            
    def save_to_file(self, text: str, output_path: str) -> bool:
        """将文本转换为语音文件"""
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return os.path.exists(output_path)
        except Exception as e:
            print(f"保存语音文件错误: {str(e)}")
            return False

