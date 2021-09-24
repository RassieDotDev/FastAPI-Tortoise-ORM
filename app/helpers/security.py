import copy, os, uuid, jwt
from datetime import datetime
from app.database.models.user import User, User_Pydantic, UserToken
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from tortoise import timezone


async def validate_token(reset_token):
    user_token = await UserToken.get(token=reset_token)
    if user_token is not None:
        user_id = copy.deepcopy(user_token.user_id)
        diff = datetime.now() - timezone.make_naive(user_token.created_at, timezone=None)
        if diff.total_seconds() < 300:
            await UserToken.filter(token=reset_token).delete()
            return {'status_code': 200, 'user': user_id}
        await UserToken.filter(token=reset_token).delete()
        return JSONResponse(status_code=404, content="Token Expired")
    return JSONResponse(status_code=404, content="Invalid Token")


async def create_verification_token(user):
    user_token_obj = await UserToken(token= uuid.uuid4())
    user_token_obj.created_at = datetime.now()
    user_token_obj.user = user
    await user_token_obj.save()
    return await user_token_obj
    


SECRET_KEY = os.getenv('JWT_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = 20160 #14 Days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(username: str, password: str):
    user = await User.get(email=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)
