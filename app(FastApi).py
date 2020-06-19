import pprint
from fastapi import FastAPI,requests
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, MONGODB_DB_NAME
import asyncio
from Models import UserInDB,TaskModel,User,Reporties,TaskInDB,UserLogin,UpdateLogin,DeleteTask,ApplyLeave,LeaveInDB
import bcrypt
from fastapi.middleware.cors import CORSMiddleware
import datetime
from flask import jsonify
from bson import ObjectId
import json
from fastapi.encoders import jsonable_encoder
from pydantic import Field
from datetime import datetime
app = FastAPI(title= 'E-Portal',version='1.0')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = AsyncIOMotorClient(MONGODB_URL)

db = client.get_database("MONGODB_DB_NAME")
collection = db.get_collection("users")

@app.post("/login")
async def login(user :UserLogin):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({"username": user.username})
    if row and row['password'] == user.password:
        return {'TRUE'}
    else:
        return {'FALSE'}
@app.put("/login")
async def Update(user:UpdateLogin):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({'username':user.username})
    if row:
        print("user exists")
        if row['password'] == user.password:
            raw = await collection.update_one({'username':user.username},{'$set':{'password':user.newpassword}})
            return {'message':'password updated'}
        else:
            print("Entered wrong password")
            return {'message':'password is invalid'}
    else:
        print("user desnot exist")
        return {'message':'user doesnot exist'}


@app.post("/leave")
async def add_leave_post(user:ApplyLeave):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("Leaves")
    userCollection =db.get_collection("users")
    raw = await userCollection.find_one({'username':user.AppliedBy})
    row = await collection.find_one({'AppliedBy': user.AppliedBy})
    userdetails : List[UserInDB] = []
    if row :
        print("Request Exists")
        return {'message':'Request Exists'}
    else:
        if raw:
            #data = UserInDB(**raw)
            userdetails = UserInDB(**raw)
            leave = {'StartDate':user.StartDate,'EndDate':user.EndDate,'Manager':userdetails.Manager,
                 'AppliedBy':user.AppliedBy,'Reason':user.Reason}
            Request = LeaveInDB(**leave)
            responce = await collection.insert_one(Request.dict())
            return {'message':'Request sent'}

