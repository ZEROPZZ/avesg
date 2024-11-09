from typing import Dict, Any, Optional
import aiohttp # type: ignore
import asyncio
import json
import logging
from datetime import datetime

class RequestHandler:
    def __init__(self):
        self.logger = logging.getLogger('request_handler')
        self.setup_logging()
        self.session = None

    def setup_logging(self):
        handler = logging.FileHandler('logs/requests.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def initialize(self):
        """初始化异步会话"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
            self.session = None

    async def send_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None, 
        headers: Optional[Dict] = None
    ) -> Dict:
        """发送请求"""
        try:
            await self.initialize()
            
            default_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            headers = headers or default_headers
            
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                self.logger.info(
                    f"Request: {method} {url} - Status: {response.status}"
                )
                
                return {
                    'status_code': response.status,
                    'data': response_data,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    async def process_text(self, text: str, context: Optional[Dict] = None) -> Dict:
        """处理文本请求"""
        url = "http://localhost:8000/api/v1/text/process"
        data = {
            "text": text,
            "context": context
        }
        return await self.send_request("POST", url, data)

    async def process_voice(
        self, 
        audio_data: bytes, 
        format: str = "wav", 
        sample_rate: int = 16000
    ) -> Dict:
        """处理语音请求"""
        url = "http://localhost:8000/api/v1/voice/process"
        data = {
            "audio_data": audio_data,
            "format": format,
            "sample_rate": sample_rate
        }
        return await self.send_request("POST", url, data)

    async def query_memory(self, query: Dict) -> Dict:
        """查询记忆"""
        url = "http://localhost:8000/api/v1/memory/query"
        return await self.send_request("POST", url, {"query": query})

    async def get_learning_status(self) -> Dict:
        """获取学习状态"""
        url = "http://localhost:8000/api/v1/learning/status"
        return await self.send_request("GET", url) 