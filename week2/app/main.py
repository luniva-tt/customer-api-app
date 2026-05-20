from fastapi import FastAPI
from week2.app.routers import customer_router
from week2.app.routers import count_router


app = FastAPI(
    title="Customer API"
)

app.include_router(
    customer_router.router
)
app.include_router(
    count_router.router)


@app.get("/")
def root():
    return {
        "message": "Customer API Running"
    }