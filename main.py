# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
import os
from os import path
from typing import List, Tuple

from fastapi import (Body, Depends, FastAPI, File, Form, Header, HTTPException,
                     Path, Query, Response, UploadFile, status)
from fastapi.responses import (FileResponse, HTMLResponse, PlainTextResponse,
                               RedirectResponse)
from fastapi.security import APIKeyHeader
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


@app.post("/password-match")
async def password_match(password: str = Body(...), password_confirm: str = Body(...)):
    if password != password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password don´t match!")

    return {"message": "Password match"}


@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return """
        <html>
            <head>
                <title>
                    Hello World!
                </title>
            </head>
            <body>
                <h1>Hello World FastAPI!!!</h1>
            </body>
        </html>
    """


@app.get("/text", response_class=PlainTextResponse)
async def get_text():
    return "Hello World!"


@app.get("/redirect")
async def redirect():
    return RedirectResponse("https://www.google.com", status.HTTP_301_MOVED_PERMANENTLY)


@app.get("/cat")
async def get_cat():
    root_directory = os.path.abspath(os.path.dirname(__file__))
    cat_path = path.join(root_directory, "assets", "cat.jpg")
    return FileResponse(cat_path)


@app.get("/xml")
async def get_xml():
    content = """
        <?xml version="1.0" encoding="UTF-8"?>
            <Hello>World</Hello>
    """
    return Response(content=content,
                    media_type="application/xml",
                    status_code=status.HTTP_200_OK)


async def pagination(skip: int = Query(0, ge=0), limit: int = Query(10, ge=0)) -> Tuple[int, int]:
    return (skip, limit)


@app.get("/paginacao")
async def get_paginacao(paginacao: Tuple[int, int] = Depends(pagination)):
    skip, limit = paginacao
    return {"skip": skip, "limit": limit}


class Pagination():
    def __init__(self, maximun_limit: int = 100) -> None:
        self.maximun_limit = maximun_limit

    async def __call__(self, skip: int = Query(0, ge=0), limit: int = Query(10, ge=0)) -> Tuple[int, int]:
        capped_limit = min(self.maximun_limit, limit)
        return (skip, capped_limit)


pagination = Pagination(maximun_limit=5)


@app.get("/paginacao-nova")
async def get_paginacao_nova(paginacao: Pagination = Depends(pagination)):
    skip, limit = paginacao
    return {"skip": skip, "limit": limit}


class PaginacaoMetodos():
    def __init__(self, maximum_limit: int = 50) -> None:
        self.maximun_limit = maximum_limit

    async def skip_limit(self, skip: int = Query(0, ge=0), limit: int = Query(10, ge=0)):
        capped_limit = min(self.maximun_limit, limit)
        return (skip, capped_limit)

    async def page_size(self, page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
        capped_size = min(self.maximun_limit, size)
        return (page, capped_size)


paginacaoMetodos = PaginacaoMetodos()


@app.get("/paginacao-metodo-um")
async def get_paginacao_nova(paginacao: Pagination = Depends(paginacaoMetodos.skip_limit)):
    skip, limit = paginacao
    return {"skip": skip, "limit": limit}


@app.get("/paginacao-metodo-dois")
async def get_paginacao_nova(paginacao: Pagination = Depends(paginacaoMetodos.page_size)):
    page, size = paginacao
    return {"page": page, "size": size}

API_TOKEN = "caldara"

api_key_header = APIKeyHeader(name="Token")


@app.get("/rota-protegida")
async def rota_protegida(token: str = Depends(api_key_header)):
    if token != API_TOKEN:
        HTTPException(status=status.HTTP_403_FORBIDDEN)
    return {"hello": "world"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True, workers=1)
