from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import date
from typing import Optional
from decouple import config

router = APIRouter()

class HoldingTransaction(BaseModel):
    portfolio_id: int
    asset_id: int
    transaction_type: str
    quantity: float
    transaction_price: float
    transaction_date: date
    
class DeleteTransactionData(BaseModel):
    portfolio_id: int
    asset_id: str
    date: date
    
class tempTransaction(BaseModel):
    holding_ID: Optional[int] = None
    transaction_type: str
    quantity: float
    transaction_price: float
    transaction_date: str
    
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

@router.get("/transaction/get_all_transactions")
def get_all_transactions(portfolio_id: int):
    try:
        db, cursor = mysql_connect()
        
        query = """
        SELECT t.* FROM Transactions t
        JOIN Holdings h ON t.HoldingID = h.HoldingID
        WHERE h.PortfolioID = %s
        """
        cursor.execute(query, (portfolio_id,))
        transactions = cursor.fetchall()

        cursor.close()
        db.close()

        if transactions:
            return transactions
        else:
            raise HTTPException(status_code=404, detail="No transactions found for the given holdings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/add_transaction")
def add_transaction(add_transaction: HoldingTransaction):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (add_transaction.portfolio_id, add_transaction.asset_id))
        holding = cursor.fetchone()
        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")

        query = """
        INSERT INTO Transactions (HoldingID, TransactionType, Quantity, TransactionPrice, TransactionDate) 
        VALUES (%s, %s, %s, %s, %s)
        """
        add_values = (
            holding['HoldingID'],
            add_transaction.transaction_type,
            add_transaction.quantity,
            add_transaction.transaction_price,
            add_transaction.transaction_date,
        )
        
        cursor.execute(query, add_values)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Transaction added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/transaction/update_transaction")
def update_transaction(update_transaction: HoldingTransaction):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (update_transaction.portfolio_id, update_transaction.asset_id))
        holding = cursor.fetchone()
        
        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        query = "SELECT * FROM Transactions WHERE HoldingID = %s AND TransactionDate = %s"
        cursor.execute(query, (holding['HoldingID'], update_transaction.transaction_date))
        transaction = cursor.fetchone()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        query = """
        UPDATE Transactions
        SET TransactionType = %s, Quantity = %s, TransactionPrice = %s
        WHERE HoldingID = %s AND TransactionDate = %s
        """
        update_values = (
            update_transaction.transaction_type,
            update_transaction.quantity,
            update_transaction.transaction_price,
            holding['HoldingID'],
            update_transaction.transaction_date
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Transaction updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/transaction/delete_transaction")
def delete_transaction(delete_transaction: DeleteTransactionData):
    try:
        db, cursor = mysql_connect()

        query = "SELECT HoldingID FROM Holdings WHERE PortfolioID = %s AND AssetID = %s"
        cursor.execute(query, (delete_transaction.portfolio_id, delete_transaction.asset_id))
        holding = cursor.fetchone()

        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")

        query = "DELETE FROM Transactions WHERE HoldingID = %s AND TransactionDate = %s"
        cursor.execute(query, (holding['HoldingID'], delete_transaction.date))
        affected_rows = cursor.rowcount
        db.commit()
        cursor.close()
        db.close()

        if affected_rows == 0:
            return {"message": "No transaction found with the given criteria, or it has already been deleted."}
        else:
            return {"message": "Transaction deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions/get_user_transactions/{user_id}")
def get_user_transactions(user_id: int):
    try:
        db, cursor = mysql_connect()

        query = """
        SELECT 
            Transactions.TransactionID,
            Transactions.TransactionType,
            Transactions.Quantity,
            Transactions.TransactionPrice,
            Transactions.TransactionDate,
            Assets.AssetName
        FROM 
            Transactions
        INNER JOIN 
            Holdings ON Transactions.HoldingID = Holdings.HoldingID
        INNER JOIN 
            Assets ON Holdings.AssetID = Assets.AssetID
        INNER JOIN 
            Portfolios ON Holdings.PortfolioID = Portfolios.PortfolioID
        WHERE
            Portfolios.UserID = %s;
        """
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        cursor.close()
        db.close()

        if transactions:
            return transactions
        else:
            raise HTTPException(status_code=404, detail="No transactions found for the specified user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/transactions/get_last_five_transactions/{user_id}")
def get_last_five_transactions(user_id: int):
    try:
        db, cursor = mysql_connect()

        query = """
        SELECT 
            t.TransactionID,
            t.TransactionType,
            t.Quantity,
            t.TransactionPrice,
            t.TransactionDate,
            a.AssetName
        FROM 
            Transactions t
        INNER JOIN 
            Holdings h ON t.HoldingID = h.HoldingID
        INNER JOIN 
            Assets a ON h.AssetID = a.AssetID
        INNER JOIN 
            Portfolios p ON h.PortfolioID = p.PortfolioID
        WHERE
            p.UserID = %s
        ORDER BY 
            t.TransactionDate DESC, t.TransactionID DESC
        LIMIT 5;
        """
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        cursor.close()
        db.close()

        if transactions:
            return transactions
        else:
            raise HTTPException(status_code=404, detail="No transactions found for the specified user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
IF WE ARE USING JUST THE BASE API'S FOR ADD, UPDATE AND DELETE
"""

@router.post("/transaction/temp_add_transaction")
def temp_add_transaction(temp_add: tempTransaction):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Transactions (HoldingID, TransactionType, Quantity, TransactionPrice, TransactionDate)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (
            temp_add.holding_ID,
            temp_add.transaction_type,
            temp_add.quantity,
            temp_add.transaction_price,
            temp_add.transaction_date
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Transaction created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/transaction/temp_update_transaction/{holding_id}")
def temp_update_transaction(holding_id: int, temp_update: tempTransaction):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Transactions WHERE HoldingID = %s", (holding_id,))
        existing_transactions = cursor.fetchone()
        if not existing_transactions:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        query = """
        UPDATE Transactions
        SET HoldingID = %s, TransactionType = %s, Quantity = %s, TransactionPrice = %s, TransactionDate = %s
        WHERE HoldingID = %s
        """
        update_values = (
            temp_update.holding_ID,
            temp_update.transaction_type,
            temp_update.quantity,
            temp_update.transaction_price,
            temp_update.transaction_date,
            holding_id
        )

        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "Transaction updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/transaction/temp_delete_transaction/{holding_id}")
def temp_delete_transaction(holding_id: int):
    try:
        db, cursor = mysql_connect()

        cursor.execute("SELECT * FROM Transactions WHERE HoldingID = %s", (holding_id,))
        transaction = cursor.fetchone()
        if not transaction:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail="Transaction not found")

        query = "DELETE FROM Transactions WHERE HoldingID = %s"
        cursor.execute(query, (holding_id,))
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Transaction deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))