import speech_recognition as sr
import os
import datetime
import pytz
import time
from gtts import gTTS
from sqlalchemy import create_engine, text, not_,and_, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import exists, not_
from models import *
DATABASE_URL = "postgresql://postgres:lyV0fDeA4LX8EyD9yULa@containers-us-west-203.railway.app:6039/railway"
# Crea una conexión a la base de datos
engine = create_engine(DATABASE_URL)
# Crea una fábrica de sesiones
Session = sessionmaker(bind=engine)
# Crea una instancia de sesión
session = Session()

respuestas = {
    "hola": "¡Hola, en qué puedo ayudarte!",
    "cómo estás": "Bien y tú?",
    "qué hora es": "",
    "adiós": "Hasta luego. ¡Que tengas un buen día!",
    "productos": "",
    "categoría": "",
    "mujeres":"Somos todas mentirosa mas Alison Hernandez  sobre todo",
    "qué puedo comprar": "Ofrecemos una variedad de productos desde collares, pulseras personalización de cover y lienzo y más"
}

def obtener_hora():
    tz_nicaragua = pytz.timezone("America/Managua")
    hora_actual = datetime.datetime.now(tz_nicaragua).strftime("%H:%M")
    return f"La hora actual en Nicaragua es {hora_actual}."

def obtener_categorias(session):
    categorias = session.query(CategoriaProducto).all()
    nombres_categorias = [categoria.nombre for categoria in categorias]
    return ", ".join(nombres_categorias)



def obtener_subcategorias(session, categoria):
    subcategorias = (
        session.query(SubCategoriaProducto)
        .join(CategoriaProducto)
        .filter(CategoriaProducto.nombre == categoria)
        .all()
    )
    nombres_subcategorias = [subcategoria.nombre for subcategoria in subcategorias]
    return ", ".join(nombres_subcategorias)

def obtener_producto_info(session, subcategoria):
    productos = (
        session.query(Producto)
        .join(SubCategoriaProducto)
        .filter(SubCategoriaProducto.nombre == subcategoria)
        .all()
    )
    info_productos = []
    for producto in productos:
        precio_producto = (
            session.query(Precio)
            .filter_by(producto_id=producto.id_producto)
            .first()
        )
        if precio_producto:
            info_productos.append(
                f"{producto.nombre}: {producto.descripcion}, Precio: {precio_producto.precio_actual}"
            )
        else:
            info_productos.append(
                f"{producto.nombre}: {producto.descripcion}, Precio no disponible"
            )
    return "\n".join(info_productos)

def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di algo...")
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="es-ES")
        print("Has dicho:", texto)
        return texto
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
        return ""
    except sr.RequestError as e:
        print("Error al solicitar resultados; {0}".format(e))
        return ""

def hablar(texto):
    tts = gTTS(texto, lang="es-Es")
    tts.save("respuesta.mp3")
    os.system("start respuesta.mp3")
    time.sleep(6)

def asistente():
    #hablar("Hola, soy tu asistente de voz Luxx. ¿En qué puedo ayudarte?")
    while True:
        comando = escuchar().lower()
       
        if comando in respuestas:
            respuesta = respuestas[comando]
            if comando == "qué hora es":
                respuesta = obtener_hora()
            if comando == "categoría":
                respuesta = "Las categorías disponibles son: " + obtener_categorias(session)
            if comando == obtener_subcategorias(session,comando.capitalize()).split(", "):
                clave=comando.capitalize()
                print(clave)
                subcategorias = obtener_subcategorias(session, clave)
                respuesta = f"Las subcategorías de {comando} son: {subcategorias}"
            if comando in obtener_subcategorias(session, comando).lower().split(", "):
                respuesta = obtener_producto_info(session, comando)
            hablar(respuesta)
        else:
            hablar("Lo siento, no comprendo ese comando.")

if __name__ == "__main__":
    sr.pause_threshold = 0.5
    asistente()