__authors__ = "Markus Sagen, Sebastian Rollino, Nils Hedberg, Alexander Bergkvist"
import sys
sys.path.append(
    "/home/alex/Desktop/IT/Surmize/summarization/bertabs")
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, Query, Form, UploadFile, Request, HTTPException
from pydantic import Required, BaseModel
from enum import Enum
import json
from ast import literal_eval
import pandas as pd
import numpy as np  # RM
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, List
from cdqa.utils.filters import filter_paragraphs
from cdqa.pipeline import QAPipeline
from model import QA
import summarization.bertabs.run_summarization as summarizer

from summarization.bertabs.Utility.clean_directories import clean_directories
from summarization.bertabs.Utility.sum_joiner import sum_joiner
from summarization.bertabs.Utility.text_splitter import text_splitter
import glob



# For defining typeChecking and defining your own type checking

# For processing datalist and pdfs

# For uploading files

# The NLP QA model

# Set user id
from uuid import UUID, uuid4
import base64


""" UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS """


# Model
qa = QA()


# API
app = FastAPI(
    title="Surmize",
    description="The service to gain insight and understanding in text, documents and more",
    version="0.0.1"
)
origins = [
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_folder = "data/"


# Empty request exception
class EmptyException(Exception):
    def __init__(self, query: str):
        self.name = "'Emtpy'"
        self.query = f"'{query}'"


# Return QA prediction from model


async def QA_predict_to_json(question: str) -> json:
    """
    Returns the prediction and context to a question as json
    """
    if question == "":
        raise EmptyException(question)

    answer, context, = qa.predict(question)
    return {
        "answer":   answer,
        "context":  context
    }


# Define asyncronous error handling
@app.exception_handler(EmptyException)
async def empty_exception_handler(request: Request, e: EmptyException):
    return JSONResponse(
        status_code=418,
        content={"message": f"The sent request {e.query} can not be {e.name}"}
    )


@app.get("/")
async def lol():
    return {"msg": "Hello World!"}


# Test model from text field
# TODO: Add headers for authentication and for internal compnents 'JWT' instead
@app.post("/api")
async def ask_question(request: Request):
    """
    Example:
    >>> curl -X POST http://localhost:5000/api -d '{"text": "Hello World"}' -H "Accept: application/json" -H "Content-type: application/json"
    """
    print("IM HERE")
    query = await request.json()
    question = query["text"]
    print(question)
    
    # Add support for authorization in QA frontend
    #user = request.headers["authorization"]
    return await QA_predict_to_json(question=question)


@app.get("/api")
async def ask_question_directly(question: str):
    """
    Returns most likely answer to the question, given the
    context of the document/(s)

    Parameters
    ----------
    **question**: str
        A question to find the most likely answer to.
        The QA model computes a score of (WHAT IST THE SCORE?) TODO:

    **n_estimators**: int or None (default None)
        The number of predictions to return. The standard, None returns only one best prediction

    **retriver_score_weight**: float (default: 0.35)
        The weight if the retriver score used in the prediction

    **return_all_preds**: boolean (default: False)
        If the API should return all predictions made by the QA reader or not

    Returns
    -------
    prediction as a tuple, if return_all_preds is False
    List of dictionaries with all predicted answers from QA reader, if return_all_preds is True

    Example
    --------
    >>> curl -X POST "http://localhost:5000/api?question=What%20is%20Paribas%20Partners%20earnings%3F" -H  "accept: application/json"
    """
    return await QA_predict_to_json(question=question)




# TODO: Allow saving multiple files on storage, works sometimes, so probably wrong way right now
# TODO: Add examples of how to use this function
@app.post("/upload_train")
async def upload_file(request: Request, file: List[UploadFile] = File(...)):
    """
    Uploads temporary file which is loadied in to the cdQA model as the data

    TODO: Add example
    """
    query = await request.form()
    user = request.headers["authorization"]
    upload_folder = f'data/uploaded/{user}/text/'
    summary_folder = f'data/uploaded/{user}/summary/'

    # Create folder to upload to
    if not os.path.exists(upload_folder) and user != 'null':
        os.makedirs(upload_folder)
        os.makedirs(summary_folder)

    for f in file:
        file_object = f.file
        file_name = f.filename
        UPLOAD_FOLDER = open(os.path.join(upload_folder, file_name), 'wb+')
        shutil.copyfileobj(file_object, UPLOAD_FOLDER)
        UPLOAD_FOLDER.close()
        file_path = f"{upload_folder}/{file_name}"
        qa.load_data(filepath=file_path, filename=file_name, path=upload_folder)
        print(upload_folder)


    ################################################## Summariser
    # Please note that data/uploaded/{user}/summary and data/uploaded/{user}/text are created above, (line 181-183)
    # this must be done before this section is run!

    USER_DATA_FOLDER = "data/uploaded/" + user + "/text/"
    TMP_SPLIT_DATA_FOLDER = "data/pending/" + user + "/stories_split/"
    TMP_SPLIT_SUMMARY = "data/pending/" + user + "/summaries_split/"
    COMPLETE_SUMMARY = "data/uploaded/" + user + "/summary/"

    os.makedirs(TMP_SPLIT_DATA_FOLDER)
    os.makedirs(TMP_SPLIT_SUMMARY)


    #clean_directories([TMP_SPLIT_DATA_FOLDER,TMP_SPLIT_SUMMARY]) #No longer necessary if we remove all folders?
    files_and_sizes, name_of_files = text_splitter(USER_DATA_FOLDER, TMP_SPLIT_DATA_FOLDER, 30) #TODO SE TILL ATT BARA DOM NYA SKJUTSAS HIT! Nu tas allt som ligger i uploaded (potentiellt gamla uppladdningar) med!

    #Run summarizer
    summarizer.main(TMP_SPLIT_DATA_FOLDER, TMP_SPLIT_SUMMARY, 8, 0.75, 50, 200)

    sum_joiner(TMP_SPLIT_SUMMARY,COMPLETE_SUMMARY,files_and_sizes, name_of_files)

    #Gather and send back summaries
    summaries = []
    for name in name_of_files:
        with open(COMPLETE_SUMMARY + name.split(".")[0] + "_summary.txt", 'r') as f:
            if f.mode == 'r':
                summaries.append(f.read())

    shutil.rmtree(f'data/pending/{user}')
    ##################################################

    return {"msg": "file successfully read", "files": [f.filename for f in file],
            "sum": ("#"*60).join(summaries)}


@app.get("/token")
def get_token(request: Request):
    token = str(uuid4())
    # URL and Filename Safe Base64 Encoding
    urlSafeEncodedBytes = base64.urlsafe_b64encode(token.encode("utf-8"))
    safeToken = str(urlSafeEncodedBytes, "utf-8")
    return {"token": safeToken}


@app.post("/getfiles")
async def send_files(request:Request):
    data = await request.json()
    user = data['user']
    files = glob.glob(f'data/uploaded/{user}/text/*.txt')
    uploaded_files= []
    for f in files:
        path= f.split("/")
        f= path[len(path) -1]
        uploaded_files.append(f)
    print(uploaded_files)
    
    return {"files":uploaded_files}

@app.post("/show_file")
async def show_file(request:Request):
    data= await request.json()
    user = data['user']
    f= data['file']
    f = open(f'data/uploaded/{user}/text/{f[0]}', 'r')
    if f.mode == 'r':
        contents = f.read()
        f.close()
        print(contents)
        return {"content":contents}
    return {"msg":"HMMM"}

