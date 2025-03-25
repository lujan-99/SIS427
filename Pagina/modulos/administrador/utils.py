import pdfplumber
from modulos.cliente.models import Pregunta, Cuestionario

def procesar_pdf(pdf_path, cuestionario_id):
    cuestionario = Cuestionario.objects.get(id=cuestionario_id)
    
    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()

    # Separar el texto por las categorías principales
    try:
        seccion_respuesta_directa = texto_completo.split("Preguntas con respuesta directa (respuestas cortas):")[1].split("Preguntas de Falso/Verdadero:")[0]
        seccion_falso_verdadero = texto_completo.split("Preguntas de Falso/Verdadero:")[1].split("Preguntas de Opción Múltiple (algunas con más de una respuesta correcta):")[0]
        seccion_opcion_multiple = texto_completo.split("Preguntas de Opción Múltiple (algunas con más de una respuesta correcta):")[1]
        
        # Imprimir el tamaño de las secciones
        print(f"Tamaño de la sección 'Preguntas con Respuesta Directa': {len(seccion_respuesta_directa.splitlines())} líneas")
        print(f"Tamaño de la sección 'Preguntas de Falso/Verdadero': {len(seccion_falso_verdadero.splitlines())} líneas")
        print(f"Tamaño de la sección 'Preguntas de Opción Múltiple': {len(seccion_opcion_multiple.splitlines())} líneas")
        
        # Procesar cada sección individualmente
        procesar_preguntas_respuesta_directa(seccion_respuesta_directa, cuestionario)
        procesar_preguntas_falso_verdadero(seccion_falso_verdadero, cuestionario)
        procesar_preguntas_opcion_multiple(seccion_opcion_multiple, cuestionario)
    except IndexError:
        print("Error al dividir las secciones del PDF. Verifica el formato del documento.")
        return

def procesar_preguntas_respuesta_directa(seccion, cuestionario):
    # Procesa las preguntas de respuesta directa (RL)
    lineas = seccion.split("\n")
    for i in range(len(lineas)):
        if "Pregunta" in lineas[i]:
            try:
                pregunta = lineas[i].split("Pregunta:")[1].strip()
                respuesta = lineas[i + 1].split("Respuesta:")[1].strip().rstrip(".")
                print(f"Procesando pregunta RL: {pregunta}, Respuesta: {respuesta}")
                Pregunta.objects.create(
                    pregunta=pregunta,
                    respuesta=respuesta,
                    tipo="RL",  # Respuesta directa
                    opciones=None,
                    cuestionario=cuestionario
                )
            except (IndexError, ValueError):
                continue

def procesar_preguntas_falso_verdadero(seccion, cuestionario):
    lineas = seccion.split("\n")
    pregunta = ""
    for i in range(len(lineas)):
        if "Pregunta" in lineas[i]:
            try:
                # Unir líneas de la pregunta
                pregunta = lineas[i].split("Pregunta:")[1].strip()
                while not pregunta.endswith(".") and i + 1 < len(lineas):
                    i += 1
                    pregunta += " " + lineas[i].strip()
                
                # Buscar la respuesta en las líneas siguientes
                for j in range(i + 1, len(lineas)):
                    if "Respuesta" in lineas[j]:
                        respuesta = lineas[j].split("Respuesta:")[1].strip().rstrip(".")
                        print(f"Procesando pregunta FV: {pregunta}, Respuesta: {respuesta}")
                        Pregunta.objects.create(
                            pregunta=pregunta,
                            respuesta=respuesta,
                            tipo="FV",  # Falso/Verdadero
                            opciones=None,
                            cuestionario=cuestionario
                        )
                        break
            except (IndexError, ValueError):
                print(f"Error procesando la pregunta FV en la línea {i}: {lineas[i]}")
                continue



def procesar_preguntas_opcion_multiple(seccion, cuestionario):
    lineas = seccion.split("\n")
    pregunta = ""
    opciones_lista = []
    respuesta = ""
    dentro_de_opciones = False

    for i in range(len(lineas)):
        # Imprimir la línea actual para depuración
        print(f"Procesando línea {i}: {lineas[i]}")
        
        # Detectar el inicio de una pregunta
        if "Pregunta" in lineas[i]:
            try:
                # Capturar la pregunta
                pregunta = lineas[i].split("Pregunta:")[1].strip()
                while not pregunta.endswith("?") and i + 1 < len(lineas):
                    i += 1
                    pregunta += " " + lineas[i].strip()
                
                # Imprimir la pregunta capturada
                print(f"Pregunta capturada: {pregunta}")

                # Iniciar la recolección de opciones
                opciones_lista = []
                dentro_de_opciones = True
                continue  # Continuar con la siguiente línea

            except (IndexError, ValueError):
                print(f"Error procesando la pregunta OM en la línea {i}: {lineas[i]}")
                continue

        # Recolectar las opciones
        if dentro_de_opciones and lineas[i].strip().startswith("▪"):
            opciones_lista.append(lineas[i].strip().lstrip("▪"))

        # Detectar la línea de respuesta
        if "Respuesta" in lineas[i]:
            respuesta = lineas[i].split("Respuesta:")[1].strip().rstrip(".").replace(" ", "")
            dentro_de_opciones = False  # Finalizamos la captura de opciones

            # Imprimir las opciones y la respuesta capturada
            print(f"Opciones capturadas: {opciones_lista}")
            print(f"Respuesta capturada: {respuesta}")

            # Crear la pregunta en la base de datos
            opciones = "\n".join(opciones_lista)
            Pregunta.objects.create(
                pregunta=pregunta,
                respuesta=respuesta,
                tipo="OM",  # Opción múltiple
                opciones=opciones,
                cuestionario=cuestionario
            )
            # Reiniciar para la siguiente pregunta
            pregunta = ""
            opciones_lista = []
            respuesta = ""


