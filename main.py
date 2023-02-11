# main.py
from fastapi import FastAPI
from routers.routes import router as item_router
from models.models import Base
from routers.routes import engine

app = FastAPI(title="My API", version="1.0")
Base.metadata.create_all(bind=engine)
app.include_router(item_router, prefix="/api")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
