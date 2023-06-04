import redis
from fastapi.security import HTTPBearer
from settingup import Session
from passlib.context import CryptContext
from models import User
from decouple import config

security = HTTPBearer()

r = redis.Redis(host=config("REDIS_HOST", default = 'redis'), port=config("REDIS_PORT", default = 6379), db=0)
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    

    
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
            
def does_user_exists(db, login: str):
    try:
        user = db.query(User).filter(User.login == login).first()
        return user is not None
    finally:
        db.close()
               
def hash_user_password(user):
    if user.password:
        user.password = pwd_context.hash(user.password)
        
def logout(user):
    r.delete(user.id)
    



    