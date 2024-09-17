import os
import time
import openai
from mantenimiento import Mantenimiento
from mejora_red import Mejora
from azure.core.credentials import AzureKeyCredential

# Configurar las credenciales de Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://fivebotopenai.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "e07b7320a12c4a568bbcbe2d1d122aea"

# Datos de conexión a la base de datos
HOST = "4.233.144.238"
DATABASE = "wiot_db"
USER = "root"
PASSWORD = "Fivecomm"
PORT = "3307"

# Función para limpiar la pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función para generar mensajes con Azure OpenAI
def generar_mensaje_con_openai(prompt):
    response = openai.ChatCompletion.create(
        engine="chat-fivebot",  # Reemplaza con el nombre de tu despliegue en Azure
        messages=[
            {"role": "system", "content": "Eres un asistente virtual que interactúa con el backend y tiene que generar mensajes para el usuario de manera formal y amable."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

# Función para mostrar mensajes al usuario usando Azure OpenAI
def mostrar_mensaje_azure(mensaje):
    mensaje_formulado = generar_mensaje_con_openai(mensaje)
    print(f"{mensaje_formulado}\n")

# Función para hacer preguntas al usuario usando Azure OpenAI
def hacer_pregunta_azure(pregunta_formal):
    pregunta_formulada = generar_mensaje_con_openai(pregunta_formal)
    respuesta = input(f"{pregunta_formulada}\nSu respuesta: ").strip().lower()
    return respuesta

# Función para mostrar el menú usando un lenguaje formal generado por Azure OpenAI
def mostrar_menu_formal():
    respuesta = hacer_pregunta_azure("Por favor, indicale al usuario si desea obtener un reporte de mantenimiento o realizar una mejora de la red.")
    if "mantenimiento" in respuesta or respuesta == '1':
        return '1'
    elif "mejora" in respuesta or respuesta == '2':
        return '2'
    else:
        mostrar_mensaje_azure("Lo siento, no he podido entender su elección. Por favor, seleccione '1' para Mantenimiento o '2' para Mejora de la red.")
        return mostrar_menu_formal()

# Función principal del asistente
def iniciar_asistente():
    limpiar_pantalla()
    print("\n💼 Bienvenido a Fivebot 💼\n")
    time.sleep(1)

    # Mostrar el menú y obtener el tipo de reporte
    tipo_reporte = mostrar_menu_formal()

   # Decisiones basadas en la selección del usuario
    if tipo_reporte == '1':
        limpiar_pantalla()
        print("🛠️ Ha seleccionado generar un reporte de Mantenimiento.")
        mantenimiento = Mantenimiento(HOST, DATABASE, USER, PASSWORD, PORT)
        mantenimiento.conectar()

        # Obtener resultados de las consultas
        dispositivos_sd_no_detectada = mantenimiento.obtener_dispositivos_sd_no_detectada()
        if dispositivos_sd_no_detectada:
            mensaje = f"📋 Se encontraron {len(dispositivos_sd_no_detectada)} dispositivos con SD no detectada."
        else:
            mensaje = "📋 No se encontraron dispositivos con SD no detectada."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_sd_no_detectada:
            sd_no_detectada = input("¿Desea ver más detalles sobre los dispositivos con SD no detectada? (s/n)").strip().lower()

            if sd_no_detectada == 's':
                detalles = ""
                for sn, timestamp in dispositivos_sd_no_detectada:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        # Repetir el proceso para otros tipos de dispositivos
        dispositivos_sd_formateada = mantenimiento.obtener_dispositivos_sd_formateada()
        mensaje = f"📋 Se encontraron {len(dispositivos_sd_formateada)} dispositivos con SD formateada."
        print(mensaje)

        if dispositivos_sd_formateada:
            sd_formateada = input("¿Desea ver más detalles sobre los dispositivos con SD no detectada? (s/n)").strip().lower()
            if sd_formateada == 's':
                detalles = ""
                for sn, timestamp in dispositivos_sd_formateada:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        dispositivos_sd_no_pudo_formatear = mantenimiento.obtener_dispositivos_sd_no_pudo_formatear()
        mensaje = f"📋 Se encontraron {len(dispositivos_sd_no_pudo_formatear)} dispositivos que no pudieron formatear la SD."
        print(mensaje)

        if dispositivos_sd_no_pudo_formatear:
            sd_no_pudo_formatear = input("¿Desea ver más detalles sobre los dispositivos con SD no detectada? (s/n)").strip().lower()
            if sd_no_pudo_formatear == 's':
                detalles = ""
                for sn, timestamp in dispositivos_sd_no_pudo_formatear:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        dispositivos_menor = mantenimiento.obtener_bateria_menor()
        mensaje = f"📋 Se encontraron {len(dispositivos_menor)} dispositivos con batería menor que 2.9V."
        print(mensaje)

        if dispositivos_menor:
            disp_menor = input("¿Desea ver más detalles sobre los dispositivos con batería menor que 2.9V? (s/n)").strip().lower()
            if disp_menor == 's':
                detalles = f"{'Dispositivo':<20} | {'IMEI':<16} | {'FW':<12} | {'Último mensaje':<19} | {'Batería (V)':<10}\n"
                detalles += "-" * 90 + "\n"
                for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                    detalles += f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent:<19} | {battery:<10}\n"
                print(detalles)

        mantenimiento.desconectar()
        iniciar_asistente()

    elif tipo_reporte == '2':
        limpiar_pantalla()
        print("📈 Ha seleccionado generar un reporte de Mejora de la red.")
        mejora = Mejora(HOST, DATABASE, USER, PASSWORD, PORT)
        mejora.conectar()

        distribucion_actual = mejora.distribucion_actual()
        if distribucion_actual:
            max_hubs = max([hubs for hora, hubs in distribucion_actual])
            mensaje = "📋 Esta es la distribución actual por horas:\n"
            mensaje += f"{'Hora':<6} | {'Hubs':<6} | {'Gráfico'}\n"
            mensaje += "-" * 70 + "\n"
            for hora, hubs in distribucion_actual:
                num_barras = int((hubs / max_hubs) * 50) if max_hubs else 0
                barras = '█' * num_barras
                mensaje += f"{hora:<6} | {hubs:<6} | {barras}\n"
            mostrar_mensaje_azure(mensaje)
            print(mensaje)
        else:
            mostrar_mensaje_azure("No hay datos disponibles para mostrar la distribución actual.")

        mostrar_detalles = hacer_pregunta_azure("Indicale al usuario si desea ver los dispositivos con conflictos en el horario de reporte (s/n)")
        if mostrar_detalles == 's' or mostrar_detalles == 'si':
            for hour in range(24):
                hubs_report = mejora.conflictos_report_time(hour)
                mensaje = f"⏰ Conflictos para la hora {hour:02d}:00\n"
                if not hubs_report:
                    mensaje += f"No se encontraron conflictos de horario de reporte para la hora {hour:02d}.\n"
                else:
                    mensaje += f"{'Dispositivo':<15} | {'CID':<10} | {'Hora de reporte':<15}\n"
                    mensaje += "-" * 50 + "\n"
                    for sn, cid, report_time in hubs_report:
                        mensaje += f"{sn:<15} | {cid:<10} | {report_time:<15}\n"

                mostrar_mensaje_azure(mensaje)
                if hubs_report:
                    resolver_conflictos = hacer_pregunta_azure(f"Indicale al usuario si desea resolver los conflictos de horario de reporte para la hora {hour:02d} (s/n)")
                    if resolver_conflictos == 's':
                        mejora.resolver_conflictos_report_time_db(hubs_report)
                        mostrar_mensaje_azure(f"Indicale al usuario que los conflictos para la hora {hour:02d} se han resueltos exitosamente.")
                        

        mejora.desconectar()
        iniciar_asistente()
    else:
        mostrar_mensaje_azure("⚠️ Opción no válida. Por favor, elija una opción válida (1 o 2).")
        iniciar_asistente()

# Ejecutar el asistente
if __name__ == "__main__":
    iniciar_asistente()