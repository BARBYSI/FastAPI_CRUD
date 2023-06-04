from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
# from fastapi_redis_cache import FastApiRedisCache, cache, cache_one_hour
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy import cast, String
from models import User, Task
from settingup import Session
from schemas import UserAuth, TaskTemplate, DeleteTask
from db import get_db, hash_user_password, does_user_exists, logout
from db import pwd_context
from auth_handler import createJWT, get_user_id_from_token
from auth_bearer import JWTBearer
from decouple import config



limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter

# @app.on_event("startup")
# def startup():
#     redis_cache = FastApiRedisCache()
#     redis_cache.init(
#         host_url=config("REDIS_URL"),
#         prefix="api-cache",
#         response_header="X-API-Cache",
#         ignore_arg_types=[Request, Response, Session],
#     )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Rate limit exceeded. Try again later."},
    )


@app.post("/register")
@limiter.limit("100/minute")
def signup(request: Request, user: UserAuth, db: Session = Depends(get_db)):
    user = User(login=user.login, password=user.password)
    if does_user_exists(db, user.login):
        raise HTTPException(status_code=400, detail="User already exists")
    hash_user_password(user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Sign up successul"}

@app.post("/login")
@limiter.limit("100/minute")
def login(request: Request, user: UserAuth, db: Session = Depends(get_db)):
    if does_user_exists(db, user.login) and pwd_context.verify(user.password, db.query(User).filter(User.login == user.login).first().password):
        user_id = db.query(User).filter(User.login == user.login).first().id
        return createJWT(user_id)
    return{
        "error": "Incorrect login or password"
    }

@app.post("/logout")
@limiter.limit("100/minute")
def logout(request: Request, response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}


@app.post("/tasks")
@limiter.limit("100/minute")
def create_task(request: Request, task: TaskTemplate, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
        user_id = get_user_id_from_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        new_task = Task(title=task.title, description=task.description)
        try:
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
        except:    
            raise HTTPException(status_code=400, detail=str('Task already exists'))
        task_id = db.query(Task).filter(Task.title == new_task.title).first().id 
        new_task = db.query(Task).filter(Task.id == task_id).first()
        task_id = cast(task_id, String)
        user.tasks.append(new_task)
        print(task_id, user.tasks)
        db.commit()
        db.refresh(user)

        return new_task

@app.get("/tasks")
@limiter.limit("100/minute")
# @cache(expire=600)
def get_tasks(request: Request, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    # tasks_json = [task.to_dict() for task in tasks]
    return tasks

@app.get("/tasks/{task_id}")
@limiter.limit("100/minute")
# @cache_one_hour()
def get_task(request: Request, task_id: int, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    return db_task

@app.put("/tasks/{task_id}")
def edit_task(request: Request, task_id: int, task: TaskTemplate, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task.id).first()
    db_task.title = task.title
    db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
@limiter.limit("100/minute")
def delete_task(request: Request, task_id: int, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    db.query(Task).filter(Task.id == task_id).delete()
    db.commit()
    return {"message": "Task deleted"}

@app.get("/api/users")
@limiter.limit("100/minute")
# @cache_one_hour()
def get_users(request: Request, db: Session = Depends(get_db)):
    return db.query(User).all()

