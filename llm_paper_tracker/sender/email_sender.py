"""邮件发送模块"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器"""
    
    def __init__(self, 
                 smtp_host: Optional[str] = None,
                 smtp_port: int = 465,
                 smtp_user: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 from_name: str = "LLM Paper Tracker"):
        self.smtp_host = smtp_host or "smtp.qq.com"
        self.smtp_port = smtp_port or 465
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_name = from_name
    
    def send(self, 
             to_emails: List[str],
             subject: str,
             html_content: str,
             text_content: Optional[str] = None) -> bool:
        """发送邮件"""
        if not to_emails:
            logger.error("No recipient emails specified")
            return False
        
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return False
        
        if text_content is None:
            text_content = self._html_to_text(html_content)
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.smtp_user}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = Header(subject, 'utf-8')
            
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, to_emails, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - check credentials")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_paper_report(self, 
                         to_emails: List[str],
                         html_content: str,
                         paper_count: int = 0) -> bool:
        """发送论文简报"""
        date_str = datetime.now().strftime("%Y年%m月%d日")
        subject = f"📚 LLM论文追踪简报 - {date_str} ({paper_count}篇)"
        
        return self.send(to_emails, subject, html_content)
    
    def _html_to_text(self, html: str) -> str:
        """简单HTML转文本"""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        text = text.replace('&quot;', '"')
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def test_connection(self) -> bool:
        """测试SMTP连接"""
        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
