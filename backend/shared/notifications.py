from typing import Optional, Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    body: str,
    html: Optional[str] = None,
    cc: Optional[list] = None,
    bcc: Optional[list] = None
) -> bool:
    """Send email notification"""
    try:
        if not settings.SMTP_HOST:
            logger.warning("SMTP not configured, skipping email")
            return False
        
        message = MIMEMultipart("alternative")
        message["From"] = settings.EMAIL_FROM
        message["To"] = to
        message["Subject"] = subject
        
        if cc:
            message["Cc"] = ", ".join(cc)
        if bcc:
            message["Bcc"] = ", ".join(bcc)
        
        # Add plain text
        message.attach(MIMEText(body, "plain"))
        
        # Add HTML if provided
        if html:
            message.attach(MIMEText(html, "html"))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )
        
        logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


async def send_sms(phone: str, message: str) -> bool:
    """Send SMS notification"""
    try:
        if not settings.SMS_API_URL:
            logger.warning("SMS API not configured, skipping SMS")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SMS_API_URL,
                json={
                    "phone": phone,
                    "message": message,
                    "api_key": settings.SMS_API_KEY
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                logger.error(f"SMS API returned status {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return False


async def send_notification(
    user_email: str,
    user_phone: Optional[str],
    subject: str,
    message: str,
    html: Optional[str] = None,
    send_email_flag: bool = True,
    send_sms_flag: bool = False
) -> Dict[str, bool]:
    """Send notification via email and/or SMS"""
    results = {}
    
    if send_email_flag:
        results["email"] = await send_email(user_email, subject, message, html)
    
    if send_sms_flag and user_phone:
        results["sms"] = await send_sms(user_phone, message)
    
    return results
