from fastapi import FastAPI
from app.routers import assets_api, users_api, portfolios_api, holdings_api

app = FastAPI()

app.include_router(assets_api.router)
app.include_router(users_api.router)
app.include_router(portfolios_api.router)
app.include_router(holdings_api.router)
