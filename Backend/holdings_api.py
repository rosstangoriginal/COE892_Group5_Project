from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()


class Holding(BaseModel):
    holding_id: int
    portfolio_id: int
    asset_id: int
    quantity: float
    purchase_price: float
    purchase_date: str


def mysql_connect():
    db = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    return db, db.cursor(dictionary=True)


@app.get("/holdings/get_holding_by_portfolio_id/{portfolio_id}")
def get_holding(portfolio_id: int):
    try:
        db, cursor = mysql_connect()

        query = "SELECT * FROM Holdings WHERE PortfolioID = %s"
        cursor.execute(query, (portfolio_id,))
        holding = cursor.fetchone()
        cursor.close()
        db.close()

        if holding:
            return holding
        else:
            raise HTTPException(status_code=404, detail="Holding of that given portfolio id not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/holdings/get_holding_by_asset_id/{asset_id}")
def get_holding(asset_id: int):
    try:
        db, cursor = mysql_connect()

        query = "SELECT * FROM Holdings WHERE AssetID = %s"
        cursor.execute(query, (asset_id,))
        holding = cursor.fetchone()
        cursor.close()
        db.close()

        if holding:
            return holding
        else:
            raise HTTPException(status_code=404, detail="Holding of that given asset id not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/holdings/create_holding")
def create_holding(holding: Holding):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Holdings (HoldingID, PortfolioID, AssetID, Quantity, PurchasePrice, PurchaseDate)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (
            holding.holding_id,
            holding.portfolio_id,
            holding.asset_id,
            holding.quantity,
            holding.purchase_price,
            holding.purchase_date
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Holding created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/holdings/update_holding_by_portfolio_id/{portfolio_id}")
def update_holding(portfolio_id: int, holding: Holding):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
        existing_holding = cursor.fetchone()
        if not existing_holding:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Holding of that portfolio id not found")

        query = """
        UPDATE Holdings
        SET HoldingID = %s, PortfolioID = %s, AssetID = %s, Quantity = %s, PurchasePrice = %s, PurchaseDate = %s
        WHERE PortfolioID = %s
        """
        update_values = (
            holding.holding_id,
            holding.portfolio_id,
            holding.asset_id,
            holding.quantity,
            holding.purchase_price,
            holding.purchase_date,
            portfolio_id
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Holding updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/holdings/update_holding_by_asset_id/{asset_id}")
def update_holding(asset_id: int, holding: Holding):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Holdings WHERE PortfolioID = %s", (asset_id,))
        existing_holding = cursor.fetchone()
        if not existing_holding:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Holding of that asset id not found")

        query = """
        UPDATE Holdings
        SET HoldingID = %s, PortfolioID = %s, AssetID = %s, Quantity = %s, PurchasePrice = %s, PurchaseDate = %s
        WHERE AssetID = %s
        """
        update_values = (
            holding.holding_id,
            holding.portfolio_id,
            holding.asset_id,
            holding.quantity,
            holding.purchase_price,
            holding.purchase_date,
            asset_id
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Holding updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/holdings/delete_holding_by_portfolio_id/{portfolio_id}")
def delete_holding(portfolio_id: int):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
        holding = cursor.fetchone()
        if not holding:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Holding of that portfolio id not found")

        query = "DELETE FROM Holdings WHERE PortfolioID = %s"
        cursor.execute(query, (portfolio_id,))
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Holding deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/holdings/delete_holding_by_asset_id/{asset_id}")
def delete_holding(asset_id: int):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Holdings WHERE AssetID = %s", (asset_id,))
        holding = cursor.fetchone()
        if not holding:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Holding of that asset id not found")

        query = "DELETE FROM Holdings WHERE AssetID = %s"
        cursor.execute(query, (asset_id,))
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Holding deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
