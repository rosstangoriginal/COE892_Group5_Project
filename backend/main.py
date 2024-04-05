from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (assets_api, users_api, portfolios_api, holdings_api, transactions_api, performance_api,
                         watchlist_api, alerts_api, dividends_api)

app = FastAPI()

# Adding CORS middleware to allow requests to be made from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets_api.router)
app.include_router(users_api.router)
app.include_router(portfolios_api.router)
app.include_router(holdings_api.router)
app.include_router(transactions_api.router)
app.include_router(performance_api.router)
app.include_router(watchlist_api.router)
app.include_router(alerts_api.router)
app.include_router(dividends_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)