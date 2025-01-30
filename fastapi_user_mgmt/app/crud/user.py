from app.database.session import db
from app.models.user import UserCreate, UserUpdate, UserResponse
from passlib.context import CryptContext
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        return UserResponse(**user)
    return None

async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        return UserResponse(**user)
    return None

async def get_users(skip: int = 0, limit: int = 100):
    users = await db.users.find().skip(skip).limit(limit).to_list(limit)
    for user in users:
        user["id"] = str(user["_id"])
    return [UserResponse(**user) for user in users]

async def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    new_user["id"] = str(new_user["_id"])
    return UserResponse(**new_user)

async def update_user(user_id: str, user: UserUpdate):
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user["_id"])
    return UserResponse(**updated_user)

async def delete_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        await db.users.delete_one({"_id": ObjectId(user_id)})
        user["id"] = str(user["_id"])
        return UserResponse(**user)
    return None