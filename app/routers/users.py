import os

import jwt
from app.database.models.user import (User, User_Pydantic, UserIn_Pydantic,
                                      UserToken, UserToken_Pydantic)
from app.helpers.mail import send_mail
from app.helpers.security import (create_verification_token,
                                         validate_token, SECRET_KEY, authenticate_user,
                                   get_current_user)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt

router = APIRouter()


@router.get("/healthz")
async def health_check():
    return {'Health': os.getenv('DATABASE_URL')}


@router.post('/users')
async def create_user(user: UserIn_Pydantic):
    user_obj = await User.create(**user.dict(exclude_unset=True))
    user_obj.password_hash = bcrypt.hash(user.password_hash)
    await user_obj.save()
    verification_token = await create_verification_token(user_obj)
    send_mail(user_obj.email, "Activate Account", f'<strong>{verification_token.token}</strong>')
    return await User_Pydantic.from_tortoise_orm(user_obj)


@router.post('/users/activate')
async def activate_user(activation_token):
    result = await validate_token(activation_token)
    if result['status_code'] == 200:
        await User.get(id=result['user']).update(is_active = True)
        return await User_Pydantic.from_queryset_single(User.get(id=result['user']))
    return result


@router.get('/users' , response_model=User_Pydantic)
async def get_users():
    return await User_Pydantic.from_queryset(User.all())


@router.get('/users/{user_id}' , response_model=User_Pydantic)
async def get_user(user_id: int):
    return await User_Pydantic.from_queryset_single(User.get(id=user_id))


@router.put('/users/{user_id}', response_model=User_Pydantic)
async def update_user(user_id: int, user: UserIn_Pydantic):
    user.password_hash = bcrypt.hash(user.password_hash)
    await User.get(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(User.get(id=user_id))


@router.delete('/users/{user_id}')
async def delete_user(user_id: int):
    await User.filter(id=user_id).delete()
    return {}


@router.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), SECRET_KEY)

    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/users/me', response_model=User_Pydantic)
async def get_session_user(user: User_Pydantic = Depends(get_current_user)):
    return user  


@router.post('/forgot-password')
async def forgot_password(email: str):
    user = await User.get(email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user_token_obj = await create_verification_token(user)
        send_mail(email, "VanUse - Reset Password", f'<strong>{user_token_obj.token}</strong>')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f'Oops Something Went wrong {e.message}'
        )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(user_token_obj))


@router.post("/reset-password",)
async def reset_password(reset_token: str, password: str, confirmed_password: str):
    result = await validate_token(reset_token)
    if result['status_code'] == 200 and password == confirmed_password:
        await User.get(id=result['user']).update(password_hash= bcrypt.hash(password))
        return await User_Pydantic.from_queryset_single(User.get(id=result['user']))
    return result  # <-- JSONResponse


@router.get("/all-tokens")
async def get_tokens():
    return await UserToken_Pydantic.from_queryset(UserToken.all())
