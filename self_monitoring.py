import psutil # type: ignore
import logging
import time
import json
import os
import numpy as np # type: ignore
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import Thread, Lock
import matplotlib.pyplot as plt # type: ignore
from collections import deque

class SelfMonitoring:
    def __init__(self, max_history_size: int = 1000):
        # 初始化监控参数
        self.monitoring_active = False
        self.monitor_thread: Optional[Thread] = None
        self.lock = Lock()
        
        # 性能指标历史记录
        self.metrics_history = {
            'cpu_usage': deque(maxlen=max_history_size),
            'memory_usage': deque(maxlen=max_history_size),
            'disk_usage': deque(maxlen=max_history_size),
            'network_io': deque(maxlen=max_history_size),
            'gpu_usage': deque(maxlen=max_history_size) if self._has_gpu() else None
        }
        
        # 警报阈值
        self.thresholds = {
            'cpu_usage': 80.0,  # CPU使用率阈值
            'memory_usage': 85.0,  # 内存使用率阈值
            'disk_usage': 90.0,  # 磁盘使用率阈值
            'network_latency': 100.0,  # 网络延迟阈值（毫秒）
            'gpu_usage': 85.0 if self._has_gpu() else None  # GPU使用率阈值
        }
        
        # 设置日志
        self._setup_logging()
        
        # 加载配置
        self.config = self._load_config()
        
        # 性能统计
        self.performance_stats = {
            'start_time': datetime.now(),
            'total_alerts': 0,
            'critical_events': 0
        }
        
    def _setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            filename='system_monitoring.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_config(self) -> Dict:
        """加载监控配置"""
        try:
            if os.path.exists('monitoring_config.json'):
                with open('monitoring_config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
        
        # 默认配置
        return {
            'monitoring_interval': 1.0,  # 监控间隔（秒）
            'alert_cooldown': 300,  # 警报冷却时间（秒）
            'save_metrics_interval': 3600,  # 指标保存间隔（秒）
            'visualization_enabled': True
        }
        
    def start_monitoring(self):
        """启动监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logging.info("监控系统已启动")
            
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
            logging.info("监控系统已停止")
            
    def _monitoring_loop(self):
        """监控主循环"""
        last_save_time = time.time()
        
        while self.monitoring_active:
            try:
                # 收集系统指标
                metrics = self._collect_metrics()
                
                # 更新历史记录
                self._update_history(metrics)
                
                # 检查警报条件
                self._check_alerts(metrics)
                
                # 定期保存指标
                if time.time() - last_save_time > self.config['save_metrics_interval']:
                    self._save_metrics()
                    last_save_time = time.time()
                    
                # 可视化更新
                if self.config['visualization_enabled']:
                    self._update_visualization()
                    
                time.sleep(self.config['monitoring_interval'])
                
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(5)  # 错误恢复等待
                
    def _collect_metrics(self) -> Dict[str, float]:
        """收集系统指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': self._get_network_usage()
        }
        
        # 如果有GPU，添加GPU指标
        if self._has_gpu():
            metrics['gpu_usage'] = self._get_gpu_usage()
            
        return metrics
        
    def _update_history(self, metrics: Dict[str, float]):
        """更新指标历史记录"""
        with self.lock:
            for key, value in metrics.items():
                if key != 'timestamp' and key in self.metrics_history:
                    self.metrics_history[key].append(value)
                    
    def _check_alerts(self, metrics: Dict[str, float]):
        """检查是否需要发出警报"""
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds:
                threshold = self.thresholds[metric_name]
                if value > threshold:
                    self._trigger_alert(metric_name, value, threshold)
                    
    def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """触发警报"""
        alert_msg = f"警报: {metric_name} ({value:.2f}) 超过阈值 {threshold:.2f}"
        logging.warning(alert_msg)
        self.performance_stats['total_alerts'] += 1
        
        if value > threshold * 1.2:  # 严重警报
            self.performance_stats['critical_events'] += 1
            
    def _save_metrics(self):
        """保存监控指标到文件"""
        try:
            with open('monitoring_metrics.json', 'w') as f:
                json.dump(self.get_metrics_summary(), f)
        except Exception as e:
            logging.error(f"保存指标失败: {e}")
            
    def _update_visualization(self):
        """更新监控可视化"""
        if not hasattr(self, 'fig'):
            plt.ion()
            self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
            self.fig.suptitle('系统监控实时数据')
            
        # 更新图表
        self._plot_metric(self.axes[0, 0], 'cpu_usage', 'CPU使用率 (%)')
        self._plot_metric(self.axes[0, 1], 'memory_usage', '内存使用率 (%)')
        self._plot_metric(self.axes[1, 0], 'disk_usage', '磁盘使用率 (%)')
        self._plot_metric(self.axes[1, 1], 'network_io', '网络I/O (MB/s)')
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.1)
        
    def _plot_metric(self, ax, metric_name: str, title: str):
        """绘制单个指标的图表"""
        ax.clear()
        if self.metrics_history[metric_name]:
            data = list(self.metrics_history[metric_name])
            ax.plot(data)
            ax.set_title(title)
            ax.set_ylim(0, 100 if 'usage' in metric_name else None)
            ax.grid(True)
            
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取监控指标摘要"""
        with self.lock:
            summary = {
                'current_metrics': self._collect_metrics(),
                'averages': {},
                'max_values': {},
                'performance_stats': self.performance_stats
            }
            
            for metric_name, values in self.metrics_history.items():
                if values:
                    values_array = np.array(values)
                    summary['averages'][metric_name] = float(np.mean(values_array))
                    summary['max_values'][metric_name] = float(np.max(values_array))
                    
            return summary
            
    def _has_gpu(self) -> bool:
        """检查是否有GPU"""
        try:
            import torch # type: ignore
            return torch.cuda.is_available()
        except ImportError:
            return False
            
    def _get_gpu_usage(self) -> float:
        """获取GPU使用率"""
        try:
            import torch # type: ignore
            return torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
        except Exception:
            return 0.0
            
    def _get_network_usage(self) -> float:
        """获取网络使用率"""
        net_io = psutil.net_io_counters()
        return (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024  # MB
        
    def set_threshold(self, metric_name: str, value: float):
        """设置警报阈值"""
        if metric_name in self.thresholds:
            self.thresholds[metric_name] = value
            logging.info(f"更新阈值 {metric_name}: {value}")
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return self.performance_stats
        
    def reset_stats(self):
        """重置统计信息"""
        self.performance_stats = {
            'start_time': datetime.now(),
            'total_alerts': 0,
            'critical_events': 0
        }

if __name__ == "__main__":
    # 测试监控系统
    monitor = SelfMonitoring()
    monitor.start_monitoring()
    
    try:
        # 运行一段时间进行测试
        time.sleep(30)
        
        # 打印监控摘要
        print(json.dumps(monitor.get_metrics_summary(), indent=2))
        
    finally:
        monitor.stop_monitoring()
