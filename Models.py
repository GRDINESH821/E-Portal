from pydantic import BaseModel, Field
from datetime import datetime,date
from bson import ObjectId
from typing import List, Optional

class ApplyLeave(BaseModel):
    StartDate : str
    EndDate : str
    AppliedBy : str
    Reason :str


class LeaveInDB(ApplyLeave):
    _id:ObjectId
    Manager: str
    status : str = 'Pending'
    createdTime : datetime = Field(default_factory=datetime.utcnow)

class Holiday(BaseModel):
    HolidayName : str
    Date :datetime
class UserLogin(BaseModel):
    username: str
    password: str

class UpdateLogin(UserLogin):
    newpassword : str
    updatedTime: datetime = Field(default_factory=datetime.utcnow)
class User(UserLogin):

    firstName: str
    lastName: str
    DOB : str


class UserInDB(User):
    _id: ObjectId
    role: str
    Manager : str = None
    createdTime: datetime = Field(default_factory=datetime.utcnow)
    updatedTime: datetime = Field(default_factory=datetime.utcnow)

class Reporties(BaseModel):
    Manager : str

class TaskModel(BaseModel):
    Task : str
    TaskDescription : str
    username : str
    Technology : str
    WorkLink : str
    
class TaskInDB(TaskModel):
    _id: ObjectId
    createdTime: datetime = Field(default_factory=datetime.utcnow)
    updatedTime: datetime = Field(default_factory=datetime.utcnow)
class DeleteTask(BaseModel):
    username  : str
    id : str


class TokenResponse(BaseModel):
    token: str
    userName: str
    firstName: str
    lastName: str
    type: str
    role: str


class TokenRequest(BaseModel):
    userName: str
    password: str