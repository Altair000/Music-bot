import os
import telebot
import subprocess
from telebot import types
from flask import Flask, request
from manejadores.musica import search_music, download_song

# Inicializar el bot con tu token
TOKEN = '7985588609:AAEpNNIRU1uDWUbdFISF9Wx2Hmx2KbDmwQ4'
bot = telebot.TeleBot(TOKEN, threaded=False)
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# Inicializar Flask
app = Flask(__name__)

# Comando para iniciar el bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = types.KeyboardButton("Cuenta")
    markup.add(button)
    bot.send_message(message.chat.id, "¡Bienvenido! Usa /search para comenzar a descargar. El bot aún está en desarrollo.", reply_markup=markup)

# Buscar canciones y enviar resultados
def search_and_send_results(message, platform):
    query = message.text
    results = search_music(query, platform)

    if not results:
        bot.send_message(message.chat.id, "No se encontraron resultados con esas especificaciones.")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for track in results:
        button = types.InlineKeyboardButton(track['title'], callback_data=track['url'])
        markup.add(button)

    bot.send_message(message.chat.id, f"Resultados de la búsqueda para '{query}':", reply_markup=markup)

# Manejo de descarga cuando el usuario selecciona una canción
@bot.callback_query_handler(func=lambda call: True)
def handle_download(call):
    song_url = call.data
    user_id = call.message.chat.id
    song_file, thumbnail_image = download_song(song_url, user_id)

    with open(song_file, 'rb') as song:
        if thumbnail_image:
            bot.send_audio(call.message.chat.id, song, thumb=thumbnail_image, caption="Aquí tienes tu canción.")
        else:
            bot.send_audio(call.message.chat.id, song, caption="Aquí tienes tu canción.")

    os.remove(song_file)

# Función para manejar el comando de búsqueda
@bot.message_handler(commands=['search'])
def handle_search(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn_youtube = types.KeyboardButton("Buscar en YouTube")
    btn_soundcloud = types.KeyboardButton("Buscar en SoundCloud")
    markup.add(btn_youtube, btn_soundcloud)

    bot.send_message(message.chat.id, "¿Dónde quieres buscar la música?", reply_markup=markup)

# Manejar la respuesta del usuario para seleccionar la plataforma
@bot.message_handler(func=lambda message: message.text in ["Buscar en YouTube", "Buscar en SoundCloud"])
def handle_platform(message):
    platform = 'youtube' if message.text == "Buscar en YouTube" else 'soundcloud'
    msg = bot.send_message(message.chat.id, "Ingresa el nombre de la canción que deseas buscar.")
    bot.register_next_step_handler(msg, lambda m: search_and_send_results(m, platform))

@app.route("/")
def home():
    return "Bot funcionando"

# Ruta de Flask para el webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_update = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "OK", 200

# Establece la webhook al iniciar
@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    success = bot.set_webhook(url=WEBHOOK_URL + f"/{TOKEN}")
    if success:
        return "Webhook configurada correctamente", 200
    else:
        return "Fallo al configurar el webhook", 500

# Elimina la webhook si es necesario
@app.route("/delete_webhook", methods=["GET", "POST"])
def delete_webhook():
    bot.delete_webhook()
    return "Webhook eliminada correctamente", 200

@app.route("/install_ffmpeg", methods=["GET"])
def install_ffmpeg():
    subprocess.run(['apt', 'install', '-y', 'ffmpeg'])

if __name__ == "__main__":
    bot.infinity_polling()
    app.run(host="0.0.0.0", port=5000)
