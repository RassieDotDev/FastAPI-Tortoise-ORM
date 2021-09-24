from fastapi import FastAPI

from app.database.database import init_db
from app.routers import trip, users, utilities

app = FastAPI()

app.include_router(users.router)
app.include_router(utilities.router)


@app.on_event("startup")
async def startup_event():
    print("INITIALISING DATABASE")
    init_db(app)
