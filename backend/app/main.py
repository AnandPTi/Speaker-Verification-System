import json
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from app.utils import *
from langchain_community.callbacks import get_openai_callback
import os
import logging
from databases import Database
from dotenv import load_dotenv
import pinecone
from databases import Database
from app.utils import *
import datetime
from langchain.docstore.document import Document
import asyncio


    
class UserQuery(BaseModel):
    query: str


class DateRange(BaseModel):
    dateRange: Optional[List] = None

    class Config:
        schema_extra = {
            "example": {
            }
        }





# Add this at the beginning of your script
logging.basicConfig(level=logging.DEBUG)
load_dotenv()


index_name = os.environ.get("index_name")


pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"])

if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, metric='cosine', dimension=1536)

DATABASE_URL = f"postgresql://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@{os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}"
database = Database(DATABASE_URL)
database = Database(DATABASE_URL)        


index_name = os.environ.get("index_name")


app = FastAPI(title="DrQA backend API", docs_url="/docs")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def create_tables():
    async with database.transaction():
        await database.execute('''
            CREATE TABLE IF NOT EXISTS veteran_data (
                patient_id VARCHAR,
                transcription TEXT NOT NULL,
                result JSONB NOT NULL
            )
        ''')



@app.on_event("startup")
async def startup_event():
    await database.connect()
    await create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()


async def save_file_data(patient_id, transcription, result):
    async with database.transaction():
        await database.execute("INSERT INTO veteran_data (patient_id, transcription, result) VALUES (:patient_id, :transcription, :result)", values={"patient_id": patient_id, "transcription": transcription,"result": json.dumps(result)})


async def check_and_update(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                await check_and_update(value)
            elif isinstance(value, list):
                await asyncio.gather(*(check_and_update(item) for item in value))
            elif value == "":
                data[key] = "Not discussed by doctor"
    elif isinstance(data, list):
        await asyncio.gather(*(check_and_update(item) for item in data if isinstance(item, dict) or isinstance(item, list)))
    return data


@app.post("/upload-files")
async def upload_file(req: Request,
                      ):
    transcription =(await req.json())["transcription"]
    secret_key = (await req.json())["secret_key"]
    patient_id = (await req.json())["patient_id"]
    print("Transcription: ", transcription)
    
    try :
        if secret_key == os.environ.get("secret_key"):
            print("Secret Key Matched")
            result = []
            docs = []
            data = []
            docs.append(Document(page_content=transcription, metadata={"source": "audio_file",'date': datetime.date.today().strftime('%Y-%m-%d')})) 
            with get_openai_callback() as callback:
                data = await get_doc_data(docs) 
                result = await check_and_update(data)
                print("Result Generated Successfull")
                print("Result: ", result)
                await save_file_data(patient_id, transcription, result)
                print("Data saved successfully to database...")
                return JSONResponse(content=result, status_code=200)
            
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as ex:
        logging.error(f"Error processing file: {str(ex)}")
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
