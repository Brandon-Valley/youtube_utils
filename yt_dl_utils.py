from __future__ import unicode_literals
import os
from pathlib import Path
import youtube_dl
import subprocess
#
# https://www.youtube.com/channel/UCxfpjrP56c2ADNXK9RQ1zAg
# https://www.youtube.com/channel/UCB7Fk050iWZ2LBfgi9tro3A/videos
# https://www.youtube.com/channel/UCjXbR88mPHHcuBLHBGKmrjw
# https://www.youtube.com/watch?v=YvnPxqZEWVs


from pytube import Playlist


# from SECRETS import youtube_api_key


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
# currently will not overwrite existing file, or even throw an error if there is one
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


def download_youtube_vids_from_vid_url_dest_path_d(vid_url_dest_path_d):
    for vid_url, dest_path in vid_url_dest_path_d.items():
        download_youtube_vid(vid_url, dest_path)

# Could improve with threading
def dl_all_videos_in_playlist(playlist_url, out_dir_path, replace_spaces_with = "_"):
    # https://www.codegrepper.com/tpc/python+download+youtube+playlist
    p = Playlist(playlist_url)

    print(f'Downloading all videos in playlist: {p.title}...')

    for video in p.videos:
        out_vid_path = os.path.join(out_dir_path, p.title, video.title + ".mp4")

        if replace_spaces_with != None:
            out_vid_path = out_vid_path.replace(" ", replace_spaces_with)

        # Create parent dir and nested parents if needed
        Path(out_vid_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {video.title} to {out_vid_path}...")
        st = video.streams.get_highest_resolution()
        st.download(filename=out_vid_path)



if __name__ == "__main__":
    TEST_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J"
    TEST_OUT_DIR_PATH = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\youtube_utils\\ignore"
    dl_all_videos_in_playlist(TEST_PLAYLIST_URL, TEST_OUT_DIR_PATH)


    print("done")
    # p = input("Enter th url of the playlist")

    # video.streams.first().download()


#     vids_dir_path = "C:\\Users\\mt204e\\Documents\\projects\\jira_best_practices\\videos\\jira_reports_tutorial_vids"

# #     save_path = "C:\\Users\\mt204e\\Documents\\projects\\jira_best_practices\\videos\\Jira_Reports_Tutorial__Burndown_Charts.mp4"
# #
# #     # dl_audio_only('https://www.youtube.com/watch?v=hWTFG3J1CP8', 'test2.wav')
# #     download_youtube_vid("https://www.youtube.com/watch?v=hH-q7rimHPY", vids_dir_path + '\\Epic_Report.mp4')

#     vid_url_dest_path_d = {
#                             'https://www.youtube.com/watch?v=gTOKqz7oW3g' : vids_dir_path + '\\Sprint_Report.mp4',
# #                             'https://www.youtube.com/watch?v=hH-q7rimHPY&list=PLaD4FvsFdarTnxd7YhUNbQceNEV7I_1Wo&index=3' : vids_dir_path + '\\Epic_Report.mp4',
#                             'https://www.youtube.com/watch?v=-h7YlVBnyKM' : vids_dir_path + '\\Velocity_Chart.mp4',
#                             'https://www.youtube.com/watch?v=Z8hM8tr4OAM' : vids_dir_path + '\\Control_Chart.mp4',
#                             'https://www.youtube.com/watch?v=CtVkZDy0ve8' : vids_dir_path + '\\Release_Burndown.mp4',
#                             'https://www.youtube.com/watch?v=U0xht5M_49A' : vids_dir_path + '\\Version_Report.mp4',
#                             'https://www.youtube.com/watch?v=9yYOaN68T-4' : vids_dir_path + '\\Average_Age_Report.mp4',

#                            }

#     download_youtube_vids_from_vid_url_dest_path_d(vid_url_dest_path_d)






