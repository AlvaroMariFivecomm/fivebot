import os
import time
import openai
from mantenimiento import Mantenimiento
from mejora_red import Mejora
from nube import hacer_pregunta_azure, mostrar_mensaje_azure
from pdf import crear_pdf

from optimizer import optimize_devices

# Datos de conexión a la base de datos
HOST = "localhost"
DATABASE = "narrow_db"
USER = "root"
PASSWORD = "Fivecomm"
PORT = "3307"

# Ruta donde quieres guardar el PDF
output_path = "/home/alvaro/Alo/applications/utils/fivecomm_IA/"

# Función para limpiar la pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


# Función para mostrar el menú usando un lenguaje formal generado por Azure OpenAI
def mostrar_menu_formal():
    respuesta = hacer_pregunta_azure("Por favor, indicale al usuario si desea obtener un reporte de mantenimiento , resolver los conflictos con los report times o optimizar la red de dispositivos por report time.")
    if "mantenimiento" in respuesta or respuesta == '1':
        return '1'
    elif "conflictos" in respuesta or respuesta == '2':
        return '2'
    elif "optimizar" in respuesta or respuesta == '3':
        return '3'
    else:
        mostrar_mensaje_azure("Lo siento, no he podido entender su elección. Por favor, seleccione '1' para mantenimiento, '2' para resolver los conflictos o '3' para optimizar la red.")
        return mostrar_menu_formal()


def opcion_optimizar():
    limpiar_pantalla()
    print("📈 Ha seleccionado la opción de optimizar la red de los dispositivos por report time.")

    print("")

    print("INTERVALO DE TIEMPO MINIMO (MIN)")
    interval_between_device_reports_input = hacer_pregunta_azure('Indicale al usuario que seleccione el intervalo de tiempo mínimo en minutos entre la comunicación de dos dispositivos en una misma celda')
    interval_between_device_reports = int(interval_between_device_reports_input)
    print("NÚMERO MÁXIMO DE DISPOSITIVOS POR HORA")
    max_global_devices_per_hour_input = hacer_pregunta_azure('Indicale al usuario que proporcione el número máximo de dispositivos por hora en la red')
    max_global_devices_per_hour = int(max_global_devices_per_hour_input)
    print("NÚMERO MÁXIMO DE DISPOSITIVOS POR HORA EN LA MISMA CELDA")
    max_devices_per_cell_per_hour_input = hacer_pregunta_azure('Indicale al usuario que proporcione el número máximo de dispositivos por hora que comparten celda')
    max_devices_per_cell_per_hour = int(max_devices_per_cell_per_hour_input)
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

#############################
        dispositivos_sd_no_detectada = mantenimiento.obtener_dispositivos_sd_no_detectada()
        detalles_sd_no_detectada = ""

        if dispositivos_sd_no_detectada:
            
            detalles_sd_no_detectada = f"se han encontrado {len(dispositivos_sd_no_detectada)} dispositivos con SD no detectada"
            mostrar_mensaje_azure(detalles_sd_no_detectada)
            qstn_sd_no_detectada = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD no detectada (s/n)")

            if qstn_sd_no_detectada == 's' or 'si' in qstn_sd_no_detectada:
                for sn, timestamp in dispositivos_sd_no_detectada:
                    detalles_sd_no_detectada += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles_sd_no_detectada)
        else:
            detalles_sd_no_detectada = "Dile al usuario que no se encontraron dispositivos con SD no detectada."
            mostrar_mensaje_azure(detalles_sd_no_detectada)
##############################
        dispositivos_sd_formateada = mantenimiento.obtener_dispositivos_sd_formateada()
        detalles_sd_formateada = ""
        if dispositivos_sd_formateada:
            detalles_sd_formateada = f"Se han encontrado {len(dispositivos_sd_formateada)} dispositivos con SD formateada."
            mostrar_mensaje_azure(detalles_sd_formateada)

            qstn_sd_formateada = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD formateada (s/n)")
            if qstn_sd_formateada == 's' or 'si' in qstn_sd_formateada:
                for sn, timestamp in dispositivos_sd_formateada:
                    detalles_sd_formateada += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles_sd_formateada)
        else:
            detalles_sd_formateada = "Dile al usuario que no se han encontrado dispositivos con SD formateada."
            mostrar_mensaje_azure(detalles_sd_formateada)
