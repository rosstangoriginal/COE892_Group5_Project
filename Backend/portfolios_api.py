from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from decouple import config

app = FastAPI()


class Portfolio(BaseModel):
    user_id: int
    portfolio_name: str
    description: str
    creation_date: str


def mysql_connect():
    db_host = config('DB_HOST')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_database = config('DB_DATABASE')

    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )
    return db, db.cursor(dictionary=True)


@app.get("/portfolios/get_total_portfolio_value/{portfolio_id}")
async def get_total_portfolio_value(portfolio_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT AssetID, Quantity FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
    asset_ids = cursor.fetchall()

    if not asset_ids:
        raise HTTPException(status_code=404, detail="No holdings found for the given portfolio id")

    total_portfolio_value = 0
    for aid in asset_ids:
        query = "SELECT MarketPrice from Assets WHERE AssetID = %s"
        cursor.execute(query, (aid['AssetID'],))
        entry = cursor.fetchone()
        total_portfolio_value += (entry['MarketPrice'] * aid['Quantity'])

    cursor.close()
    db.close()

    return total_portfolio_value


@app.get("/portfolios/get_portfolio/{user_id}")
def get_portfolio(user_id: int):
    db, cursor = mysql_connect()

    query = "SELECT * FROM Portfolios WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    portfolio = cursor.fetchone()
    cursor.close()
    db.close()

    if portfolio:
        return portfolio
    else:
        raise HTTPException(status_code=404, detail="Portfolio of that given user id not found")


@app.post("/portfolios/create_portfolio")
def create_portfolio(portfolio: Portfolio):
    db, cursor = mysql_connect()

    query = """
    INSERT INTO Portfolios (UserID, PortfolioName, Description, CreationDate)
    VALUES (%s, %s, %s, %s)
    """
    data = (
        portfolio.user_id,
        portfolio.portfolio_name,
        portfolio.description,
        portfolio.creation_date
    )
    cursor.execute(query, data)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Portfolio created successfully."}


@app.put("/portfolios/update_portfolio/{user_id}")
def update_portfolio(user_id: int, portfolio: Portfolio):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Portfolios WHERE UserID = %s", (user_id,))
    existing_portfolio = cursor.fetchone()
    if not existing_portfolio:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Portfolio of that id not found")

    query = """
    UPDATE Portfolios
    SET UserID = %s, PortfolioName = %s, Description = %s, CreationDate = %s
    WHERE UserID = %s
    """
    update_values = (
        portfolio.user_id,
        portfolio.portfolio_name,
        portfolio.description,
        portfolio.creation_date,
        user_id
    )

    cursor.execute(query, update_values)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Portfolio updated successfully."}


@app.delete("/portfolios/delete_portfolio/{user_id}")
def delete_portfolio(user_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Portfolios WHERE UserID = %s", (user_id,))
    portfolio = cursor.fetchone()
    if not portfolio:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Portfolio of that user id not found")

    query = "DELETE FROM Portfolios WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Portfolio deleted successfully."}
