# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

from typing import List

from fastapi import Body, FastAPI, File, Form, Header, Path, Query, UploadFile
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


app = FastAPI()


@app.get("/index")
async def index():
    return {"msg": "Olá FastAPI"}


@app.get("/users")
async def get_user(page: int = Query(1, gt=0),
                   size: int = Query(10, le=100)):
    return {"page": page, "size": size}


@app.get("/users/{id}")
async def get_user_by_id(id: int = Path(..., ge=1)):
    return {"id": id}


@app.get("/licence-plates/{licence}")
async def get_licence_plates(licence: str = Path(..., regex=r"^\w{2}-\d{3}-\w{2}$", title="Licença", description="Parâmetro de licença")):
    return {"licence": licence}


@app.post("/users")
# async def create_user(name: str = Body(...), age: int = Body(...)):
async def create_user(user: User):
    return user


@app.post("/users/form")
async def create_user_form(name: str = Form(...), age: int = Form(...)):
    return {"name": name, "age": age}


@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {"file_name": file.filename, "content_type": file.content_type}


@app.post("/files")
async def upload_files(files: List[UploadFile] = File(...)):
    return [{"file_name": file.filename, "content_type": file.content_type} for file in files]


@app.get("/")
async def get_header(hello: str = Header(...)):
    return {"hello": hello}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True)
