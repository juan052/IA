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
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "cómo estás": "Bien y tu?",
    "qué hora es": "",
    "adiós": "Hasta luego. ¡Que tengas un buen día!",
    "productos": "",
    "categorias":"",
    "qué puedo comprar": "Ofrecemos una variedad de productos desde collares, pulseras personalizacion de cover y lienzo y mas"
}

def obtener_hora():
    tz_nicaragua = pytz.timezone("America/Managua")
    hora_actual = datetime.datetime.now(tz_nicaragua).strftime("%H:%M")
    print(hora_actual)
    return f"La hora actual en Nicaragua es {hora_actual}."

def obtener_productos(session):
    productos = session.query(CategoriaProducto).all()
    nombres_productos = [producto.nombre for producto in productos]
    
    cadena_productos = ", ".join(nombres_productos)
    resultado = f"Los productos que contamos actualmente son: {cadena_productos}"
    
    print(resultado)
    return resultado


def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di algo...")
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="es-ES")
        print("Has dicho: " + texto)
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
    time.sleep(5)

def asistente():
    hablar("Hola, soy tu asistente de voz Luxx. ¿En qué puedo ayudarte?")
    while True:
        comando = escuchar().lower()
        if comando in respuestas:
            respuesta = respuestas[comando]
            if comando == "qué hora es":
                respuesta = obtener_hora()
            if comando=="productos":
                respuesta = obtener_productos(session)

            hablar(respuesta)
        else:
            hablar("Lo siento, no comprendo ese comando.")

if __name__ == "__main__":
    sr.pause_threshold = 0.5
    asistente()
