import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import speech_recognition as sr
from gtts import gTTS # type: ignore
import pygame  # type: ignore
import os
import numpy as np # type: ignore
from typing import Optional, Dict, Any
import sounddevice as sd # type: ignore
import wave
import tempfile

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.sample_rate = 16000
        pygame.mixer.init()
        
        # 调整识别器的参数
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
    def start_listening(self) -> str:
        """开始监听并返回识别的文本"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                return text
        except sr.UnknownValueError:
            return "无法识别语音"
        except sr.RequestError as e:
            return f"语音识别服务错误: {e}"
            
    def text_to_speech(self, text: str, lang='zh-CN') -> bool:
        """将文本转换为语音并播放"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                
            # 转换文本为语音
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_filename)
            
            # 播放语音
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # 删除临时文件
            os.remove(temp_filename)
            return True
        except Exception as e:
            print(f"语音合成错误: {e}")
            return False
            
    def record_audio(self, duration: int = 5) -> np.ndarray:
        """录制音频"""
        print(f"Recording for {duration} seconds...")
        audio_data = sd.rec(int(duration * self.sample_rate),
                          samplerate=self.sample_rate,
                          channels=1)
        sd.wait()
        return audio_data
        
    def save_audio(self, audio_data: np.ndarray, filename: str):
        """保存音频到文件"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
            
    def get_audio_devices(self) -> Dict[str, Any]:
        """获取可用的音频设备"""
        return {
            'input_devices': sr.Microphone.list_microphone_names(),
            'default_device': self.microphone.device_index
        }

if __name__ == "__main__":
    # 只在直接运行此文件时执行测试
    print("=== 语音接口测试模式 ===")
    voice = VoiceInterface()
    print("请说话...")
    text = voice.start_listening()
    print(f"识别结果: {text}")
    voice.text_to_speech("语音接口测试成功")
        