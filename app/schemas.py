from pydantic import BaseModel
from datetime import datetime

from app.database import Base

#Class for request schemas

class PostBase(BaseModel):
    title: str #Mandatory field 
    content: str
    published: bool = True  #If no value is passed, defaults to True
    #rating: Optional[int] = None #Value is optional with type int, and default is None

class PostCreate(PostBase):
    pass

# Class for response schemas

class PostResponse(BaseModel):
    title: str
    content: str
    published: bool
    class Config:
        orm_mode = True