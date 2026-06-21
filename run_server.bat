@echo off
cd /d "%~dp0"
title Landslide Detection System - Web Server + MQTT
echo ===================================================
echo     KHOI DONG HE THONG CANH BAO SAT LO
echo     FastAPI + MQTT Broker + Grafana (Docker)
echo ===================================================
echo.

:: ==== BUOC 1: Khoi dong Docker Containers ====
echo [1/3] Dang khoi dong MQTT Broker (Mosquitto)...
docker start mosquitto 2>nul || (
    echo     Chua co container mosquitto, dang xoa cai cu va tao moi...
    docker rm -f mosquitto 2>nul
    docker run -d --name mosquitto -p 1883:1883 -p 9001:9001 -v "%~dp0mosquitto\mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto:2
)

echo [2/3] Dang khoi dong Grafana Dashboard...
docker start grafana 2>nul || (
    echo     Chua co container grafana, dang tao moi...
    docker run -d -p 3000:3000 --name=grafana -e "GF_SECURITY_ADMIN_PASSWORD=admin123" -e "GF_SECURITY_ALLOW_EMBEDDING=true" -e "GF_AUTH_ANONYMOUS_ENABLED=true" -e "GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer" grafana/grafana-oss
)

echo.
echo [3/3] Dang khoi dong FastAPI Server tai cong 8000...
echo      (MQTT Subscriber se tu dong bat khi Server khoi dong)
echo.

:: Mo trinh duyet sau 2 giay
start /b cmd /c "timeout /t 2 >nul && start http://127.0.0.1:8000"

:: Mo san Simulator o mot cua so khac (de tranh bi ket boi uvicorn)
start "Simulator" cmd /k "timeout /t 3 >nul && python simulator/simulate.py"

echo Nhan Ctrl+C de dung may chu.
echo.

SELECT 
  s.id AS sensor_id,
  s.name AS name,
  s.latitude AS latitude,
  s.longitude AS longitude,
  COALESCE(sd.do_nghieng, 0) AS do_nghieng,
  COALESCE(sd.do_rung, 0) AS do_rung,
  COALESCE(sd.luong_mua, 0) AS luong_mua,
  COALESCE(sd.timestamp, NOW()) AS time,
  CASE
    WHEN COALESCE(sd.do_nghieng, 0) >= COALESCE(t.nghieng_danger, 20.0) 
      OR COALESCE(sd.do_rung, 0) >= COALESCE(t.rung_danger, 6.0) 
      OR COALESCE(sd.luong_mua, 0) >= COALESCE(t.mua_danger, 60.0) THEN 3
    WHEN COALESCE(sd.do_nghieng, 0) >= COALESCE(t.nghieng_warn, 10.0) 
      OR COALESCE(sd.do_rung, 0) >= COALESCE(t.rung_warn, 3.0) 
      OR COALESCE(sd.luong_mua, 0) >= COALESCE(t.mua_warn, 30.0) THEN 2
    ELSE 1
  END AS alert_level
FROM sensors s
LEFT JOIN (
  SELECT * FROM thresholds ORDER BY id ASC LIMIT 1
) t ON true
LEFT JOIN (
  -- Lấy bản ghi mới nhất của từng trạm
  SELECT DISTINCT ON (sensor_id) 
    sensor_id, do_nghieng, do_rung, luong_mua, timestamp
  FROM sensor_data
  ORDER BY sensor_id, timestamp DESC
) sd ON s.id = sd.sensor_id;


uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
python simulator/simulate.py

pause
