import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

def send_email(to_email: str, subject: str, html_content: str):
    """Send an email using SendGrid."""
    try:
        from_email="harshithardyjoshi@gmail.com"
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            raise ValueError("SendGrid API Key not found in environment variables")
        sg = SendGridAPIClient(api_key)
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        response = sg.send(message)
        print(response)
        return {
            "status_code": response.status_code,
            "body": response.body.decode('utf-8') if response.body else "",
            "headers": dict(response.headers),
        }
    except Exception as e:
        raise Exception(f"Error sending email: {str(e)}")