@app.get("/get_TasksbyId")
async def get_Tasks(id:str,username:str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("AppTask")
    row = await collection.find_one({'_id': ObjectId(id)})
    if row:
        if row['username']==username:
            print('Task Exists')
            tasks = TaskInDB(**row)
            return tasks
    else:
        print('Task Doesnot Exists')
        return {'message':"Task doesn't exist "}

@app.get("/get_Tasks_byUser")
async def get_Tasks_byUser(User : str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("AppTask")
    row =  collection.find()
    tasksList : List[TaskInDB] = []

    taskId = []
    tasks = []
    if row:
        print('Task Exists')
        async for task in row:
            if task['username'] == User:
                #asks.append({'Task':task['Task']})
                print(task)
                taskId.append({'_id':str(task['_id'])})
                data = TaskInDB(**task)
                print(data)
                tasks.append(task)

                tasksList.append(data)
                #print(tasks)
                #print(data)
        print(tasks)
        returndata,taskId



    else:
        print('Task Doesnot Exists')
        return {'message': "Task doesn't exist "}


    
@app.get("/get_reportiesTasks")
async def get_reportiesTask(username : str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    TaskCollection = db.get_collection("AppTasks")
    row = collection.find({"Manager":username})
    tasks =  TaskCollection.find()
    works = []
    workId = []
    if row:
        async for user in row:
            print(user)
            async for task in tasks:
                print(task)
                if user['username'] == task['username']:
                    works.append({'Task' : task['Task']})
                    workId.append({'_id' : task['_id']})
    return works,workId

@app.get("/getA_reportiesTasks")
async def getA_reportiesTask(username : str,reportie :str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    TaskCollection = db.get_collection("AppTasks")
    row = await collection.find_one({"username":reportie})
    tasks =  TaskCollection.find()
    works : List[TaskInDB] = []
    workId = []
    #reportiedata = UserInDB(**row)
    print(row)
    if row['Manager'] == username:
        print('in')
        print(tasks)
        async for task in tasks:
            print(task)
            if task['username'] == reportie :
                data = TaskInDB(**task)
                works.append(task)
                workId.append({'_id' : task['_id']})
    return works,workId

@app.get("/get_reporties")
async def get_reporties(username:str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    users =  collection.find({"Manager": username})
    groups: List[UserInDB] = []
    async for document in users:
        data = UserInDB(**document)
        groups.append(data)
    return groups

@app.put("/set_reportie")
async def set_reportie(username : str ,reportieId : str ):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({"_id":ObjectId(reportieId)})
    raw = await collection.update_one({"_id":ObjectId(reportieId)}, {'$set': {'Manager': username}})
    return {'message':'added reportie'}



@app.post("/add_Tasks")
async def add_Tasks(Tasks : TaskModel):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("AppTask")
    row = await collection.find_one({"Task" : Tasks.Task})
    if row:
        print("Task Already Exists")
        return {'message':'Task Already Exists'}


    else:
        print("Task doesn't Exist")
        Tsk = {
            'Task': Tasks.Task,'TaskDescription' :  Tasks.TaskDescription,'username':Tasks.username,
            'Technology': Tasks.Technology,'WorkLink':Tasks.WorkLink
        }
        print(Tsk)
        dbTask = TaskInDB(**Tsk)
        response = await collection.insert_one(dbTask.dict())
        return {'message':'Task Added'}
        
@app.delete("/delete_Tasks")
async def delete_Tasks(Tasks:DeleteTask):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("AppTask")
    row = await collection.find_one({"username": Tasks.username})
    if row:
        if  row['_id'] == ObjectId(Tasks.id):
            task = TaskInDB(**row)
            await collection.delete_one(task.dict())
            return {'message':'Task Deleted'}
    else:
        return {'message':'Task doesnot exist'}

@app.put("/Update_Tasks")
async def Update_Tasks(username : str,id: str,Task:str,TaskDescription:str,WorkLink:str,Technology:str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database("ps2")
    collection = db.get_collection("AppTask")
    row = await collection.find_one({'_id':ObjectId(id)})
    if row:
        if row['username'] == username:
            raw = await collection.update_one({'_id':ObjectId(id)}, {'$set':{ {'TaskDescription': TaskDescription},{'Task': Task},
                                                                              {'WorkLink': WorkLink}, {'Technology': Technology}} })
            #raw = await collection.update_one({'_id': ObjectId(id)}, {'$set': {'Task': Task}})
            #raw = await collection.update_one({'_id':ObjectId(id)},{'$set': {'WorkLink': WorkLink}})
            #raw = await collection.update_one({'_id':ObjectId(id)}, {'$set': {'Technology': Technology}})
            #raw = await collection.update_one({'Task': Tasks.Task}, {'$set': {'createdTime': Field(default_factory=datetime.utcnow)}})
            ram = TaskInDB(**row)
            return {'message':'Task Updated'}
        else:
            return {'message':'Access Denied'}
    else:
        return {'message':'Task doesnot exist'}





@app.post("/add_users")
async def add_users(users: User):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({"username": users.username})
    if row:
        print("User Already Exists")
    else:
        print("No User Exists")
        usr = {'firstName': users.firstName, 'lastName': users.lastName, 'username': users.username, 'role': "user",
               'password': users.password,'DOB':users.DOB}

        dbuser = UserInDB(**usr)
        response = await collection.insert_one(dbuser.dict())

    return {'Message' : 'User added'}

@app.delete("/delete_user")
async def delete_user(user:str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({"username": user})
    if row:
        raw = UserInDB(**row)
        await collection.delete_one(raw.dict())
        return {'message' : 'user Deleted'}
    else:
        return {'message':'user doesnot exists'}


@app.get("/findUser")
async def findUser(username: str):
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    row = await collection.find_one({"username": username})
    if row:
        print("User Already Exists")
        usrdB = UserInDB(**row)
        return usrdB
    else:
        return "No User"


@app.get('/today_BD')
async  def today_Birthday():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("users")
    date = datetime.date.today()
    today = date.strftime("%Y/%m/%d")
    print(today)
    bd = today[5:10]
    print("bd is " + bd)
    "print(daytime.day(today))"
    "row = await collection.find_one({daytime.day('DOB'):str(today[5:10])})"

    'row = await collection.find_one({datetime.day("DOB"): str(today[5:10])})'
    row =  collection.find({})
    hbd = []
    async for user in row:
            print(user["DOB"][5:10])
            if user["DOB"][5:10] == str(today[5:10]):
                hbd.append({'names':user["username"]})
            await asyncio.sleep(1)
    print(hbd)
    return hbd


@app.get('/month_BD')
async def month_BD():
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client.get_database(MONGODB_DB_NAME)
        collection = db.get_collection("users")
        date = datetime.date.today()
        today =date.strftime("%y/%m/%d")
        month = date.strftime("%m")
        users = collection.find()
        month_bdname = []
        month_bdDate =[]
        async for user in users:
            if user['DOB'][5:7]==month and  user['DOB'][8:10]>str(date)[8:10]:
                month_bdname.append({'names': user['username']})
                month_bdDate.append({'date':user['DOB'][5:10]})

        return month_bdname,month_bdDate

@app.get('/Holidays')
async def Holidays():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database(MONGODB_DB_NAME)
    collection = db.get_collection("Holidays")
    date = datetime.date.today()
    today = date.strftime("%y/%m/%d")
    month = date.strftime("%m")
    holidays = collection.find()
    month_holidayname = []
    month_holidayDate = []
    async for holiday in holidays:
        if holiday['Date'][5:7] == month and holiday['Date'][8:10] > str(date)[8:10]:
            month_holidayname.append({'names': holiday['Name']})
            month_holidayDate.append({'date': holiday['Date']})

    return month_holidayname, month_holidayDate


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)