from typing import Dict, List, Optional
from .nlu_core import NLUCore, NLUResult
import re
import jieba # type: ignore
import numpy as np # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore

class NLPProcessor:
    def __init__(self):
        self.nlu_core = NLUCore()
        self.tfidf_vectorizer = TfidfVectorizer()
        self.word_vectors = {}  # 词向量存储
        
        # 加载停用词
        self.stop_words = self._load_stop_words()
        
    def _load_stop_words(self) -> set:
        """加载停用词"""
        try:
            with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f)
        except Exception as e:
            print(f"Failed to load stop words: {str(e)}")
            return set()

    def process_text(self, text: str) -> Dict:
        """处理文本"""
        # 预处理
        cleaned_text = self._preprocess_text(text)
        
        # NLU处理
        nlu_result = self.nlu_core.process_text(cleaned_text)
        
        # 分词和词性标注
        tokens = self._tokenize(cleaned_text)
        
        # 关键词提取
        keywords = self._extract_keywords(cleaned_text)
        
        # 文本向量化
        text_vector = self._vectorize_text(cleaned_text)
        
        return {
            'original_text': text,
            'cleaned_text': cleaned_text,
            'nlu_result': nlu_result,
            'tokens': tokens,
            'keywords': keywords,
            'text_vector': text_vector
        }

    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 去除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 去除多余空白
        text = ' '.join(text.split())
        
        return text

    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 使用结巴分词
        tokens = jieba.cut(text)
        
        # 去除停用词
        tokens = [token for token in tokens if token not in self.stop_words]
        
        return tokens

    def _extract_keywords(self, text: str) -> List[Dict]:
        """提取关键词"""
        try:
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=10, withWeight=True)
            
            return [{'word': word, 'weight': weight} for word, weight in keywords]
            
        except Exception as e:
            print(f"Keyword extraction failed: {str(e)}")
            return []

    def _vectorize_text(self, text: str) -> np.ndarray:
        """文本向量化"""
        try:
            # 使用TF-IDF向量化
            vector = self.tfidf_vectorizer.fit_transform([text])
            return vector.toarray()[0]
            
        except Exception as e:
            print(f"Text vectorization failed: {str(e)}")
            return np.zeros(100)  # 返回零向量作为默认值

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        try:
            vec1 = self._vectorize_text(text1)
            vec2 = self._vectorize_text(text2)
            
            # 计算余弦相似度
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            return float(similarity)
            
        except Exception as e:
            print(f"Similarity calculation failed: {str(e)}")
            return 0.0

    def extract_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """提取文本模式"""
        matches = []
        for pattern in patterns:
            try:
                found = re.findall(pattern, text)
                matches.extend(found)
            except Exception as e:
                print(f"Pattern matching failed: {str(e)}")
        
        return matches

    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """生成文本摘要"""
        try:
            # 使用TextRank算法生成摘要
            summary = textrank.summarize(text, max_length) # type: ignore
            return summary
            
        except Exception as e:
            print(f"Summary generation failed: {str(e)}")
            return text[:max_length] + "..." 