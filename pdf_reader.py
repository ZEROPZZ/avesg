import pdfplumber # type: ignore
import logging
from typing import List, Optional
from pathlib import Path

class PDFReader:
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def read_pdf(self, file_path: str) -> Optional[List[str]]:
        """
        读取PDF文件内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            List[str]: PDF中的文本内容列表，每个元素为一页内容
            如果读取失败返回 None
        """
        try:
            if not Path(file_path).exists():
                logging.error(f"PDF文件不存在: {file_path}")
                return None
                
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text.strip())
            
            if not text_content:
                logging.warning(f"PDF文件 {file_path} 没有可提取的文本内容")
                return None
                
            logging.info(f"成功读取PDF文件: {file_path}")
            return text_content
            
        except Exception as e:
            logging.error(f"读取PDF文件时发生错误: {str(e)}")
            return None
    
    def extract_text_from_page(self, file_path: str, page_number: int) -> Optional[str]:
        """
        提取PDF特定页面的文本
        
        Args:
            file_path: PDF文件路径
            page_number: 页码（从0开始）
            
        Returns:
            str: 页面文本内容
            如果提取失败返回 None
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_number >= len(pdf.pages):
                    logging.error(f"页码 {page_number} 超出PDF页数范围")
                    return None
                    
                page = pdf.pages[page_number]
                text = page.extract_text()
                
                if not text:
                    logging.warning(f"页面 {page_number} 没有可提取的文本内容")
                    return None
                    
                return text.strip()
                
        except Exception as e:
            logging.error(f"提取页面文本时发生错误: {str(e)}")
            return None

if __name__ == "__main__":
    # 测试代码
    reader = PDFReader()
    
    # 测试读取整个PDF
    test_pdf = "test.pdf"  # 替换为实际的PDF文件路径
    content = reader.read_pdf(test_pdf)
    if content:
        print(f"PDF总页数: {len(content)}")
        print("第一页内容预览:", content[0][:200])
    
    # 测试读取特定页面
    page_text = reader.extract_text_from_page(test_pdf, 0)
    if page_text:
        print("第一页内容:", page_text[:200]) 