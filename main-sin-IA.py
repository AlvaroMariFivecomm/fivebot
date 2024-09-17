import os
import time
from mantenimiento import Mantenimiento
from mejora_red import Mejora

 # Datos de conexión a la base de datos
HOST = "4.233.144.238"
DATABASE = "wiot_db"
USER = "root"
PASSWORD = "Fivecomm"
PORT="3307"

# Función para limpiar la pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función para mostrar una pregunta y recoger la respuesta del usuario
def hacer_pregunta(pregunta):
    print("\n" + "="*50)
    print(f"👉 {pregunta}")
    print("="*50)
    return input("\nTu respuesta: ")

# Función para mostrar un menú de opciones
def mostrar_menu():
    print("\n1. Mantenimiento")
    print("2. Mejora de la red")
    return input("\nSelecciona el tipo de reporte (1 o 2): ")

# Función principal
def iniciar_asistente():
    limpiar_pantalla()
    print("\n💼 Bienvenido al asistente de Fivecomm 💼\n")
    time.sleep(1)

    # Preguntar qué tipo de reporte desea
    tipo_reporte = mostrar_menu()

    # Decisiones basadas en la selección del usuario
    if tipo_reporte == '1':
        limpiar_pantalla()
        print("\n🔧 Has seleccionado el reporte de Mantenimiento.\n")
        mantenimiento = Mantenimiento(HOST, DATABASE, USER, PASSWORD, PORT)
        # Conectar a la base de datos
        mantenimiento.conectar()

        # Obtener resultados de las consultas

        # 1. Dispositivos con SD no detectada
        dispositivos_sd_no_detectada = mantenimiento.obtener_dispositivos_sd_no_detectada()
        if dispositivos_sd_no_detectada:
            print(f"\n📋 Se encontraron {len(dispositivos_sd_no_detectada)} dispositivos con SD no detectada.")
        else:
            print(f"\n📋 No se encontraron dispositivos con SD no detectada.")

        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()

        if mostrar_detalles == 's':
            for sn, timestamp in dispositivos_sd_no_detectada:
                print(f"Dispositivo: {sn}, Último reporte: {timestamp}")

        # 2. Dispositivos con SD formateada
        dispositivos_sd_formateada = mantenimiento.obtener_dispositivos_sd_formateada()
        print(f"\n📋 Se encontraron {len(dispositivos_sd_formateada)} dispositivos con SD formateada.")
        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()

        if mostrar_detalles == 's':
            for sn, timestamp in dispositivos_sd_formateada:
                print(f"Dispositivo: {sn}, Último reporte: {timestamp}")

        # 3. Dispositivos con SD que no pudo formatearse
        dispositivos_sd_no_pudo_formatear = mantenimiento.obtener_dispositivos_sd_no_pudo_formatear()
        print(f"\n📋 Se encontraron {len(dispositivos_sd_no_pudo_formatear)} dispositivos con SD que no pudo formatearse.")
        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()

        if mostrar_detalles == 's':
            for sn, timestamp in dispositivos_sd_no_pudo_formatear:
                print(f"Dispositivo: {sn}, Último reporte: {timestamp}")

        # 4. Dispositivos con batería menor que 2.9
        dispositivos_menor = mantenimiento.obtener_bateria_menor()
        print(f"\n📋 Se encontraron {len(dispositivos_menor)} dispositivos con batería menor que 2.9.")
        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()

        if mostrar_detalles == 's':
            print(f"{'Dispositivo':<20} | {'Imei':<16} | {'fw':<12} | {'last_message_sent':<19} | {'bateria':<6}")
            for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                print(f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<6}")

        # 5. Dispositivos con batería entre 2.9 y 3.2
        dispositivos_menor = mantenimiento.obtener_bateria_entre()
        print(f"\n📋 Se encontraron {len(dispositivos_menor)} dispositivos con batería entre 2.9 y 3.2.")
        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()

        if mostrar_detalles == 's':
            print(f"{'Dispositivo':<20} | {'Imei':<16} | {'fw':<12} | {'last_message_sent':<19} | {'bateria':<6}")
            for sn, imei, fw, last_message_sent, battery in dispositivos_menor:
                print(f"{sn:<20} | {imei:<16} | {fw:<12} | {last_message_sent} | {battery:<6}")
        # Cerrar la conexión
        mantenimiento.desconectar()
        iniciar_asistente()
    elif tipo_reporte == '2':
        limpiar_pantalla()
        print("\n📈 Has seleccionado el reporte de Mejora de la red.\n")
        mejora = Mejora(HOST, DATABASE, USER, PASSWORD, PORT)
        # Conectar a la base de datos
        mejora.conectar()

        # Obtener resultados de las consultas

        # Definir el ancho máximo de la barra
        ancho_maximo = 50
        # 1. Distribución actual
        distribucion_actual = mejora.distribucion_actual()
        max_hubs = max([hubs for hora, hubs in distribucion_actual])

        print(f"\n📋 Esta es la distribución actual por")
        print(f"{'Hora':<6} | {'Hubs':<6} ")
        for hora, hubs in distribucion_actual:
            # Calcular el número de caracteres de la barra en función de los hubs
            num_barras = int((hubs / max_hubs) * ancho_maximo)
            barras = '█' * num_barras  # Usa el carácter de bloque completo
            print(f"{hora:<6} | {hubs:<6} | {barras}")
        
        # 2. Ver conflictos
        print(f"\n📋 ¿Quieres ver los dispositivos que tienen conflictos con el report time?")
        mostrar_detalles = input("¿Deseas ver más detalles? (s/n): ").strip().lower()
        
        if mostrar_detalles == 's':
            # Iterar sobre todas las horas del día (de 00 a 23)
            for hour in range(24):
                # Obtener los conflictos para la hora actual
                hubs_report = mejora.conflictos_report_time(hour)
                
                # Mostrar la hora actual
                print(f"\n⏰ Conflictos para la hora {hour:02d}:00\n")

                # Verificar si hay resultados
                if not hubs_report:
                    print(f"No se encontraron conflictos de report time para la hora {hour:02d}.")
                else:
                    # Mostrar los resultados en formato tabular
                    print(f"{'Device SN':<15} | {'CID':<10} | {'Report Time':<15}")
                    print("-" * 70)
                    
                    for sn, cid, report_time in hubs_report:
                        print(f"{sn:<15} | {cid:<10} | {report_time:<15}")
                    
                    # 3. Resolver conflictos
                    mostrar_detalles = input(f"¿Quieres resolver los conflictos de report time para la hora {hour:02d}? (s/n): ").strip().lower()
                    if mostrar_detalles == 's':
                        # Obtener los dispositivos con conflictos para la hora actual
                        hubs_report_conflictos = mejora.conflictos_report_time(hour)
                        mejora.resolver_conflictos_report_time_db(hubs_report_conflictos)

        #4 

                            
    else:
        print("\n⚠️ Opción no válida. Por favor, reinicia y elige una opción válida (1 o 2).\n")

# Ejecutar el asistente
iniciar_asistente()