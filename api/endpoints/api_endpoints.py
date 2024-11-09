from fastapi import APIRouter, HTTPException, Request, Depends # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Dict, List, Optional, Any
import time
from datetime import datetime
import aiohttp # type: ignore

# 定义请求模型
class TextRequest(BaseModel):
    text: str
    context: Optional[Dict] = None
    user_id: Optional[str] = None

class VoiceRequest(BaseModel):
    audio_data: bytes
    format: str = "wav"
    sample_rate: int = 16000
    user_id: Optional[str] = None

class MemoryRequest(BaseModel):
    query: Dict
    user_id: Optional[str] = None

class TriviaRequest(BaseModel):
    amount: int = 1
    category: int = 24
    difficulty: str = "easy"

class BookRequest(BaseModel):
    isbn: str

class WebSearchRequest(BaseModel):
    query: str
    limit: int = 100

class GOTRequest(BaseModel):
    skip: int = 0
    limit: int = 10

# API路由类
class APIEndpoints:
    def __init__(self, system_manager):
        self.router = APIRouter()
        self.system_manager = system_manager
        
        # Trivia API配置
        self.trivia_config = {
            "api_key": "7GJk41orn-GLR0kwzeE4z31o3QYx4TsPkMtfUyx52QmIZWD0Lf",
            "api_host": "Open-Trivia-API.allthingsdev.co",
            "api_endpoint": "e39df3a7-4e1c-40c4-8449-b7ff3ed7b16c",
            "base_url": "https://Open-Trivia-API.proxy-production.allthingsdev.co"
        }
        
        # Books API配置
        self.book_config = {
            "app_version": "1.0.0",
            "api_key": "7GJk41orn-GLR0kwzeE4z31o3QYx4TsPkMtfUyx52QmIZWD0Lf",
            "api_host": "Top-Goodread-Books-collection-1980-to-2023.allthingsdev.co",
            "api_endpoint": "b4591402-4f74-4a16-b18e-c522ee27e837",
            "base_url": "https://Top-Goodread-Books-collection-1980-to-2023.proxy-production.allthingsdev.co"
        }
        
        # Web Search API配置
        self.search_config = {
            "api_key": "7GJk41orn-GLR0kwzeE4z31o3QYx4TsPkMtfUyx52QmIZWD0Lf",
            "api_host": "Real-Time-Web-Search.allthingsdev.co",
            "api_endpoint": "d2f8da3f-6773-4db9-8ef8-eb8d20242ac7",
            "base_url": "https://Real-Time-Web-Search.proxy-production.allthingsdev.co"
        }
        
        # Game of Thrones API配置
        self.got_config = {
            "app_version": "1.0.0",
            "api_key": "7GJk41orn-GLR0kwzeE4z31o3QYx4TsPkMtfUyx52QmIZWD0Lf",
            "api_host": "Game-of-Thrones-API.allthingsdev.co",
            "api_endpoint": "073a1031-7170-4e61-b164-be0f47692394",
            "base_url": "https://Game-of-Thrones-API.proxy-production.allthingsdev.co"
        }
        
        self.setup_routes()

    def setup_routes(self):
        # 文本处理接口
        @self.router.post("/api/v1/text/process")
        async def process_text(request: TextRequest):
            try:
                result = self.system_manager.process_text(
                    text=request.text,
                    context=request.context,
                    user_id=request.user_id
                )
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # 语音处理接口
        @self.router.post("/api/v1/voice/process")
        async def process_voice(request: VoiceRequest):
            try:
                result = self.system_manager.process_voice(
                    audio_data=request.audio_data,
                    format=request.format,
                    sample_rate=request.sample_rate,
                    user_id=request.user_id
                )
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # 记忆查询接口
        @self.router.post("/api/v1/memory/query")
        async def query_memory(request: MemoryRequest):
            try:
                result = self.system_manager.query_memory(
                    query=request.query,
                    user_id=request.user_id
                )
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # 学习状态接口
        @self.router.get("/api/v1/learning/status")
        async def get_learning_status():
            try:
                result = self.system_manager.get_learning_status()
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # 系统健康检查接口
        @self.router.get("/api/v1/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }

        # 1. Trivia API端点
        @self.router.get("/api/v1/trivia")
        async def get_trivia(
            amount: int = 1,
            category: int = 24,
            difficulty: str = "easy"
        ):
            """获取Trivia问题"""
            try:
                headers = {
                    "x-apihub-key": self.trivia_config["api_key"],
                    "x-apihub-host": self.trivia_config["api_host"],
                    "x-apihub-endpoint": self.trivia_config["api_endpoint"]
                }

                url = f"{self.trivia_config['base_url']}/api.php"
                params = {
                    "amount": amount,
                    "category": category,
                    "difficulty": difficulty
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "status": "success",
                                    "data": result,
                                    "timestamp": datetime.now().isoformat()
                                }
                            )
                        else:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Failed to fetch trivia data"
                            )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching trivia: {str(e)}"
                )

        # 2. Books API端点
        @self.router.get("/api/v1/books/{isbn}")
        async def get_book_info(isbn: str):
            """获取图书信息"""
            try:
                headers = {
                    "x-app-version": self.book_config["app_version"],
                    "x-apihub-key": self.book_config["api_key"],
                    "x-apihub-host": self.book_config["api_host"],
                    "x-apihub-endpoint": self.book_config["api_endpoint"]
                }

                url = f"{self.book_config['base_url']}/api/v1/bookread/infmn"
                params = {"isbn": isbn}

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "status": "success",
                                    "data": result,
                                    "timestamp": datetime.now().isoformat()
                                }
                            )
                        else:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Failed to fetch book information"
                            )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching book information: {str(e)}"
                )

        # 3. Web Search API端点
        @self.router.get("/api/v1/search")
        async def web_search(
            q: str,
            limit: int = 100
        ):
            """实时Web搜索"""
            try:
                headers = {
                    "x-apihub-key": self.search_config["api_key"],
                    "x-apihub-host": self.search_config["api_host"],
                    "x-apihub-endpoint": self.search_config["api_endpoint"]
                }

                url = f"{self.search_config['base_url']}/v1/search"
                params = {
                    "q": q,
                    "limit": limit
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "status": "success",
                                    "data": result,
                                    "timestamp": datetime.now().isoformat()
                                }
                            )
                        else:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Failed to perform web search"
                            )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error in web search: {str(e)}"
                )

        # 4. Game of Thrones API端点
        @self.router.get("/api/v1/got/characters")
        async def get_got_characters(
            skip: int = 0,
            limit: int = 10
        ):
            """获取权力的游戏角色信息"""
            try:
                headers = {
                    "x-app-version": self.got_config["app_version"],
                    "x-apihub-key": self.got_config["api_key"],
                    "x-apihub-host": self.got_config["api_host"],
                    "x-apihub-endpoint": self.got_config["api_endpoint"]
                }

                url = f"{self.got_config['base_url']}/api/v1/got/characters"
                params = {
                    "skip": skip,
                    "limit": limit
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "status": "success",
                                    "data": result,
                                    "timestamp": datetime.now().isoformat()
                                }
                            )
                        else:
                            raise HTTPException(
                                status_code=response.status,
                                detail="Failed to fetch GOT characters"
                            )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching GOT characters: {str(e)}"
                )