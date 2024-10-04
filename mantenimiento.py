from db_connector import DBConnector


class Mantenimiento:
    def __init__(self, host, database, user, password, port):
        """Inicializa la conexión a la base de datos utilizando DBConnector."""
        self.db = DBConnector(host, database, user, password, port)

    def conectar(self):
        """Conectar a la base de datos."""
        self.db.conectar()

    def desconectar(self):
        """Cerrar la conexión a la base de datos."""
        self.db.cerrar_conexion()

    def obtener_dispositivos_sd_no_detectada(self):
        """Consulta para obtener dispositivos con 'sd_not_detected'."""
        consulta = """SELECT d.sn, MAX(a.timestamp) as last_report
        FROM narrow_db.ALARMS a
        JOIN DEVICE_PROPERTIES d ON d.id = a.device_id
        WHERE a.sd_not_detected = 1
        GROUP BY d.sn
        ORDER BY last_report DESC;
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados

    def obtener_dispositivos_sd_formateada(self):
        """Consulta para obtener dispositivos con 'sd_formated'."""
        consulta = """SELECT d.sn, MAX(a.timestamp) as last_report
        FROM narrow_db.ALARMS a
        JOIN DEVICE_PROPERTIES d ON d.id = a.device_id
        WHERE a.sd_formated = 1
        GROUP BY d.sn
        ORDER BY last_report DESC;
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados

    def obtener_dispositivos_sd_no_pudo_formatear(self):
        """Consulta para obtener dispositivos con 'sd_could_not_format'."""
        consulta = """SELECT d.sn, MAX(a.timestamp) as last_report
        FROM narrow_db.ALARMS a
        JOIN DEVICE_PROPERTIES d ON d.id = a.device_id
        WHERE a.sd_could_not_format = 1
        GROUP BY d.sn
        ORDER BY last_report DESC;
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados
    
    def obtener_bateria_menor(self):
        """Consulta para obtener los dispositivos con bateria menor de 2.9"""
        consulta="""SELECT sn, imei, fw, last_mssg_send,battery
        FROM narrow_db.DEVICE_PROPERTIES
        WHERE fw != '' AND battery < 2.9 AND battery > 0 AND fw NOT LIKE '%_MEX%' AND fw NOT LIKE '%_COL%'
        ORDER BY last_mssg_send DESC
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados
    
    def obtener_bateria_entre(self):
        """Consulta para obtener los dispositivos con bateria entre 2.9 y 3.2"""
        consulta="""SELECT sn, imei, fw, last_mssg_send,battery
        FROM narrow_db.DEVICE_PROPERTIES
        WHERE fw != '' AND battery >= 2.9 AND battery <= 3.2 AND fw NOT LIKE '%_MEX%' AND fw NOT LIKE '%_COL%'
        ORDER BY last_mssg_send DESC
        """
        resultados = self.db.ejecutar_consulta(consulta)
        return resultados