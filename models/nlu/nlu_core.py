import spacy # type: ignore
import nltk # type: ignore
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification # type: ignore
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    QUERY = "query"
    COMMAND = "command"
    STATEMENT = "statement"
    QUESTION = "question"
    UNKNOWN = "unknown"

@dataclass
class NLUResult:
    text: str
    intent: IntentType
    entities: List[Dict]
    sentiment: float
    confidence: float
    parsed_result: Dict

class NLUCore:
    def __init__(self):
        self.logger = self._setup_logger()
        
        # 加载模型和工具
        self.nlp = spacy.load("zh_core_web_sm")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                         model="uer/roberta-base-finetuned-jd-binary-chinese")
        
        # 加载意图分类器
        self.intent_classifier = self._load_intent_classifier()
        
        # 加载实体识别器
        self.ner_model = self._load_ner_model()
        
        # 加载配置
        self.config = self._load_config()

    def _setup_logger(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('nlu_core')
        logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler('logs/nlu.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open('config/nlu_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            return {}

    def _load_intent_classifier(self):
        """加载意图分类器"""
        try:
            model_name = "uer/roberta-base-chinese-cluener2020"
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            return pipeline("text-classification", model=model, tokenizer=tokenizer)
        except Exception as e:
            self.logger.error(f"Failed to load intent classifier: {str(e)}")
            return None

    def _load_ner_model(self):
        """加载命名实体识别模型"""
        try:
            return pipeline("ner", model="uer/roberta-base-chinese-cluener2020")
        except Exception as e:
            self.logger.error(f"Failed to load NER model: {str(e)}")
            return None

    def process_text(self, text: str) -> NLUResult:
        """处理输入文本"""
        try:
            # 基础文本处理
            doc = self.nlp(text)
            
            # 意图识别
            intent = self._classify_intent(text)
            
            # 实体识别
            entities = self._extract_entities(text)
            
            # 情感分析
            sentiment = self._analyze_sentiment(text)
            
            # 解析结果
            parsed_result = self._parse_text(doc)
            
            # 计算置信度
            confidence = self._calculate_confidence(parsed_result)
            
            return NLUResult(
                text=text,
                intent=intent,
                entities=entities,
                sentiment=sentiment,
                confidence=confidence,
                parsed_result=parsed_result
            )
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            return None

    def _classify_intent(self, text: str) -> IntentType:
        """分类意图"""
        try:
            # 使用规则和模型组合的方法
            if '?' in text or '？' in text:
                return IntentType.QUESTION
            
            if any(cmd in text for cmd in self.config.get('command_keywords', [])):
                return IntentType.COMMAND
            
            # 使用模型进行更复杂的意图分类
            if self.intent_classifier:
                result = self.intent_classifier(text)[0]
                if result['score'] > 0.7:
                    return self._map_intent_label(result['label'])
            
            return IntentType.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Intent classification failed: {str(e)}")
            return IntentType.UNKNOWN

    def _extract_entities(self, text: str) -> List[Dict]:
        """提取实体"""
        try:
            entities = []
            
            # 使用spaCy进行基础实体识别
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            # 使用预训练模型进行补充实体识别
            if self.ner_model:
                ner_results = self.ner_model(text)
                for ent in ner_results:
                    if ent['score'] > 0.5:
                        entities.append({
                            'text': ent['word'],
                            'label': ent['entity'],
                            'score': ent['score']
                        })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
            return []

    def _analyze_sentiment(self, text: str) -> float:
        """分析情感"""
        try:
            result = self.sentiment_analyzer(text)[0]
            # 将结果映射到-1到1的范围
            if result['label'] == 'positive':
                return result['score']
            else:
                return -result['score']
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return 0.0

    def _parse_text(self, doc) -> Dict:
        """解析文本"""
        return {
            'tokens': [token.text for token in doc],
            'pos_tags': [token.pos_ for token in doc],
            'dependencies': [(token.text, token.dep_, token.head.text) 
                           for token in doc],
            'noun_chunks': [chunk.text for chunk in doc.noun_chunks]
        }

    def _calculate_confidence(self, parsed_result: Dict) -> float:
        """计算置信度"""
        # 基于各个组件的结果计算整体置信度
        confidence_scores = []
        
        # 添加各种置信度计算逻辑
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

    def _map_intent_label(self, label: str) -> IntentType:
        """映射意图标签"""
        intent_mapping = {
            'query': IntentType.QUERY,
            'command': IntentType.COMMAND,
            'statement': IntentType.STATEMENT,
            'question': IntentType.QUESTION
        }
        return intent_mapping.get(label.lower(), IntentType.UNKNOWN) 