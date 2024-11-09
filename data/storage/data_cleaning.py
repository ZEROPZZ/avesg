class DataCleaning:
    def clean_pdf_text(self, text):
        """清理PDF提取的文本"""
        # 移除多余的空格和换行
        text = ' '.join(text.split())
        return text 
