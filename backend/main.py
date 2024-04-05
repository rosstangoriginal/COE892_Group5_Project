from fastapi import FastAPI
from app.routers import (assets_api, users_api, portfolios_api, holdings_api, transactions_api, performance_api,
                         watchlist_api, alerts_api, dividends_api)

app = FastAPI()

app.include_router(assets_api.router)
app.include_router(users_api.router)
app.include_router(portfolios_api.router)
app.include_router(holdings_api.router)
app.include_router(transactions_api.router)
app.include_router(performance_api.router)
app.include_router(watchlist_api.router)
app.include_router(alerts_api.router)
app.include_router(dividends_api.router)
