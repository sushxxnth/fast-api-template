from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.crud.user import (
    get_user, get_users, create_user, update_user, delete_user, get_user_by_email
)

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate):
    db_user = await get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = await create_user(user)
    return created_user

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    db_user = await get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=list[UserResponse])
async def read_users(skip: int = 0, limit: int = 100):
    users = await get_users(skip, limit)
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: str, user: UserUpdate):
    db_user = await get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await update_user(user_id, user)
    return updated_user

@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user_endpoint(user_id: str):
    db_user = await get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = await delete_user(user_id)
    return deleted_user
