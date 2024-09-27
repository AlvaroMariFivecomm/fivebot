import mysql.connector
from typing import List

from optimizer.device import Device

def fetch_devices_from_db() -> List[Device]:
    db_config = {
        'user': 'root',
        'password': 'Fivecomm',
        'host': '172.17.0.2', 
        'port': 3306,
        'database': 'wiot_db'
    }

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                d.sn,
                d.imei,
                d.report_time,
                c.cid
            FROM 
                DEVICE d
            LEFT JOIN 
                (
                    SELECT 
                        device_id,
                        cid,
                        MAX(timestamp) AS latest_timestamp
                    FROM 
                        COVERAGE
                    GROUP BY 
                        device_id
                ) c ON d.id = c.device_id
            WHERE
                c.cid IS NOT NULL 
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        return [Device(row['sn'], row['imei'], row['report_time'], row['cid']) for row in rows]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()
