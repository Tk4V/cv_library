"""
SendGrid email service for reliable email delivery.
"""
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

logger = logging.getLogger(__name__)


class SendGridService:
    """SendGrid email service wrapper"""
    
    def __init__(self, api_key=None):
        """
        Initialize SendGrid service
        
        Args:
            api_key: SendGrid API key (optional, will read from env if not provided)
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SendGrid API key is required")
        
        self.sg = SendGridAPIClient(api_key=self.api_key)
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@yourdomain.com')
        logger.info("📧 SendGrid service initialized")

    def send_email_with_attachment(self, to_email, subject, content, pdf_content=None, pdf_filename=None):
        """
        Send email with optional PDF attachment using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email body (HTML or plain text)
            pdf_content: PDF file content as bytes (optional)
            pdf_filename: PDF filename (optional)
            
        Returns:
            Dict with status and message
        """
        try:
            logger.info(f"📧 Preparing SendGrid email to: {to_email}")
            
            # Create the email
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            
            # Add PDF attachment if provided
            if pdf_content and pdf_filename:
                encoded_pdf = base64.b64encode(pdf_content).decode()
                attachment = Attachment(
                    FileContent(encoded_pdf),
                    FileName(pdf_filename),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.attachment = attachment
                logger.info(f"📎 PDF attachment added: {pdf_filename} ({len(pdf_content)} bytes)")
            
            # Send the email
            response = self.sg.send(message)
            logger.info(f"✅ SendGrid email sent successfully. Status: {response.status_code}")
            
            return {
                'status': 'success',
                'message': f'Email sent to {to_email}',
                'recipient': to_email,
                'status_code': response.status_code
            }
            
        except Exception as e:
            logger.error(f"❌ SendGrid email failed: {str(e)}")
            logger.exception("Full exception details:")
            
            # Try to get more details from the error
            error_details = str(e)
            if hasattr(e, 'body'):
                logger.error(f"❌ SendGrid error body: {e.body}")
                error_details = f"{str(e)} - Body: {e.body}"
            if hasattr(e, 'to_dict'):
                logger.error(f"❌ SendGrid error dict: {e.to_dict}")
            
            return {
                'status': 'error',
                'error': error_details,
                'recipient': to_email
            }
    
    def send_simple_email(self, to_email, subject, content):
        """
        Send simple email without attachments
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email body (HTML or plain text)
            
        Returns:
            Dict with status and message
        """
        return self.send_email_with_attachment(to_email, subject, content)

