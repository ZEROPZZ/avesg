import numpy as np # type: ignore
from transformers import AutoTokenizer, AutoModel, pipeline # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import torch # type: ignore
import jieba # type: ignore
from typing import List, Dict, Any, Tuple

class NaturalLanguageUnderstanding:
    def __init__(self):
        # 加载预训练模型和分词器
        self.model_name = "bert-base-chinese"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # 情感分析pipeline
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                         model="uer/roberta-base-finetuned-jd-binary-chinese")
        
        # 问答系统
        self.qa_pipeline = pipeline("question-answering", 
                                  model="uer/roberta-base-chinese-extractive-qa")
        
        self.context_history = []
        self.embedding_cache = {}
        
    def process_text(self, text: str) -> Dict[str, Any]:
        """深度处理输入文本"""
        # 分词
        tokens = list(jieba.cut(text))
        
        # 获取BERT编码
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        # 情感分析
        sentiment = self.sentiment_analyzer(text)[0]
        
        return {
            'tokens': tokens,
            'embeddings': embeddings.numpy(),
            'sentiment': sentiment,
            'original_text': text
        }
        
    def get_response(self, input_text: str, context: str = "") -> Dict[str, Any]:
        """生成智能响应"""
        processed = self.process_text(input_text)
        self.context_history.append(processed)
        
        # 如果有上下文，进行问答
        if context:
            qa_result = self.qa_pipeline({
                'question': input_text,
                'context': context
            })
        else:
            qa_result = None
            
        response = {
            'processed_input': processed,
            'qa_result': qa_result,
            'sentiment': processed['sentiment'],
            'context_size': len(self.context_history)
        }
        
        return response
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return float(cosine_similarity(emb1, emb2)[0][0])
        
    def get_embedding(self, text: str) -> np.ndarray:
        """获取文本的嵌入表示"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).numpy()
            
        self.embedding_cache[text] = embedding
        return embedding
        
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
        words = jieba.analyse.extract_tags(text, topK=top_k)
        return words
        
    def get_intent(self, text: str) -> str:
        """简单的意图识别"""
        keywords = set(self.extract_keywords(text))
        
        # 定义一些基本意图
        intents = {
            'query': {'什么', '怎么', '为什么', '如何', '谁'},
            'command': {'执行', '运行', '开始', '停止', '暂停'},
            'greeting': {'你好', '早上好', '晚上好', '嗨'},
            'farewell': {'再见', '拜拜', '回头见'}
        }
        
        for intent, intent_keywords in intents.items():
            if keywords & intent_keywords:
                return intent
        return 'unknown'

    def clear_context(self) -> None:
        """清除上下文历史"""
        self.context_history = []
        self.embedding_cache = {}

if __name__ == "__main__":
    nlu = NaturalLanguageUnderstanding()
    
    # 测试文本处理
    test_text = "今天天气真不错，我很开心！"
    response = nlu.get_response(test_text)
    print(f"处理结果: {response}")
    
    # 测试问答
    context = "深度学习是人工智能的一个分支，它使用多层神经网络来学习数据的表示。"
    question = "什么是深度学习？"
    qa_response = nlu.get_response(question, context)
    print(f"问答结果: {qa_response}") 