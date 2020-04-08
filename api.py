__authors__ = "Markus Sagen, Sebastian Rollino, Nils Hedberg, Alexander Bergkvist"


from fastapi import FastAPI, File, Query, Form, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# For defining typeChecking and defining your own type checking
from pydantic import Required, BaseModel
from enum import Enum
import json

# For processing datalist and pdfs
from ast import literal_eval
import pandas as pd
import numpy as np  # RM

# For uploading files
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, List

# The NLP QA model
from cdqa.utils.filters import filter_paragraphs
from cdqa.pipeline import QAPipeline
from model import QA


# model = QA()

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
    query = await request.json()
    question = query["text"]
    print(question)
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


# TODO: Allow adding pdf to the trained model
# TODO: Allow saving multiple files on storage, works sometimes, so probably wrong way right now
# TODO: In model.py, allow combining multiple txt and csv into one
# TODO: In model.py, create folder for pdfs to load into model to enable training
# TODO: Add examples of how to use this function
@app.post("/upload_train")
async def save_uploaded_file_tmp(request: Request, file: List[UploadFile] = File(...)):
    """
    Uploads temporary file which is loadied in to the cdQA model as the data

    TODO: Add example
    """
    query = await request.form()
    tmp = query['tmp']              # Get if file only for training or also for storage from request
    upload_folder = 'data/upload'

    for f in file:
        file_object = f.file
        UPLOAD_FOLDER = open(os.path.join(upload_folder, f.filename), 'wb+')
        shutil.copyfileobj(file_object, UPLOAD_FOLDER)
        UPLOAD_FOLDER.close()
        qa.load_data(f'{upload_folder}/{f.filename}')
        if (tmp == 'true'):
            os.remove(f'{upload_folder}/{f.filename}')
    return {"msg": "file read", "files": [f.filename for f in file]}
    