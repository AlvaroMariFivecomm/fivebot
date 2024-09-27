import os
import time
import openai
from mantenimiento import Mantenimiento
from mejora_red import Mejora
from azure.core.credentials import AzureKeyCredential

from optimizer.optimizer import optimize_devices

# Configurar las credenciales de Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://botdefivecomm.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "9e39810840064977acd5da7c53cfd076"

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
def generar_mensaje_con_openai(prompt, historial=[]):
    response = openai.ChatCompletion.create(
        engine="Fivebot",  # Usa el nombre de tu despliegue en Azure
        messages=[
            {"role": "system", "content": "Eres un asistente virtual con IA llamado Fivebot. Interactúas con el backend de una aplicación para comunicarle información relevante al usuario. Utiliza un lenguaje claro, sencillo y conciso."},
            *historial,  # Incluye mensajes pasados hasta un máximo de 10, como especificaste
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,  
        temperature=0.7, 
        top_p=0.95,  
        frequency_penalty=0,
        presence_penalty=0, 
        stop=None  
    )
    return response.choices[0].message['content'].strip()

historial = [
    {"role": "user", "content": "indicale al usuario si desea obtener un reporte de mantenimiento o realizar una mejora de la red"},
    {"role": "assistant", "content": "Estimado usuario, ¿desea obtener un reporte de mantenimiento de la red o realizar una mejora en la misma? Indícame cuál de las dos opciones prefieres."},

    {"role": "user", "content": "Comunicale al usuario que se han encontradi 12 dispositivos con SD no detectada."},
    {"role": "assistant", "content": "Buen día, hemos detectado que en el sistema se han registrado 12 dispositivos con problemas de detección de tarjeta SD. Por favor, envíe un técnico para que verifique el estado de los dispositivos y se asegure de que están correctamente conectados. En caso de persistir el problema, contacta con el departamento de soporte técnico para que puedan brindarte la asistencia necesaria."},

    {"role": "user", "content": "Indicale al usuario si desea ver los dispositivos con conflictos en el horario de reporte (s/n)"},
    {"role": "assistant", "content": "Estimado usuario, ¿desea ver los dispositivos con conflictos en el horario de reporte? Por favor, responda sí o no."},

    {"role": "user", "content": "comunícale al usuario que se han encontrado conflictos de los siguientes dispositivos con el report time"},
    {"role": "assistant", "content": "Se han detectado conflictos en la hora 00:00 en los dispositivos FC23C2S02W0M005311 y FC23C2S02WHT004771. Ambos dispositivos reportan a las 00:19 y presentan el mismo CID.Por favor, revisa la configuración de los dispositivos y verifica si es necesario realizar alguna corrección en los mismos para evitar futuros conflictos."},

    {"role": "user", "content": "Indicale al usuario si desea resolver los conflictos de horario de reporte para la hora 00 (s/n)"},
    {"role": "assistant", "content": "Estimado/a usuario/a, ¿desea resolver los conflictos de horario de reporte para la hora 00? Por favor, responda con 's' para sí o 'n' para no."}

]

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
    respuesta = hacer_pregunta_azure("Por favor, indicale al usuario si desea obtener un reporte de mantenimiento , resolver los conflictos con los report times o optimizar la red de dispositivos por report time.")
    if "mantenimiento" in respuesta or respuesta == '1':
        return '1'
    elif "mejora" in respuesta or respuesta == '2':
        return '2'
    elif "optimizar" in respuesta or respuesta == '3':
        return '3'
    else:
        mostrar_mensaje_azure("Lo siento, no he podido entender su elección. Por favor, seleccione '1' para mantenimiento, '2' para resolver los conflictos o '3' para optimizar la red.")
        return mostrar_menu_formal()


def opcion_optimizar():
    limpiar_pantalla()
    print("📈 Ha seleccionado la opción de optimizar la red de los dispositivos por report time.")
    interval_between_device_reports = hacer_pregunta_azure('Indicale al usuario que seleccione el intervalo de tiempo mínimo entre la comunicación de dos dispositivos en una misma celda')
    max_global_devices_per_hour = hacer_pregunta_azure('Indicale al usuario que proporcione el número máximo de dispositivos por hora en la red')
    max_devices_per_cell_per_hour = hacer_pregunta_azure('Indicale al usuario que proporcione el número máximo de dispositivos por hora que comparten celda')

    return optimize_devices(interval_between_device_reports, max_global_devices_per_hour, max_devices_per_cell_per_hour)


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
        print("🛠️ Has seleccionado la opción de resolver los conflictos con los report times.")
        mantenimiento = Mantenimiento(HOST, DATABASE, USER, PASSWORD, PORT)
        mantenimiento.conectar()

        # Obtener resultados de las consultas
        dispositivos_sd_no_detectada = mantenimiento.obtener_dispositivos_sd_no_detectada()
        if dispositivos_sd_no_detectada:
            mensaje = f"📋 Dile al usuario que se han encontrado {len(dispositivos_sd_no_detectada)} dispositivos con SD no detectada."
        else:
            mensaje = "📋 No se encontraron dispositivos con SD no detectada."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_sd_no_detectada:
            sd_no_detectada = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD no detectada (s/n)")

            if sd_no_detectada == 's' or 'si' in sd_no_detectada:
                detalles = ""
                for sn, timestamp in dispositivos_sd_no_detectada:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        # Repetir el proceso para otros tipos de dispositivos
        dispositivos_sd_formateada = mantenimiento.obtener_dispositivos_sd_formateada()
        mensaje = f"📋 Dile al usuario que se han encontrado {len(dispositivos_sd_formateada)} dispositivos con SD formateada."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_sd_formateada:
            sd_formateada = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD no detectada (s/n)")
            if sd_formateada == 's' or 'si' in sd_formateada:
                detalles = ""
                for sn, timestamp in dispositivos_sd_formateada:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        dispositivos_sd_no_pudo_formatear = mantenimiento.obtener_dispositivos_sd_no_pudo_formatear()
        mensaje = f"📋 Dile al usuario que se han encontrado {len(dispositivos_sd_no_pudo_formatear)} dispositivos que no pudieron formatear la SD."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_sd_no_pudo_formatear:
            sd_no_pudo_formatear = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD no detectada (s/n)")
            if sd_no_pudo_formatear == 's' or 'si' in sd_no_pudo_formatear:
                detalles = ""
                for sn, timestamp in dispositivos_sd_no_pudo_formatear:
                    detalles += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles)

        dispositivos_menor = mantenimiento.obtener_bateria_menor()
        mensaje = f"📋 Dile al usuario que se han encontrado {len(dispositivos_menor)} dispositivos con batería menor que 2.9V."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_menor:
            disp_menor = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con batería menor que 2.9V (s/n)").strip().lower()
            if disp_menor == 's' or 'si' in disp_menor:
                detalles = f"{'Dispositivo':<20} | {'IMEI':<16} | {'FW':<12} | {'Último mensaje':<19} | {'Batería (V)':<10}\n"
                detalles += "-" * 90 + "\n"
                for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                    detalles += f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<10}\n"
                print(detalles)

        dispositivos_entre = mantenimiento.obtener_bateria_entre()
        mensaje = f"📋 Dile al usuario que se han encontrado {len(dispositivos_entre)} dispositivos con batería entre 2.9V y 3.2V."
        mostrar_mensaje_azure(mensaje)

        if dispositivos_entre:
            disp_entre = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con batería entre 2.9V y 3.2V (s/n)").strip().lower()
            if disp_entre == 's' or 'si' in disp_entre:
                detalles = f"{'Dispositivo':<20} | {'IMEI':<16} | {'FW':<12} | {'Último mensaje':<19} | {'Batería (V)':<10}\n"
                detalles += "-" * 90 + "\n"
                for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                    detalles += f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<10}\n"
                print(detalles)


        respuesta = input(f"\nPulsa enter para continuar").strip().lower()


        mantenimiento.desconectar()

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
                # hour=23
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
                        
        respuesta = input(f"\nPulsa enter para continuar").strip().lower()

        mejora.desconectar()
        iniciar_asistente()
    elif tipo_reporte == '3':
        ans = opcion_optimizar()
        if ans == False:
            opcion_optimizar
    else:
        mostrar_mensaje_azure("⚠️ Opción no válida. Por favor, elija una opción válida (1 o 2).")
        iniciar_asistente()

# Ejecutar el asistente
if __name__ == "__main__":
    iniciar_asistente()