import mysql.connector
from mysql.connector import Error

class DBConnector:
    def __init__(self, host, database, user, password, port):
        """Inicializa la conexión a la base de datos."""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conexion = None

    def conectar(self):
        """Establece la conexión a la base de datos MariaDB."""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            # if self.conexion.is_connected():
                # print("✅ Conexión exitosa a la base de datos MariaDB")
        except Error as e:
            print(f"⚠️ Error al conectar a la base de datos: {e}")
            self.conexion = None

    def ejecutar_consulta(self, consulta, params=None):
        """Ejecuta una consulta SQL y devuelve los resultados."""
        if not self.conexion:
            print("⚠️ No hay conexión a la base de datos.")
            return None

        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, params)

            if consulta.lower().startswith(('insert', 'update', 'delete')):
                self.conexion.commit()

            if consulta.lower().startswith('select'):
                resultados = cursor.fetchall()
                cursor.close()
                return resultados

            print("✅ Transacción confirmada con éxito.")
            cursor.close()
        except Error as e:
            print(f"⚠️ Error al ejecutar la consulta: {e}")
            return None

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("🔌 Conexión cerrada.")

