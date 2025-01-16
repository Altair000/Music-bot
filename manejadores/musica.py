import yt_dlp
from io import BytesIO
import requests

# Función para descargar la canción y obtener los datos relacionados
def download_song(url, user_id):
    # Definir opciones de yt-dlp para la descarga
    ydl_opts = {
        'quiet': True,  # Suprimir logs
        'format': 'bestaudio/best',  # Descargar la mejor calidad de audio
        'outtmpl': f'{user_id}_%(title)s.%(ext)s',  # Guardar el archivo con el ID del usuario y el título
        'noplaylist': True,  # No descargar listas de reproducción
        'extractaudio': True,  # Solo extraer audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Convertir a formato mp3
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'writethumbnail': True  # Descargar la miniatura de la canción (carátula)
    }

    # Usar yt-dlp para descargar la canción
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        song_file = f"{user_id}_{info_dict['title']}.mp3"
        thumbnail_url = info_dict.get('thumbnail', None)

    # Descargar la imagen de portada (carátula)
    if thumbnail_url:
        thumbnail_response = requests.get(thumbnail_url)
        thumbnail_image = BytesIO(thumbnail_response.content)
    else:
        thumbnail_image = None  # Si no hay imagen, se usará un valor predeterminado

    return song_file, thumbnail_image

# Función para buscar canciones en YouTube o SoundCloud
def search_music(query, platform):
    ydl_opts = {
        'quiet': False,  # Suprimir logs
        'extract_flat': True,  # No extraer contenido completo, solo metadata
        'playlistend': 10,  # Limitar los resultados a 10
    }

    # Definir los enlaces según la plataforma seleccionada
    if platform == 'youtube':
        ydl_opts['format'] = 'bestaudio/best'  # Buscar solo audio en YouTube
        search_url = f"ytsearch10:{query}"  # Búsqueda de YouTube
    elif platform == 'soundcloud':
        ydl_opts['format'] = 'bestaudio/best'  # Buscar solo audio en SoundCloud
        search_url = f"scsearch:{query}"  # Búsqueda de SoundCloud
    else:
        return []

    # Usar yt-dlp para buscar la música
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(search_url, download=False)
        tracks = []
        for entry in results['entries']:
            duration = entry.get('duration', 0)
            # Filtrar canciones que duren entre 2 y 10 minutos
            if 120 <= duration <= 600:  # 2 minutos = 120 segundos, 10 minutos = 600 segundos
                tracks.append({
                    'title': entry['title'],
                    'url': entry['url'],
                    'duration': duration
                })
        return tracks
