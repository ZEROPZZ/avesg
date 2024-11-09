import os
import pyttsx3 # type: ignore
import PyPDF2 # type: ignore
import speech_recognition as sr

class PDFVoiceReader:
    def __init__(self):
        # 初始化语音引擎
        self.engine = pyttsx3.init()
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        # 当前PDF文档
        self.pdf_document = None
        # 当前页码
        self.current_page = 0
        # PDF文件路径
        self.pdf_path = None
        # 语音命令映射
        self.commands = {
            "开始阅读": self.start_reading,
            "停止阅读": self.stop_reading,
            "下一页": self.next_page,
            "上一页": self.previous_page,
            "跳转到": self.jump_to_page
        }

    def load_pdf(self, pdf_path):
        """加载PDF文件"""
        try:
            if os.path.exists(pdf_path):
                self.pdf_path = pdf_path
                self.pdf_document = PyPDF2.PdfReader(open(pdf_path, 'rb'))
                self.current_page = 0
                print(f"PDF文件加载成功，共{len(self.pdf_document.pages)}页")
                return True
            else:
                print("PDF文件不存在")
                return False
        except Exception as e:
            print(f"加载PDF文件时出错: {str(e)}")
            return False

    def read_current_page(self):
        """读取当前页面内容"""
        if self.pdf_document and self.current_page < len(self.pdf_document.pages):
            try:
                page = self.pdf_document.pages[self.current_page]
                text = page.extract_text()
                return text
            except Exception as e:
                print(f"读取页面时出错: {str(e)}")
                return None
        return None

    def start_reading(self):
        """开始阅读当前页面"""
        text = self.read_current_page()
        if text:
            print(f"正在阅读第{self.current_page + 1}页")
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print("无法读取当前页面")

    def stop_reading(self):
        """停止阅读"""
        self.engine.stop()
        print("已停止阅读")

    def next_page(self):
        """下一页"""
        if self.pdf_document and self.current_page < len(self.pdf_document.pages) - 1:
            self.current_page += 1
            print(f"已切换到第{self.current_page + 1}页")
            self.start_reading()
        else:
            print("已经是最后一页")

    def previous_page(self):
        """上一页"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            print(f"已切换到第{self.current_page + 1}页")
            self.start_reading()
        else:
            print("已经是第一页")

    def jump_to_page(self, page_number):
        """跳转到指定页面"""
        if self.pdf_document:
            page_number = int(page_number) - 1
            if 0 <= page_number < len(self.pdf_document.pages):
                self.current_page = page_number
                print(f"已跳转到第{page_number + 1}页")
                self.start_reading()
            else:
                print("页码超出范围")

    def listen_command(self):
        """监听语音命令"""
        with sr.Microphone() as source:
            print("请说出命令...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio, language='zh-CN')
                print(f"识别到命令: {command}")
                self.process_command(command)
            except sr.WaitTimeoutError:
                print("未检测到语音输入")
            except sr.UnknownValueError:
                print("无法识别语音命令")
            except sr.RequestError as e:
                print(f"语音识别服务出错: {str(e)}")

    def process_command(self, command):
        """处理语音命令"""
        for cmd, func in self.commands.items():
            if cmd in command:
                if cmd == "跳转到":
                    # 提取页码数字
                    try:
                        page_number = int(''.join(filter(str.isdigit, command)))
                        func(page_number)
                    except ValueError:
                        print("无法识别页码")
                else:
                    func()
                return
        print("未知命令")

    def run(self):
        """运行PDF语音阅读器"""
        print("欢迎使用PDF语音阅读器")
        while True:
            print("\n请选择操作：")
            print("1. 加载PDF文件")
            print("2. 开始语音控制")
            print("3. 退出")
            
            choice = input("请输入选项编号：")
            
            if choice == "1":
                pdf_path = input("请输入PDF文件路径：")
                self.load_pdf(pdf_path)
            elif choice == "2":
                if self.pdf_document:
                    print("开始语音控制模式")
                    print("可用命令：开始阅读、停止阅读、下一页、上一页、跳转到X页")
                    while True:
                        self.listen_command()
                else:
                    print("请先加载PDF文件")
            elif choice == "3":
                print("感谢使用，再见！")
                break
            else:
                print("无效的选项")

if __name__ == "__main__":
    reader = PDFVoiceReader()
    reader.run()