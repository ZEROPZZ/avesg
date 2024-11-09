import logging
from typing import Dict, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSystem:
    def __init__(self):
        self.logger = logging.getLogger('alert_system')
        self._setup_logging()
        
        self.alert_levels = {
            'INFO': 0,
            'WARNING': 1,
            'ERROR': 2,
            'CRITICAL': 3
        }
        
        self.alert_history: List[Dict] = []
        self.email_config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'your-email@example.com',
            'password': 'your-password'
        }

    def _setup_logging(self):
        """设置日志系统"""
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logs/alert_system.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def trigger_alert(self, level: str, message: str, component: str):
        """触发警报"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'component': component
        }
        
        self.alert_history.append(alert)
        self.logger.log(
            getattr(logging, level),
            f"{component}: {message}"
        )
        
        if self.alert_levels[level] >= self.alert_levels['ERROR']:
            self._send_email_alert(alert)

    def _send_email_alert(self, alert: Dict):
        """发送邮件警报"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = 'admin@example.com'
            msg['Subject'] = f"System Alert: {alert['level']} - {alert['component']}"
            
            body = f"""
            Alert Details:
            Level: {alert['level']}
            Component: {alert['component']}
            Message: {alert['message']}
            Time: {alert['timestamp']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.email_config['username'],
                    self.email_config['password']
                )
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")

    def get_alert_history(self, level: Optional[str] = None) -> List[Dict]:
        """获取警报历史"""
        if level:
            return [
                alert for alert in self.alert_history
                if alert['level'] == level
            ]
        return self.alert_history

    def clear_alert_history(self):
        """清除警报历史"""
        self.alert_history = [] 
