from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()


class Portfolio(BaseModel):
    portfolio_id: int
    user_id: int
    portfolio_name: str
    description: str
    creation_date: str


def mysql_connect():
    db = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    return db, db.cursor(dictionary=True)


@app.get("/portfolios/get_portfolio/{user_id}")
def get_portfolio(user_id: int):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolios/create_portfolio")
def create_portfolio(portfolio: Portfolio):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Portfolios (PortfolioID, UserID, PortfolioName, Description, CreationDate)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (
            portfolio.portfolio_id,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/portfolios/update_portfolio/{user_id}")
def update_portfolio(user_id: int, portfolio: Portfolio):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Portfolios WHERE UserID = %s", (user_id,))
        existing_portfolio = cursor.fetchone()
        if not existing_portfolio:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Portfolio of that id not found")

        query = """
        UPDATE Portfolios
        SET PortfolioID = %s, UserID = %s, PortfolioName = %s, Description = %s, CreationDate = %s
        WHERE UserID = %s
        """
        update_values = (
            portfolio.portfolio_id,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/portfolios/delete_portfolio/{user_id}")
def delete_portfolio(user_id: int):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))