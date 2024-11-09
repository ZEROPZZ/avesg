from typing import Dict, List, Optional
from .nlp_processor import NLPProcessor
from .nlu_core import NLUCore

class LanguageManager:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.nlu_core = NLUCore()
        self.context = {}
        
    def process_input(self, text: str, context: Optional[Dict] = None) -> Dict:
        """处理输入文本"""
        # 更新上下文
        if context:
            self.context.update(context)
            
        # 处理文本
        processing_result = self.nlp_processor.process_text(text)
        
        # 理解意图和实体
        understanding_result = self.nlu_core.process_text(text)
        
        # 合并结果
        result = {
            'processing': processing_result,
            'understanding': understanding_result,
            'context': self.context
        }
        
        # 更新上下文
        self._update_context(result)
        
        return result

    def _update_context(self, result: Dict):
        """更新上下文信息"""
        # 更新实体信息
        if 'entities' in result['understanding']:
            self.context['entities'] = result['understanding']['entities']
            
        # 更新意图信息
        if 'intent' in result['understanding']:
            self.context['last_intent'] = result['understanding']['intent']
            
        # 限制上下文大小
        if len(self.context) > 1000:
            self.context.pop(list(self.context.keys())[0])

    def get_response_suggestion(self, processing_result: Dict) -> str:
        """获取响应建议"""
        # 基于处理结果生成响应建议
        try:
            intent = processing_result['understanding'].intent
            entities = processing_result['understanding'].entities
            sentiment = processing_result['understanding'].sentiment
            
            # 根据不同意图生成响应
            if intent == IntentType.QUESTION: # type: ignore
                return self._generate_question_response(entities)
            elif intent == IntentType.COMMAND: # type: ignore
                return self._generate_command_response(entities)
            else:
                return self._generate_default_response(sentiment)
                
        except Exception as e:
            print(f"Response suggestion generation failed: {str(e)}")
            return "我明白了。"

    def _generate_question_response(self, entities: List[Dict]) -> str:
        """生成问题响应"""
        # 实现问题响应生成逻辑
        return "让我为您查找相关信息。"

    def _generate_command_response(self, entities: List[Dict]) -> str:
        """生成命令响应"""
        # 实现命令响应生成逻辑
        return "好的，我会执行您的命令。"

    def _generate_default_response(self, sentiment: float) -> str:
        """生成默认响应"""
        if sentiment > 0:
            return "很高兴听到这个。"
        elif sentiment < 0:
            return "我理解您的感受。"
        else:
            return "我明白了。" 