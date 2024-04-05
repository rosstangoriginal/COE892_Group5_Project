from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import date
from decouple import config

router = APIRouter()

class PortfolioPerformance(BaseModel):
    user_id: int
    portfolio_name: str
    date: date
    portfolio_value: float
    daily_change: float
    total_gain_loss: float
    
class DeletePerformanceData(BaseModel):
    user_id: int
    portfolio_name: str
    date: date
    
class tempPerformance(BaseModel):
    portfolio_ID: int
    date: date
    portfolio_value: float
    daily_change: float
    total_gain_loss: float
    
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

@router.get("/performance/get_all_performances/{user_id}")
def get_all_performances_by_user(user_id: int):
    try:
        db, cursor = mysql_connect()

        query = """
        SELECT p.* FROM Performance p
        INNER JOIN Portfolios pf ON p.PortfolioID = pf.PortfolioID
        WHERE pf.UserID = %s
        """
        cursor.execute(query, (user_id,))
        performances = cursor.fetchall()

        cursor.close()
        db.close()

        if performances:
            return performances
        else:
            raise HTTPException(status_code=404, detail="No performance records found for the given user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/performance/by_portfolioid/{portfolio_id}")
def get_performance_by_portfolioid(portfolio_id: int):
    try:
        db, cursor = mysql_connect()

        query = "SELECT * FROM Performance WHERE PortfolioID = %s ORDER BY Date ASC"
        cursor.execute(query, (portfolio_id,))
        performances = cursor.fetchall()

        cursor.close()
        db.close()

        if performances:
            return performances
        else:
            raise HTTPException(status_code=404, detail="No performance records found for the given portfolio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/performance/add_performance")
def add_performance(performance: PortfolioPerformance):
    try:
        db, cursor = mysql_connect()

        query = "SELECT PortfolioID FROM Portfolios WHERE UserID = %s AND PortfolioName = %s"
        cursor.execute(query, (performance.user_id, performance.portfolio_name))
        portfolio = cursor.fetchone()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        query = """
        INSERT INTO Performance (PortfolioID, Date, PortfolioValue, DailyChange, TotalGainLoss)
        VALUES (%s, %s, %s, %s, %s)
        """
        add_values = (
            portfolio['PortfolioID'],
            performance.date,
            performance.portfolio_value,
            performance.daily_change,
            performance.total_gain_loss,
        )
        
        cursor.execute(query, add_values)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Performance added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/performance/update_performance")
def update_performance(performance_data: PortfolioPerformance):
    try:
        db, cursor = mysql_connect()

        query = "SELECT PortfolioID FROM Portfolios WHERE UserID = %s AND PortfolioName = %s"
        cursor.execute(query, (performance_data.user_id, performance_data.portfolio_name))
        portfolio = cursor.fetchone()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        query = "SELECT * FROM Performance WHERE PortfolioID = %s AND Date = %s"
        cursor.execute(query, (portfolio['PortfolioID'], performance_data.date))
        performance = cursor.fetchone()
        
        if not performance:
            raise HTTPException(status_code=404, detail="Performance record not found")

        query = """
        UPDATE Performance
        SET PortfolioValue = %s, DailyChange = %s, TotalGainLoss = %s
        WHERE PortfolioID = %s AND Date = %s
        """
        update_values = (
            performance_data.portfolio_value,
            performance_data.daily_change,
            performance_data.total_gain_loss,
            portfolio['PortfolioID'],
            performance_data.date
        )
        
        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Performance updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/performance/delete_performance")
def delete_performance(data: DeletePerformanceData):
    try:
        db, cursor = mysql_connect()

        query = "SELECT PortfolioID FROM Portfolios WHERE UserID = %s AND PortfolioName = %s"
        cursor.execute(query, (data.user_id, data.portfolio_name))
        portfolio = cursor.fetchone()

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        query = "DELETE FROM Performance WHERE PortfolioID = %s AND Date = %s"
        cursor.execute(query, (portfolio['PortfolioID'], data.date))
        affected_rows = cursor.rowcount
        db.commit()
        cursor.close()
        db.close()

        if affected_rows == 0:
            return {"message": "No performance record found for the given date and portfolio."}
        else:
            return {"message": "Performance record deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
"""
IF WE ARE USING JUST THE BASE API'S FOR ADD, UPDATE AND DELETE
"""

@router.post("/performance/temp_add_performance")
def temp_add_performance(temp_add: tempPerformance):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Performance (PortfolioID, Date, PortfolioValue, DailyChange, TotalGainLoss)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (
            temp_add.portfolio_ID,
            temp_add.date,
            temp_add.portfolio_value,
            temp_add.daily_change,
            temp_add.total_gain_loss
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Performance created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/performance/temp_update_performance")
def temp_update_performance(temp_update: tempPerformance):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Performance WHERE PortfolioID = %s", (temp_update.portfolio_ID,))
        existing_performance = cursor.fetchone()
        if not existing_performance:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Performance not found")
        
        query = """
        UPDATE Performance
        SET Date = %s, PortfolioValue = %s, DailyChange = %s, TotalGainLoss = %s
        WHERE PortfolioID = %s
        """
        update_values = (
            temp_update.date,
            temp_update.portfolio_value,
            temp_update.daily_change,
            temp_update.total_gain_loss,
            temp_update.portfolio_ID
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Performance updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/performance/temp_delete_performance")
def temp_delete_performance(portfolio_id: int):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Performance WHERE PortfolioID = %s", (portfolio_id,))
        transaction = cursor.fetchone()
        if not transaction:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Performance not found")

        query = "DELETE FROM Performance WHERE Performance = %s"
        cursor.execute(query, (portfolio_id,))
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Performance deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))