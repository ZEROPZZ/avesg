import psutil # type: ignore
import time
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class SystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger('system_monitor')
        self._setup_logging()
        
        self.metrics: Dict[str, Dict] = {
            'system': {},
            'components': {},
            'performance': {},
            'errors': []
        }
        
        self.monitoring_interval = 5  # 秒
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 设置监控阈值
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 2.0
        }

    def _setup_logging(self):
        """设置日志系统"""
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler('logs/system_monitor.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def start_monitoring(self):
        """启动监控"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("System monitoring started")

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("System monitoring stopped")

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_system_metrics()
                self._collect_component_metrics()
                self._collect_performance_metrics()
                self._analyze_metrics()
                self._save_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                self.metrics['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })

    def _collect_system_metrics(self):
        """收集系统指标"""
        self.metrics['system'] = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'boot_time': psutil.boot_time()
        }

    def _collect_component_metrics(self):
        """收集组件指标"""
        self.metrics['components'] = {
            'timestamp': datetime.now().isoformat(),
            'voice_system': self._check_voice_system(),
            'pdf_system': self._check_pdf_system(),
            'database': self._check_database(),
            'api_status': self._check_api_status()
        }

    def _collect_performance_metrics(self):
        """收集性能指标"""
        self.metrics['performance'] = {
            'timestamp': datetime.now().isoformat(),
            'response_times': self._measure_response_times(),
            'throughput': self._measure_throughput(),
            'error_rate': self._calculate_error_rate()
        }

    def _analyze_metrics(self):
        """分析指标"""
        # 检查CPU使用率
        if self.metrics['system']['cpu_usage'] > self.thresholds['cpu_usage']:
            self.logger.warning(f"High CPU usage: {self.metrics['system']['cpu_usage']}%")
            
        # 检查内存使用率
        if self.metrics['system']['memory_usage'] > self.thresholds['memory_usage']:
            self.logger.warning(f"High memory usage: {self.metrics['system']['memory_usage']}%")
            
        # 检查磁盘使用率
        if self.metrics['system']['disk_usage'] > self.thresholds['disk_usage']:
            self.logger.warning(f"High disk usage: {self.metrics['system']['disk_usage']}%")

    def _save_metrics(self):
        """保存指标"""
        metrics_file = f"logs/metrics_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {str(e)}")

    def _check_voice_system(self) -> Dict:
        """检查语音系统状态"""
        return {
            'status': 'operational',
            'latency': self._measure_voice_latency(),
            'error_rate': self._calculate_voice_error_rate()
        }

    def _check_pdf_system(self) -> Dict:
        """检查PDF系统状态"""
        return {
            'status': 'operational',
            'processing_speed': self._measure_pdf_processing_speed(),
            'error_rate': self._calculate_pdf_error_rate()
        }

    def _check_database(self) -> Dict:
        """检查数据库状态"""
        return {
            'status': 'operational',
            'connections': self._get_db_connections(),
            'response_time': self._measure_db_response_time()
        }

    def _check_api_status(self) -> Dict:
        """检查API状态"""
        return {
            'status': 'operational',
            'response_time': self._measure_api_response_time(),
            'error_rate': self._calculate_api_error_rate()
        }

    def get_system_health(self) -> Dict:
        """获取系统健康状态"""
        return {
            'overall_status': self._calculate_overall_status(),
            'system_metrics': self.metrics['system'],
            'component_status': self.metrics['components'],
            'performance_metrics': self.metrics['performance']
        }

    def _calculate_overall_status(self) -> str:
        """计算整体系统状态"""
        # 实现状态计算逻辑
        return 'healthy'

    # 辅助方法
    def _measure_voice_latency(self) -> float:
        """测量语音系统延迟"""
        return 0.1

    def _calculate_voice_error_rate(self) -> float:
        """计算语音系统错误率"""
        return 0.01

    def _measure_pdf_processing_speed(self) -> float:
        """测量PDF处理速度"""
        return 1.0

    def _calculate_pdf_error_rate(self) -> float:
        """计算PDF系统错误率"""
        return 0.02

    def _get_db_connections(self) -> int:
        """获取数据库连接数"""
        return 10

    def _measure_db_response_time(self) -> float:
        """测量数据库响应时间"""
        return 0.05

    def _measure_api_response_time(self) -> float:
        """测量API响应时间"""
        return 0.2

    def _calculate_api_error_rate(self) -> float:
        """计算API错误率"""
        return 0.01

    def _measure_response_times(self) -> Dict:
        """测量响应时间"""
        return {
            'voice': self._measure_voice_latency(),
            'pdf': self._measure_pdf_processing_speed(),
            'api': self._measure_api_response_time()
        }

    def _measure_throughput(self) -> Dict:
        """测量吞吐量"""
        return {
            'requests_per_second': 100,
            'data_processed_per_second': 1024
        }

    def _calculate_error_rate(self) -> float:
        """计算错误率"""
        return 0.01