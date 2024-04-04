from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from typing import Optional
from decouple import config

router = APIRouter()

class WatchlistCreate(BaseModel):
    user_ID: int
    asset_ID: int
    watchlist_name: str
    notes: Optional[str] = None
    
class WatchlistUpdate(BaseModel):
    user_ID: int
    asset_ID: int
    watchlist_name: str
    notes: str
    
class WatchlistDelete(BaseModel):
    user_ID: int
    asset_ID: int
    
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

@router.get("/watchlist/get_all_watchlist/{user_id}")
def get_all_watchlists(user_id: int):
    try:
        db, cursor = mysql_connect()

        query = """
        SELECT w.WatchlistID, w.WatchlistName, w.Notes, a.AssetName, a.AssetType, a.MarketPrice, a.Currency 
        FROM Watchlist w INNER JOIN Assets a ON w.AssetID = a.AssetID 
        WHERE w.UserID = %s
        """
        cursor.execute(query, (user_id,))
        watchlists = cursor.fetchall()
        cursor.close()
        db.close()

        if watchlists:
            return watchlists
        else:
            raise HTTPException(status_code=404, detail="No watchlist entries found for the given user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/watchlist/add_watchlist")
def add_watchlist(watchlist: WatchlistCreate):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Watchlist (UserID, AssetID, WatchlistName, Notes)
        VALUES (%s, %s, %s, %s)
        """
        data = (
            watchlist.user_ID,
            watchlist.asset_ID,
            watchlist.watchlist_name,
            watchlist.notes
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Watchlist entry added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/watchlist/update_watchlist")
def update_watchlist(update_watchlist: WatchlistUpdate):
    try:
        db, cursor = mysql_connect()

        query = """
        UPDATE Watchlist
        SET WatchlistName = %s, Notes = %s
        WHERE UserID = %s AND AssetID = %s
        """
        update_values = (
            update_watchlist.watchlist_name, 
            update_watchlist.notes,
            update_watchlist.user_ID,
            update_watchlist.asset_ID
        )
        
        cursor.execute(query, update_values)
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Watchlist entry not found")

        cursor.close()
        db.close()

        return {"message": "Watchlist updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/watchlist/delete_watchlist")
def delete_watchlist(delete_watchlist: WatchlistDelete):
    try:
        db, cursor = mysql_connect()

        query = "DELETE FROM Watchlist WHERE UserID = %s AND AssetID = %s"
        cursor.execute(query, (delete_watchlist.user_ID, delete_watchlist.asset_ID))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Watchlist entry not found or already deleted")

        cursor.close()
        db.close()

        return {"message": "Watchlist deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))