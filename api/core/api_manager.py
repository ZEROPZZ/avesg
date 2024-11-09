from fastapi import FastAPI, HTTPException, Depends, Request # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from typing import Dict, List, Optional
import uvicorn # type: ignore
import logging
import json
import time
from datetime import datetime

class APIManager:
    def __init__(self):
        self.app = FastAPI(
            title="AVESG API",
            description="Advanced Voice Enabled System Gateway API",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('api_manager')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logs/api.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def setup_middleware(self):
        """设置中间件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """请求日志中间件"""
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            self.logger.info(
                f"Method: {request.method} Path: {request.url.path} "
                f"Duration: {duration:.2f}s Status: {response.status_code}"
            )
            return response
            
    def setup_routes(self):
        """设置路由"""
        @self.app.get("/")
        async def root():
            return {"message": "AVESG API is running"}
            
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
            
    def add_route(self, path: str, endpoint, methods: List[str]):
        """添加自定义路由"""
        for method in methods:
            self.app.add_api_route(
                path,
                endpoint,
                methods=[method]
            )
            
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """运行API服务器"""
        uvicorn.run(self.app, host=host, port=port) 