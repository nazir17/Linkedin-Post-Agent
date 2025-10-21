from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import post_controller
from app.configs.database import engine, Base
import asyncio

app = FastAPI(
    title="LinkedIn AI Agent",
    description="AI-powered LinkedIn content generation and posting",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    print("✅ Application shutdown")


app.include_router(post_controller.router)


@app.get("/")
async def root():
    return {
        "message": "LinkedIn AI Agent API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}