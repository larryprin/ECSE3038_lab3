from datetime import datetime
import os
from fastapi import FastAPI, Body, Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
import pydantic
from pydantic import BaseModel, Field, EmailStr
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio


app = FastAPI()
origins = [
  "http://localhost:8000",
  "https://ecse3038-lab3-tester.netlify.app"

]

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)


client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://ecsebot:iYlk9QaJ9HpGjFhJ@cluster0.ntysecb.mongodb.net/?retryWrites=true&w=majority")
db = client.tank



pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str


@app.get("/profile", status_code=201)
async def get_profile():
  prof1 = await db["profile"].find_one()
  return prof1

@app.post("/profile",status_code=201)
async def create_new_profile(request: Request):
  profile_object = await request.json()
  profile_object["last_updated"]=datetime.now()

  new_profile = await db["profile"].insert_one(profile_object)
  created_profile = await db["profile"].find_one({"_id": new_profile.inserted_id})
  return created_profile


@app.get ("/data")
async def get_tanks():
  data1 = await db["tanks"].find().to_list(999)
  return data1

@app.post("/data", status_code=201)
async def create_new_tank(request: Request):
  tank_object= await request.json()

  new_tank = await db["tanks"].insert_one(tank_object)
  created_tank = await db["tanks"].find_one({"_id": new_tank.inserted_id})
  return created_tank
  

@app.patch("/data/{id}")
async def tank_update(id: str, request: Request):
  tank_object= await request.json()

  updated_tank = await db["tanks"].update_one({"_id": ObjectId(id)}, {"$set": tank_object})
  patched_tank = await db["tanks"].find_one({"_id": id})
  return patched_tank
 


@app.delete("/data/{id}",status_code=204)
async def delete_tank(id: str):
  tank_delete= await db["tanks"].find_one_and_delete({"_id": ObjectId(id)})

  if not tank_delete:
    raise HTTPException(status_code = 404, detail = "was nvr there")

