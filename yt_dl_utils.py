from __future__ import unicode_literals
import youtube_dl



# downloads only audio in mp3 from youtube url, if no out_path is given, will download next to this file with vid title
def dl_audio_only(yt_url, out_path = None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
                                'key'             : 'FFmpegExtractAudio',
                                'preferredcodec'  : 'mp3',
                                'preferredquality': '192',
                          }],
    }
    
    if out_path != None:
        ydl_opts['outtmpl'] = out_path

    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])
        

# dl_audio_only('https://www.youtube.com/watch?v=hWTFG3J1CP8', 'test2.mp3')