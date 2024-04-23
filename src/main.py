from fastapi import FastAPI
from dtypes import make_response
from controllers import invoice_router

app = FastAPI()
app.include_router(invoice_router)

@app.get("/healthz")
def health_check():
    return make_response(200, "OK")