from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from decouple import config

app = FastAPI()


class Asset(BaseModel):
    asset_name: str
    asset_type: str
    description: str
    market_price: float
    currency: str


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


@app.get("/assets/get_asset/{asset_id}")
def get_asset(asset_id: int):
    db, cursor = mysql_connect()

    query = "SELECT * FROM Assets WHERE AssetID = %s"
    cursor.execute(query, (asset_id,))
    asset = cursor.fetchone()
    cursor.close()
    db.close()

    if asset:
        return asset
    else:
        raise HTTPException(status_code=404, detail="Asset of that given id not found")


@app.post("/assets/create_asset")
def create_asset(asset: Asset):
    db, cursor = mysql_connect()

    query = """
    INSERT INTO Assets (AssetName, AssetType, Description, MarketPrice, Currency)
    VALUES (%s, %s, %s, %s, %s)
    """
    data = (
        asset.asset_name,
        asset.asset_type,
        asset.description,
        asset.market_price,
        asset.currency
    )
    cursor.execute(query, data)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Asset created successfully."}


@app.put("/assets/update_asset/{asset_id}")
def update_asset(asset_id: int, asset: Asset):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Assets WHERE AssetID = %s", (asset_id,))
    existing_asset = cursor.fetchone()
    if not existing_asset:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Asset of that id not found")

    query = """
    UPDATE Assets
    SET AssetName = %s, AssetType = %s, Description = %s, MarketPrice = %s, Currency = %s
    WHERE AssetID = %s
    """
    update_values = (
        asset.asset_name,
        asset.asset_type,
        asset.description,
        asset.market_price,
        asset.currency,
        asset_id
    )

    cursor.execute(query, update_values)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Asset updated successfully."}


@app.delete("/assets/delete_asset/{asset_id}")
def delete_asset(asset_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Assets WHERE AssetID = %s", (asset_id,))
    asset = cursor.fetchone()
    if not asset:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Asset of that id not found")

    query = "DELETE FROM Assets WHERE AssetID = %s"
    cursor.execute(query, (asset_id,))
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Asset deleted successfully."}
