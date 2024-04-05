from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from decouple import config

router = APIRouter()


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


@router.get("/assets/get_asset/{asset_id}")
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


@router.get("/assets/get_all_assets_by_portfolio_id/{portfolio_id}")
async def get_all_assets(portfolio_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT AssetID FROM Holdings WHERE PortfolioID = %s", (portfolio_id,))
    asset_ids = cursor.fetchall()

    if not asset_ids:
        raise HTTPException(status_code=404, detail="No holdings found for the given portfolio id")

    asset_arr = []
    for aid in asset_ids:
        query = "SELECT * from Assets WHERE AssetID = %s"
        cursor.execute(query, (aid['AssetID'],))
        asset_arr.extend(cursor.fetchall())

    cursor.close()
    db.close()

    if asset_arr:
        return asset_arr
    else:
        raise HTTPException(status_code=404, detail="No assets found for the given portfolio id")


@router.post("/assets/create_asset")
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
    asset_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()

    return {"message": "Asset created successfully.", "asset_id": asset_id}


@router.put("/assets/update_asset/{asset_id}")
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


@router.delete("/assets/delete_asset/{asset_id}")
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
