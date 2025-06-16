import os
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    required_keys = ["OPEN_API_KEY", "GOOGLE_API_KEY"]
    missing = [key for key in required_keys if not os.environ.get(key)]

    if missing:
        raise RuntimeError(f"❌ Missing environment variables: {', '.join(missing)}")

    print("✅ All required environment variables are set.")

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "FastAPI is running with required API keys"}