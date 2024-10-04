from db_connector import DBConnector
import csv
from datetime import datetime, timedelta

class Mejora:
    def __init__(self, host, database, user, password, port):
        """Inicializa la conexión a la base de datos utilizando DBConnector."""
        self.db = DBConnector(host, database, user, password, port)

    def conectar(self):
        """Conectar a la base de datos."""
        self.db.conectar()

    def desconectar(self):
        """Cerrar la conexión a la base de datos."""
        self.db.cerrar_conexion()

    def distribucion_actual(self):
        """Mostrar la distribución actual de report times"""
        consulta = """SELECT 
            COALESCE(a.hour, b.hour) AS hour,
            COALESCE(a.count, 0) AS total
        FROM (
            SELECT
                SUBSTRING(dp.report_time, 1, 2) AS hour,
                COUNT(*) AS count
            FROM narrow_db.DEVICE_PROPERTIES dp
            WHERE dp.fw != ''
            GROUP BY hour
        ) AS a
        LEFT JOIN (
            SELECT
                HOUR(dp.last_mssg_send) AS hour,
                COUNT(*) AS count
            FROM narrow_db.DEVICE_PROPERTIES dp
            WHERE DATE(dp.last_mssg_send) = CURDATE()
            AND dp.fw != ''
            GROUP BY hour
        ) AS b
        ON a.hour = b.hour
        ORDER BY hour;
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados
    
    def hubs_enviados(self):
        """Mostrar los hubs que han comunicado"""
        consulta = """SELECT 
            dp.id, dp.sn, dp.last_mssg_send
        FROM 
            DEVICE_PROPERTIES dp
        WHERE
            DATE(dp.last_mssg_send) = CURDATE()
        """
        resultados = self.db.ejecutar_consulta(consulta)
        
        # Obtener la fecha actual para usarla en el nombre del archivo
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Crear el nombre del archivo con la fecha de ejecución
        filename = f"devices_{current_date}.csv"

         # Guardar los resultados en un archivo CSV
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Escribir la cabecera del CSV
            writer.writerow(['ID', 'DEVICE_PROPERTIESID', 'Last Message Sent'])
            
            # Escribir cada fila con los resultados
            for id, sn, last_mssg_send in resultados:
                writer.writerow([id, sn, last_mssg_send])

        return resultados
    
    def conflictos_report_time(self, hour):
        """Dispositivos cuyos reportes están todos dentro de 5 minutos para una hora específica"""
        consulta = f"""SELECT DISTINCT dp1.sn, c1.CID, dp1.report_time
            FROM DEVICE_PROPERTIES dp1
            JOIN COVERAGE c1 ON c1.device_id = dp1.id
            WHERE DATE(c1.`timestamp`) = DATE(NOW() - INTERVAL 1 DAY)
            AND SUBSTRING(dp1.report_time, 1, 2) = '{hour:02d}'
            AND (c1.CID, dp1.report_time) IN (
                SELECT c2.CID, dp2.report_time
                FROM DEVICE_PROPERTIES dp2
                JOIN COVERAGE c2 ON c2.device_id = dp2.id
                WHERE DATE(c2.`timestamp`) = DATE(NOW() - INTERVAL 1 DAY)
                GROUP BY c2.CID, dp2.report_time
                HAVING COUNT(DISTINCT dp2.id) > 1
            )
            ORDER BY dp1.report_time;
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados
    
    def generar_nuevo_report_time(report_time, times_usados):
        """Generar un nuevo report_time que no esté en la lista de tiempos usados
        y tenga al menos 3 minutos de diferencia con los tiempos existentes.
        """
        # Convertir el report_time en un objeto de tipo datetime (solo tiempo, sin fecha)
        hora_actual = datetime.strptime(report_time, '%H:%M').replace(minute=0)

        # Aumentar el tiempo en 3 minutos hasta encontrar un tiempo que cumpla con la condición
        while True:
            # Aumentar en 3 minutos
            hora_actual += timedelta(minutes=3)

            # Formatear el nuevo tiempo a 'HH:MM'
            nuevo_time = hora_actual.strftime('%H:%M')

            # Comprobar si la diferencia con todos los tiempos en `times_usados` es de al menos 3 minutos
            conflict = False
            for used_time in times_usados:
                used_hora = datetime.strptime(used_time, '%H:%M')
                diferencia = abs((hora_actual - used_hora).total_seconds()) / 60

                if diferencia < 3:  # Si la diferencia es menor que 3 minutos, marcar conflicto
                    conflict = True
                    break

            # Si no hay conflictos, devolver el nuevo tiempo
            if not conflict:
                return nuevo_time
    
    def resolver_conflictos_report_time_db(self,hubs_report_conflictos):
        """
        Resolver los conflictos de report_time dentro de la misma celda y preguntar al usuario
        antes de realizar los cambios.
        """
        cambios_propuestos = []

        conflictos_por_cid = {}
        for sn, cid, report_time in hubs_report_conflictos:
            if cid not in conflictos_por_cid:
                conflictos_por_cid[cid] = []
            conflictos_por_cid[cid].append((sn, report_time))
        
        # Recorrer los conflictos agrupados por `CID`
        for cid, dispositivos in conflictos_por_cid.items():
            # Consultar todos los report_time de la misma celda (CID) para evitar conflictos
            consulta = f"""SELECT report_time 
            FROM DEVICE_PROPERTIES dp 
            JOIN COVERAGE c ON c.device_id = dp.id 
            WHERE c.CID = '{cid}'
            """
            resultados = self.db.ejecutar_consulta(consulta)
            
            # Extraer los report_time ya usados en esa celda (CID)
            times_usados = [resultado[0] for resultado in resultados]            
            # Recorrer los dispositivos en conflicto dentro de la misma celda
            for sn, report_time in dispositivos:
                # Generar un nuevo report_time que no tenga conflictos
                nuevo_report_time = Mejora.generar_nuevo_report_time(report_time, times_usados)
                
                # Agregar el nuevo `report_time` a la lista de tiempos usados para que no se repita
                times_usados.append(nuevo_report_time)

                # Agregar el cambio propuesto a la lista
                cambios_propuestos.append((sn, cid, report_time, nuevo_report_time))

        # Mostrar los cambios propuestos
        if cambios_propuestos:
            print("\n📋 Cambios propuestos:")
            for sn, cid, old_time, new_time in cambios_propuestos:
                print(f"Dispositivo {sn} (CID: {cid}): Cambiar {old_time} a {new_time}")

            # Preguntar al usuario si desea aplicar los cambios
            confirmacion = input("¿Deseas realizar estos cambios en la base de datos? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                # Si el usuario acepta, realizar los cambios
                for sn, cid, old_time, new_time in cambios_propuestos:
                    consulta_update = f"""UPDATE DEVICE_PROPERTIES dp
                    JOIN COVERAGE c ON c.device_id = dp.id
                    SET dp.report_time = '{new_time}'
                    WHERE dp.sn = '{sn}'
                    """
                    self.db.ejecutar_consulta(consulta_update)
                
                print("✅ Los cambios han sido aplicados a la base de datos.")
                return cambios_propuestos
            else:
                print("❌ Los cambios han sido cancelados.")
                return False
            
        else:
            print("No se encontraron cambios propuestos.")
            return None