import openai

# Configurar las credenciales de Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://botdefivecomm.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "9e39810840064977acd5da7c53cfd076"


# Función para generar mensajes con Azure OpenAI
def generar_mensaje_con_openai(prompt, historial=[]):
    response = openai.ChatCompletion.create(
        engine="Fivebot",  # Usa el nombre de tu despliegue en Azure
        messages=[
            {"role": "system", "content": "Eres un asistente virtual con IA llamado Fivebot. Interactúas con el backend de una aplicación para comunicarle información relevante al usuario. Utiliza un lenguaje claro, sencillo y conciso. No seas servicial, limitate a comunicar el mensaje y a no pedir feedback"},
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
    mensaje_formulado = generar_mensaje_con_openai(mensaje, historial)
    print(f"{mensaje_formulado}\n")

# Función para hacer preguntas al usuario usando Azure OpenAI
def hacer_pregunta_azure(pregunta_formal):
    pregunta_formulada = generar_mensaje_con_openai(pregunta_formal,historial)
    respuesta = input(f"{pregunta_formulada}\nSu respuesta: ").strip().lower()
    return respuesta