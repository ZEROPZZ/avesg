from typing import Dict, Any
from fastapi.responses import JSONResponse # type: ignore
import json
import logging
from datetime import datetime

class ResponseHandler:
    def __init__(self):
        self.logger = logging.getLogger('response_handler')
        self.setup_logging()

    def setup_logging(self):
        handler = logging.FileHandler('logs/responses.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def format_response(
        self, 
        data: Any, 
        status_code: int = 200, 
        message: str = "Success"
    ) -> JSONResponse:
        """格式化响应"""
        response_data = {
            "status": "success" if status_code < 400 else "error",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(
            f"Response: status_code={status_code}, message={message}"
        )
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    def handle_error(
        self, 
        error: Exception, 
        status_code: int = 500
    ) -> JSONResponse:
        """处理错误响应"""
        error_message = str(error)
        
        self.logger.error(
            f"Error: status_code={status_code}, message={error_message}"
        )
        
        return JSONResponse(
            content={
                "status": "error",
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            },
            status_code=status_code
        ) 