###############################
        dispositivos_sd_no_pudo_formatear = mantenimiento.obtener_dispositivos_sd_no_pudo_formatear()
        detalles_sd_no_pudo_formatear = ""
        if dispositivos_sd_no_pudo_formatear:
            detalles_sd_no_pudo_formatear = f"Se han encontrado {len(dispositivos_sd_no_pudo_formatear)} dispositivos que no pudieron formatear la SD."
            mostrar_mensaje_azure(detalles_sd_no_pudo_formatear)
            qstn_sd_no_pudo_formatear = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con SD no detectada (s/n)")
            if qstn_sd_no_pudo_formatear == 's' or 'si' in qstn_sd_no_pudo_formatear:
                for sn, timestamp in dispositivos_sd_no_pudo_formatear:
                    detalles_sd_no_pudo_formatear += f"Dispositivo: {sn}, Último reporte: {timestamp}\n"
                print(detalles_sd_no_pudo_formatear)
        else:
            detalles_sd_no_pudo_formatear = "No se han encontrado dispositivos que no pudieron formatear la SD."
            mostrar_mensaje_azure(detalles_sd_no_pudo_formatear)
################################
        dispositivos_menor = mantenimiento.obtener_bateria_menor()
        detalles_dispositivos_menor = ""
        if dispositivos_menor:
            detalles_dispositivos_menor = f"Se han encontrado {len(dispositivos_menor)} dispositivos con batería menor que 2.9V."
            mostrar_mensaje_azure(detalles_dispositivos_menor)

            qstn_disp_menor = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con batería menor que 2.9V (s/n)").strip().lower()
            if qstn_disp_menor == 's' or 'si' in qstn_disp_menor:
                detalles_dispositivos_menor = f"{'Dispositivo':<20} | {'IMEI':<16} | {'FW':<12} | {'Último mensaje':<19} | {'Batería (V)':<10}\n"
                detalles_dispositivos_menor += "-" * 90 + "\n"
                for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                    detalles_dispositivos_menor += f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<10}\n"
                print(detalles_dispositivos_menor)
        else:
            detalles_dispositivos_menor = f"Dile al usuario que no se han encontrado dispositivos con batería menor que 2.9V."
            mostrar_mensaje_azure(detalles_dispositivos_menor)
