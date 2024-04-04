from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
import mysql.connector
from typing import Optional

app = FastAPI()

class Alerts(BaseModel):
    user_ID: int
    alert_type: str
    alert_description: str
    trigger_condition: str
    status: str
    
class AlertCriteria(BaseModel):
    user_id: int
    alert_type: str
    new_description: Optional[str] = None
    new_trigger_condition: Optional[str] = None
    new_status: Optional[str] = None

class AlertDeleteCriteria(BaseModel):
    user_id: int
    alert_type: str
    
def mysql_connect():
    db = mysql.connector.connect(
        host="your_host",
        user="your_user",
        password="your_password",
        database="your_database"
    )
    return db, db.cursor(dictionary=True)
    
@app.get("/alerts/get_alerts/{user_id}")
def get_alerts(user_id: int):
    try:
        db, cursor = mysql_connect()

        query = "SELECT * FROM Alerts WHERE UserID = %s"
        cursor.execute(query, (user_id,))
        alerts = cursor.fetchone()
        cursor.close()
        db.close()

        if alerts:
            return alerts
        else:
            raise HTTPException(status_code=404, detail="Alerts not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/alerts/create_alert")
def create_alert(alert: Alerts):
    try:
        db, cursor = mysql_connect()

        query = """
        INSERT INTO Alerts (UserID, AlertType, AlertDescription, TriggerCondition, Status)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (
            alert.user_ID,
            alert.alert_type,
            alert.alert_description,
            alert.trigger_condition,
            alert.status
        )
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()

        return {"message": "Alert created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/alerts/update_alert")
def update_alert(criteria: AlertCriteria):
    try:
        db, cursor = mysql_connect()
        updates = []
        params = []

        if criteria.new_description:
            updates.append("AlertDescription = %s")
            params.append(criteria.new_description)
        if criteria.new_trigger_condition:
            updates.append("TriggerCondition = %s")
            params.append(criteria.new_trigger_condition)
        if criteria.new_status:
            updates.append("Status = %s")
            params.append(criteria.new_status)

        if not updates:
            raise HTTPException(status_code=400, detail="No update information provided.")

        update_str = ", ".join(updates)
        params.extend([criteria.user_id, criteria.alert_type])

        query = f"UPDATE Alerts SET {update_str} WHERE UserID = %s AND AlertType = %s"
        cursor.execute(query, tuple(params))
        db.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found or no update needed.")

        cursor.close()
        db.close()

        return {"message": "Alert updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/alerts/delete_alert")
def delete_alert(criteria: AlertDeleteCriteria):
    try:
        db, cursor = mysql_connect()
        
        query = "DELETE FROM Alerts WHERE UserID = %s AND AlertType = %s"
        cursor.execute(query, (criteria.user_id, criteria.alert_type))
        db.commit()

        affected_rows = cursor.rowcount
        cursor.close()
        db.close()

        if affected_rows == 0:
            return {"message": "No alert found with the given criteria, or it has already been deleted."}
        else:
            return {"message": f"{affected_rows} alert(s) deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))