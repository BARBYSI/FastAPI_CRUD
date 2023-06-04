from pydantic import BaseModel


class UserAuth(BaseModel):
    login: str
    password: str
    
class TaskTemplate(BaseModel):
    title: str
    description: str
    
class DeleteTask(BaseModel):
    id: int  