#################################            
        dispositivos_entre = mantenimiento.obtener_bateria_entre()
        detalles_dispositivos_entre = ""
        if dispositivos_entre:
            detalles_dispositivos_entre = f"Se han encontrado {len(dispositivos_entre)} dispositivos con batería entre 2.9V y 3.2V."
            mostrar_mensaje_azure(detalles_dispositivos_entre)            

            qst_disp_entre = hacer_pregunta_azure("Pregúntale al usuario si desea ver más detalles sobre los dispositivos con batería entre 2.9V y 3.2V (s/n)").strip().lower()
            if qst_disp_entre == 's' or 'si' in qst_disp_entre:
                detalles_dispositivos_entre = f"{'Dispositivo':<20} | {'IMEI':<16} | {'FW':<12} | {'Último mensaje':<19} | {'Batería (V)':<10}\n"
                detalles_dispositivos_entre += "-" * 90 + "\n"
                for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                    detalles_dispositivos_entre += f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<10}\n"
                print(detalles_dispositivos_entre)
        else:
            detalles_dispositivos_entre = f"Dile al usuario que no se han encontrado dispositivos con batería entre 2.9V y 3.2V."

            mostrar_mensaje_azure(detalles_dispositivos_entre)            
        
        input(f"\nPulsa enter para continuar").strip().lower()

        mantenimiento.desconectar()

        elecciones = [
            ("Dispositivos con SD no detectada", detalles_sd_no_detectada),
            ("Dispositivos con SD formateada", detalles_sd_formateada),
            ("Dispositivos con SD que no pudo formatear", detalles_sd_no_pudo_formatear),
            ("Dispositivos con batería menor de 2.9V", detalles_dispositivos_menor),
            ("Dispositivos con batería entre 2.9V y 3.2V", detalles_dispositivos_entre)
        ]

        crear_pdf(elecciones, output_path + 'mantenimiento.pdf')
        iniciar_asistente()
    elif tipo_reporte == '2':
        elecciones_tipo_reporte = []
        limpiar_pantalla()
        print("📈 Ha seleccionado generar un reporte de Mejora de la red.")
        mejora = Mejora(HOST, DATABASE, USER, PASSWORD, PORT)
        mejora.conectar()

        distribucion_actual = mejora.distribucion_actual()
        if distribucion_actual:
            max_hubs = max([hubs for hora, hubs in distribucion_actual])
            mensaje = "Esta es la distribución actual por horas:\n"
            mensaje += f"{'Hora':<6} | {'Hubs':<6} | {'Gráfico'}\n"
            mensaje += "-" * 70 + "\n"
            for hora, hubs in distribucion_actual:
                num_barras = int((hubs / max_hubs) * 50) if max_hubs else 0
                barras = '||' * num_barras
                mensaje += f"{hora:<6} | {hubs:<6} | {barras}\n"
            mostrar_mensaje_azure(mensaje)
            print(mensaje)
            elecciones_tipo_reporte.append(("Distribución actual por horas", mensaje))
        else:
            mostrar_mensaje_azure("No hay datos disponibles para mostrar la distribución actual.")

        mostrar_detalles = hacer_pregunta_azure("Indicale al usuario si desea ver los dispositivos con conflictos en el horario de reporte (s/n)")
        if mostrar_detalles == 's' or mostrar_detalles == 'si':
            while True:
                hour_input = input("\nDe qué hora quieres ver los conflictos (hh). Escribe exit para salir: ").strip().lower()

                if hour_input == 'exit':
                    break

                if not hour_input.isdigit() or not (0 <= int(hour_input) <= 23):
                    mostrar_mensaje_azure("Por favor, ingrese una hora válida entre 00 y 23 o 'exit' para salir.")
                    continue

                hour = int(hour_input)

                hubs_report = mejora.conflictos_report_time(hour)
                mensaje = f"Conflictos para la hora {hour:02d}:00\n"

                if not hubs_report:
                    mensaje += f"No se encontraron conflictos de horario de reporte para la hora {hour:02d}.\n"
                    elecciones_tipo_reporte.append((f"Conflictos para la hora {hour:02d}:00\n", mensaje))
                else:
                    mensaje += f"{'Dispositivo':<15} | {'CID':<10} | {'Hora de reporte':<15}\n"
                    mensaje += "-" * 50 + "\n"
                    for sn, cid, report_time in hubs_report:
                        mensaje += f"{sn:<15} | {cid:<10} | {report_time:<15}\n"

                    elecciones_tipo_reporte.append((f"Conflictos para la hora {hour:02d}:00\n", mensaje))

                mostrar_mensaje_azure(mensaje)

                if hubs_report:
                    resolver_conflictos = hacer_pregunta_azure(f"Indicale al usuario si desea resolver los conflictos de horario de reporte para la hora {hour:02d} (s/n)")
                    if resolver_conflictos == 's':
                        cambio = mejora.resolver_conflictos_report_time_db(hubs_report)
                        if cambio:
                            mostrar_mensaje_azure(f"Los conflictos para la hora {hour:02d} se han resuelto exitosamente.")
                            elecciones_tipo_reporte.append((f"Cambios para la hora {hour:02d}", cambio))

                            
        crear_pdf(elecciones_tipo_reporte, output_path + 'mejora.pdf')
                        
        input(f"\nPulsa enter para continuar").strip().lower()

        mejora.desconectar()
 
        iniciar_asistente()
    elif tipo_reporte == '3':
        while True:
            ans = opcion_optimizar()
            
            if not ans:
                iniciar_asistente()
                break
    else:
        mostrar_mensaje_azure("⚠️ Opción no válida. Por favor, elija una opción válida (1 o 2).")
        iniciar_asistente()

# Ejecutar el asistente
if __name__ == "__main__":
    iniciar_asistente()