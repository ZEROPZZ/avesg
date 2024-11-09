from speech.speech_synthesis import SpeechSynthesizer
import speech_recognition as sr
from typing import Optional, Dict, Any

class VoiceProcessor:
    def __init__(self):
        self.synthesizer = SpeechSynthesizer()
        self.recognizer = sr.Recognizer()
        self.commands: Dict[str, Any] = {
            "开始阅读": self.start_reading,
            "停止阅读": self.stop_reading,
            "暂停": self.pause_reading,
            "继续": self.resume_reading
        }
        
    def start_reading(self, text: str) -> None:
        """开始阅读文本"""
        self.synthesizer.text_to_speech(text)
        
    def stop_reading(self) -> None:
        """停止阅读"""
        self.synthesizer.engine.stop()
        
    def pause_reading(self) -> None:
        """暂停阅读"""
        self.synthesizer.engine.pause()
        
    def resume_reading(self) -> None:
        """继续阅读"""
        self.synthesizer.engine.resume()
        
    def process_voice_command(self) -> Optional[str]:
        """处理语音命令"""
        try:
            with sr.Microphone() as source:
                print("请说出命令...")
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio, language='zh-CN')
                return command
        except sr.WaitTimeoutError:
            print("未检测到语音输入")
        except sr.UnknownValueError:
            print("无法识别语音命令")
        except sr.RequestError as e:
            print(f"语音识别服务错误: {str(e)}")
        return None 