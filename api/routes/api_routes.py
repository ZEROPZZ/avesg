from fastapi import APIRouter, HTTPException, Depends # type: ignore
from typing import Dict, List, Optional
from pydantic import BaseModel # type: ignore
import json

class TextInput(BaseModel):
    text: str
    context: Optional[Dict] = None

class VoiceInput(BaseModel):
    audio_data: bytes
    format: str
    sample_rate: int

class APIRoutes:
    def __init__(self, system_manager):
        self.system_manager = system_manager
        self.router = APIRouter()
        self.setup_routes()
        
    def setup_routes(self):
        """设置所有路由"""
        # 文本处理路由
        @self.router.post("/process/text")
        async def process_text(input_data: TextInput):
            try:
                result = self.system_manager.process_text(
                    input_data.text,
                    input_data.context
                )
                return {"status": "success", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # 语音处理路由
        @self.router.post("/process/voice")
        async def process_voice(input_data: VoiceInput):
            try:
                result = self.system_manager.process_voice(
                    input_data.audio_data,
                    input_data.format,
                    input_data.sample_rate
                )
                return {"status": "success", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # 记忆查询路由
        @self.router.get("/memory/query")
        async def query_memory(query: Dict):
            try:
                result = self.system_manager.query_memory(query)
                return {"status": "success", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # 学习状态路由
        @self.router.get("/learning/status")
        async def get_learning_status():
            try:
                status = self.system_manager.get_learning_status()
                return {"status": "success", "result": status}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) 