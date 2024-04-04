from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import date
from decouple import config
import traceback

app = FastAPI()

class HoldingDividend(BaseModel):
    portfolio_id: int
    asset_id: int
    dividend_amount: float
    payment_date: date
    
class DeleteDividendData(BaseModel):
    portfolio_id: int
    asset_id: int

class tempDividend(BaseModel):
    holding_id: int
    dividend_amount: float
    
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

@app.get("/dividends/get_dividend")
def get_dividend(portfolio_id: int, asset_id: int):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (portfolio_id, asset_id))
        holdings = cursor.fetchall()

        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for the given PortfolioID and AssetID")
        
        holding_ids = [holding['HoldingID'] for holding in holdings]

        dividends = []
        for pid in holding_ids:
            query = "SELECT * FROM Dividends WHERE HoldingID = %s"
            cursor.execute(query, (pid,))
            dividends.extend(cursor.fetchall())
            
        cursor.close()
        db.close()

        if dividends:
            return dividends
        else:
            raise HTTPException(status_code=404, detail="Dividend not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/dividends/create_dividend")
def add_dividend(add_dividend: HoldingDividend):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (add_dividend.portfolio_id, add_dividend.asset_id))
        holdings = cursor.fetchone()

        print(holdings)
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for the given PortfolioID and AssetID")
        
        query = """
        INSERT INTO Dividends (HoldingID, DividendAmount, PaymentDate)
        VALUES (%s, %s, %s)
        """
        data = (
            holdings['HoldingID'],
            add_dividend.dividend_amount,
            add_dividend.payment_date
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Dividend created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/dividends/update_dividend")
def update_dividend(update_dividend: HoldingDividend):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (update_dividend.portfolio_id, update_dividend.asset_id))
        holdings = cursor.fetchone()

        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for the given PortfolioID and AssetID")
        
        query = "SELECT * FROM Dividends WHERE HoldingID = %s AND PaymentDate = %s"
        cursor.execute(query, holdings['HoldingID'], update_dividend.payment_date)
        dividend = cursor.fetchone()
        
        if not dividend:
            raise HTTPException(status_code=404, detail="Dividend not found")
        
        query = """
        UPDATE Dividends
        SET DividendAmount = %s
        WHERE HoldingID = %s AND PaymentDate = %s
        """
        update_values = (
            update_dividend.dividend_amount,
            holdings['HoldingID'],
            update_dividend.payment_date
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Dividend updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/dividends/delete_dividend")
def delete_dividend(data: DeleteDividendData):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (data.portfolio_id, data.asset_id))
        holding = cursor.fetchone()

        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")

        query = "DELETE FROM Dividends WHERE HoldingID = %s"
        cursor.execute(query, (holding['HoldingID'],))
        affected_rows = cursor.rowcount
        db.commit()
        cursor.close()
        db.close()

        if affected_rows == 0:
            return {"message": "No Dividend found with the given criteria, or it has already been deleted."}
        else:
            return {"message": "Dividend deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
"""
IF WE ARE USING JUST THE BASE API'S FOR ADD, UPDATE AND DELETE
"""

@app.post("/dividends/temp_add_dividend")
def temp_add_dividend(temp_add: tempDividend):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Dividends (HoldingID, DividendAmount, PaymentDate)
        VALUES (%s, %s, %s)
        """
        data = (
            temp_add.holding_id,
            temp_add.dividend_amount,
            temp_add.payment_date
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Dividend created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/dividends/temp_update_dividend")
def temp_update_dividend(temp_update: tempDividend):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Dividends WHERE HoldingID = %s", (temp_update.holding_id,))
        existing_dividend = cursor.fetchone()
        if not existing_dividend:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Dividend not found")
        
        query = """
        UPDATE Dividends
        SET DividendAmount = %s, PaymentDate = %s
        WHERE HoldingID = %s
        """
        update_values = (
            temp_update.dividend_amount,
            temp_update.payment_date,
            temp_update.holding_id
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Dividend updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/dividends/temp_delete_dividend")
def temp_delete_dividend(holding_id: int):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Dividends WHERE HoldingID = %s", (holding_id,))
        dividend = cursor.fetchone()
        if not dividend:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Dividend not found")

        query = "DELETE FROM Dividends WHERE HoldingID = %s"
        cursor.execute(query, (holding_id,))
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Dividend deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))