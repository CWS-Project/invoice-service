from fastapi import FastAPI, Response
from dtypes import make_response
from controllers import invoice_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(invoice_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health_check(response: Response):
    return make_response(response, 200, "OK")