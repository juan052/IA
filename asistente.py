import speech_recognition as sr
from gtts import gTTS
import os
import datetime
import pytz
import time
respuestas = {
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "cómo estás": "Leroy muele cochones del Casimiro Sotelo.",
    "qué hora es": "",
    "adiós": "Hasta luego. ¡Que tengas un buen día!",
    "Messi": "¡Claro! Sin duda alguna Leonel Andres Messi.",
    "qué puedo comprar": "Ofrecemos una variedad de productos desde collares, pulseras personzalisacion de cover y lienzo y mas"
}

def obtener_hora():
    tz_nicaragua = pytz.timezone("America/Managua")
    hora_actual = datetime.datetime.now(tz_nicaragua).strftime("%H:%M")
    print(hora_actual)
    return f"La hora actual en Nicaragua es {hora_actual}."

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
    time.sleep(6)

def asistente():
    hablar("Hola, soy tu asistente de voz Luxx. ¿En qué puedo ayudarte?")
    while True:
        comando = escuchar().lower()
        if comando in respuestas:
            respuesta = respuestas[comando]
            if comando == "qué hora es":
                respuesta = obtener_hora()
            hablar(respuesta)
        else:
            hablar("Lo siento, no comprendo ese comando.")

if __name__ == "__main__":
    sr.pause_threshold = 0.5
    asistente()