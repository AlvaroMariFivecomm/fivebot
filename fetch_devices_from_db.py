import mysql.connector
from typing import List

from device import Device


def fetch_devices_from_db() -> List[Device]:
    db_config = {
        'user': 'root',
        'password': 'Fivecomm',
        'host': 'localhost', 
        'port': 3307,
        'database': 'narrow_db'
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
                DEVICE_PROPERTIES d
            LEFT JOIN 
                COVERAGE c ON d.id = c.device_id
                AND c.timestamp = (
                    SELECT 
                        MAX(c2.timestamp)
                    FROM 
                        COVERAGE c2
                    WHERE 
                        c2.device_id = c.device_id
                )
            WHERE
                c.cid IS NOT NULL;

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
