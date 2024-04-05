from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from decouple import config

router = APIRouter()


class Holding(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
    purchase_price: float
    purchase_date: str


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


@router.get("/holdings/get_holding_by_portfolio_id/{portfolio_id}")
async def get_holding(portfolio_id: int):
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


@router.get("/holdings/get_all_holdings_by_portfolio_id/{portfolio_id}")
async def get_all_holdings(portfolio_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
    holdings_arr = cursor.fetchall()

    cursor.close()
    db.close()

    if holdings_arr:
        return holdings_arr
    else:
        raise HTTPException(status_code=404, detail="No holdings found for the given portfolio id")


@router.get("/holdings/get_holding_by_asset_id/{asset_id}")
def get_holding(asset_id: int):
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


@router.post("/holdings/create_holding")
def create_holding(holding: Holding):
    db, cursor = mysql_connect()

    query = """
    INSERT INTO Holdings (PortfolioID, AssetID, Quantity, PurchasePrice, PurchaseDate)
    VALUES (%s, %s, %s, %s, %s)
    """
    data = (
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


@router.put("/holdings/update_holding_by_portfolio_id/{portfolio_id}")
def update_holding(portfolio_id: int, holding: Holding):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
    existing_holding = cursor.fetchone()
    if not existing_holding:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Holding of that portfolio id not found")
    query = """
    UPDATE Holdings
    SET PortfolioID = %s, AssetID = %s, Quantity = %s, PurchasePrice = %s, PurchaseDate = %s
    WHERE PortfolioID = %s
    """

    update_values = (
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


@router.put("/holdings/update_holding_by_asset_id/{asset_id}")
def update_holding(asset_id: int, holding: Holding):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Holdings WHERE AssetID = %s", (asset_id,))
    existing_holding = cursor.fetchone()
    if not existing_holding:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Holding of that asset id not found")

    query = """
    UPDATE Holdings
    SET PortfolioID = %s, AssetID = %s, Quantity = %s, PurchasePrice = %s, PurchaseDate = %s
    WHERE AssetID = %s
    """
    update_values = (
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


@router.delete("/holdings/delete_holding_by_portfolio_id/{portfolio_id}")
def delete_holding(portfolio_id: int):
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


@router.delete("/holdings/delete_holding_by_asset_id/{asset_id}")
def delete_holding(asset_id: int):
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
