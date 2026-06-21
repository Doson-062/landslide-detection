import os
import sys
from dotenv import load_dotenv

load_dotenv(".env")

from app.database import SessionLocal
from app.models import Sensor, SensorData, Alert, Threshold

def main():
    db = SessionLocal()
    try:
        print("--- THRESHOLDS ---")
        thres = db.query(Threshold).all()
        for t in thres:
            print(f"ID: {t.id} | Nghieng Warn/Danger: {t.nghieng_warn}/{t.nghieng_danger} | Rung: {t.rung_warn}/{t.rung_danger} | Mua: {t.mua_warn}/{t.mua_danger}")
        
        print("\n--- SENSORS ---")
        sensors = db.query(Sensor).all()
        for s in sensors:
            print(f"ID: {s.id} | Name: {s.name} | Location: {s.location} | Active: {s.is_active}")
            
        print("\n--- LATEST 10 SENSOR DATA ---")
        data = db.query(SensorData).order_by(SensorData.id.desc()).limit(10).all()
        for d in data:
            print(f"ID: {d.id} | Sensor: {d.sensor_id} | Nghieng: {d.do_nghieng} | Rung: {d.do_rung} | Mua: {d.luong_mua} | Time: {d.timestamp}")
            
        print("\n--- LATEST 10 ALERTS ---")
        alerts = db.query(Alert).order_by(Alert.id.desc()).limit(10).all()
        for a in alerts:
            print(f"ID: {a.id} | Sensor: {a.sensor_id} | Level: {a.level} | Msg: {a.message} | Time: {a.timestamp} | Resolved: {a.is_resolved}")
            
    except Exception as e:
        print("Error connecting to DB or querying:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
