import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    from_name: Optional[str] = "Bryan"
    is_html: Optional[bool] = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/send-email")
def send_email(req: EmailRequest):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = req.subject
        msg["From"] = f"{req.from_name} <{GMAIL_ADDRESS}>"
        msg["To"] = req.to

        content_type = "html" if req.is_html else "plain"
        msg.attach(MIMEText(req.body, content_type))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, req.to, msg.as_string())

        return {"success": True, "message": f"Email sent to {req.to}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
