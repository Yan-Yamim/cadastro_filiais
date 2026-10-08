from http import HTTPStatus

from fastapi import FastAPI

from cadastro_filiados.views import router

app = FastAPI()

app.include_router(router)

@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World'}