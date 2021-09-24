from app.helpers.mail import send_mail as mail
from app.helpers.security import oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.post('/send-mail')
async def send_mail(email: str, subject: str, content: str, 
                    token: str = Depends(oauth2_scheme)):
    response = mail(email, subject, content)
    return response.status_code
