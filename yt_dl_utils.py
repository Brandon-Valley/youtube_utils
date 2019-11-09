from __future__ import unicode_literals
import youtube_dl
import subprocess
# 
# https://www.youtube.com/channel/UCxfpjrP56c2ADNXK9RQ1zAg
# https://www.youtube.com/channel/UCB7Fk050iWZ2LBfgi9tro3A/videos
# https://www.youtube.com/channel/UCjXbR88mPHHcuBLHBGKmrjw
# https://www.youtube.com/watch?v=YvnPxqZEWVs


# downloads only audio in mp3 from youtube url, if no out_path is given, will download next to this file with vid title
def dl_audio_only(yt_url, out_path = None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
                                'key'             : 'FFmpegExtractAudio',
                                'preferredcodec'  : 'wav',
                                'preferredquality': '192',
                          }],
    }
    if out_path != None:
        ydl_opts['outtmpl'] = out_path

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])
        
        
# downloads yt vid at highest resolution
def download_youtube_vid(videourl, vid_save_path):
#     print(' in dl utils downloading yt vid to : ', path + '/' + save_title + '.mp4')#`````````````````````````````````````````````````
    cmd = 'youtube-dl -f best "' + videourl + '" -o ' + vid_save_path
#     print('cmd: ', cmd)#````````````````````````````````````````````````````````````````````````````````````
    subprocess.call(cmd, shell=True)
 
#     yt = YouTube(videourl)
#     yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
#     if not os.path.exists(path):
#         os.makedirs(path)
#     yt.download(path)
#      
#     print('in dl_utils, finding newest file_path...')#`````````````````````````````````````````````````````````````````````````````
#     # rename saved video
#     newest_file_path = file_system_utils.get_newest_file_path(path)
#     print('in dl_utils, renameing...')#`````````````````````````````````````````````````````````````````````````````
#     os.rename(newest_file_path, path + '//' + save_title + '.mp4')
# downloadYouTube('https://www.youtube.com/watch?v=zNyYDHCg06c', './videos/FindingNemo1')
        
        

# dl_audio_only('https://www.youtube.com/watch?v=hWTFG3J1CP8', 'test2.wav')
download_youtube_vid("https://www.youtube.com/watch?v=NaYg00lBKr4", 'test.mp4')






