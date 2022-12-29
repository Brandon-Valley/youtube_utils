from __future__ import unicode_literals
import os
from pathlib import Path
from pprint import pprint
import youtube_dl
import subprocess

from sms.logger import txt_logger
from sms.file_system_utils import file_system_utils as fsu
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

def _get_path_safe_str(in_str):
    """ # Replace any special chars that can't be in path with '_' """
    return in_str.translate({ord(c): "_" for c in ":*<>?|`"})

# def dl_vid_w_seperate_sub_file(vid_url, out_dir_path, replace_spaces_with = "_"):
#     v = 
#     out_template = os.path.join(out_dir_path)
#     cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=ttml]/best[ext=mp4]/best --write-auto-subs --sub-format ttml --no-playlist -o "test_dir/title.%(ext)s" https://www.youtube.com/watch?v=HVzdSPhcMUo'


# Could improve with threading
# Great 3 short vid test playlist: https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J
def dl_all_videos_in_playlist(playlist_url, out_dir_path, replace_spaces_with = "_", sub_style = "no_subs"):
    # https://www.codegrepper.com/tpc/python+download+youtube+playlist
    p = Playlist(playlist_url)

    print(f'Downloading all videos in playlist: {p.title}...')

    for video in p.videos:
        # Replace any special chars that can't be in path with '_'
        # Must do this here instead of the whole out_vid_path b/c will mess up C: drive on Windows
        path_safe_playlist_title = _get_path_safe_str(p.title)
        path_safe_video_title = _get_path_safe_str(video.title)

        # print(video.caption_tracks())
        # for caption_track in video.caption_tracks():
        #     print(f"{caption_track=}")
        # print(video.initial_data)
        # print(video.initial_data)

        # Very lazy way of doing things, should probably use pytube for everything
        # LATER should check if yt vid has actual subtitles before just downloading auto-subs
        if sub_style == "separate_file":
            out_template = os.path.join(out_dir_path, path_safe_playlist_title, path_safe_video_title, path_safe_video_title) + ".%(ext)s"

            if replace_spaces_with != None:
                out_template = out_template.replace(" ", replace_spaces_with)

            cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=ttml]/best[ext=mp4]/best --write-auto-subs --sub-format ttml --no-playlist -o "{out_template}" {video.watch_url}'
            print(f"Running cmd: {cmd}...")
            subprocess.call(cmd, shell = True)

        elif sub_style == "embed_subs":
            out_template = os.path.join(out_dir_path, path_safe_playlist_title, path_safe_video_title, path_safe_video_title) + ".%(ext)s"

            if replace_spaces_with != None:
                out_template = out_template.replace(" ", replace_spaces_with)

            cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=ttml]/best[ext=mp4]/best --write-auto-subs --embed-subs --no-playlist -o "{out_template}" {video.watch_url}'
            print(f"Running cmd: {cmd}...")
            subprocess.call(cmd, shell = True)

        elif sub_style == "no_subs":
            out_vid_path = os.path.join(out_dir_path, path_safe_playlist_title, path_safe_video_title + ".mp4")

            if replace_spaces_with != None:
                out_vid_path = out_vid_path.replace(" ", replace_spaces_with)

            # Create parent dir and nested parents if needed
            Path(out_vid_path).parent.mkdir(parents=True, exist_ok=True)

            print(f"Downloading {video.title} to {out_vid_path}...")
            st = video.streams.get_highest_resolution()
            st.download(filename=out_vid_path)

        else:
            raise Exception(f"ERROR: Invalid {sub_style=}")

# LATER if last sub hanging around too long, could use # https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
def _fix_ttml_sub_times(in_ttml_path):
    """ By Default, .ttml subs hang around too long """

    def _get_begin_and_end_time_strs_from_line(line):
        # Parse begin_str & end_str from line
        s_line_1 = line.split('<p begin="')[1]
        begin_str, s_line_2 = s_line_1.split('" end="')
        print(f"..{begin_str=}")
        end_str, s_line_3 = s_line_2.split('" style="')
        print(f"..{end_str=}")
        return begin_str, end_str

    og_ttml_lines = txt_logger.read(in_ttml_path)
    new_ttml_lines = og_ttml_lines

    subs_started = False

    prev_begin = None
    prev_end = None

    # for line_num, line in enumerate(og_ttml_lines):
    for line_num in range(len(og_ttml_lines)):

        print(f"{line_num=}")

        cur_line  = og_ttml_lines[line_num]
        next_line = og_ttml_lines[line_num + 1]

        # Move on if subs have not started yet, end if past subs
        if cur_line.startswith("<p begin="):
            subs_started = True
            # If last line
            if not next_line.startswith("<p begin="):
                print(f"On last line, exiting loop: {cur_line=}")
                break
        else:
            continue

        print(cur_line)

        cur_line_start_str, cur_line_end_str = _get_begin_and_end_time_strs_from_line(cur_line)
        print(f"..{cur_line_start_str=}")
        print(f"..{cur_line_end_str=}")
        next_line_start_str, next_line_end_str = _get_begin_and_end_time_strs_from_line(next_line)
        print(f"....{next_line_start_str=}")
        print(f"....{next_line_end_str=}")
   
        if next_line_start_str < cur_line_end_str:
            # replace current line's end time with next line's start time
            pre_end_split_str = cur_line.split(' end="')[0] + ' end="'
            post_end_split_str = '" style="' + cur_line.split('" style="')[1]
            new_line = f"{pre_end_split_str}{next_line_start_str}{post_end_split_str}"
            print(f"{new_line=}")
            new_ttml_lines[line_num] = new_line

    txt_logger.write(new_ttml_lines, in_ttml_path)

def re_time_subs_for_separate_sub_yt_playlist_dl_dir(in_dir_path):
    vid_sub_dir_path_l = fsu.get_dir_content_l(in_dir_path, "dir")

    for vid_sub_dir_path in vid_sub_dir_path_l:

        sub_file_path_l = list(Path(vid_sub_dir_path).glob("*.ttml"))

        if len(sub_file_path_l) == 0:
            print("no subs in ", vid_sub_dir_path)
            continue
        elif len(sub_file_path_l) > 1:
            raise Exception(f"Error: more than 1 - {sub_file_path_l}")

        sub_file_path = sub_file_path_l[0].__str__()

        print(f"Fixing timing for {sub_file_path=}")
        _fix_ttml_sub_times(sub_file_path)



if __name__ == "__main__":
    # # TEST_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J"
    # # TEST_OUT_DIR_PATH = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\youtube_utils\\ignore"
    # # # dl_all_videos_in_playlist(TEST_PLAYLIST_URL, TEST_OUT_DIR_PATH)
    # # dl_all_videos_in_playlist("https://www.youtube.com/playlist?list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ",
    # #                          "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\ignore\\tbs_pl_dl")
    # # out_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\youtube_utils\\ignore\\sub"
    # # cmd = "youtube-dl --write-description --write-info-json --write-annotations --write-sub --write-thumbnail https://www.youtube.com/watch?v=l0U7SxXHkPY"
    # # cmd = "youtube-dl --write-description --write-info-json --write-annotations --write-sub --write-thumbnail https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45"
    # # cmd = "youtube-dl --write-auto-sub --write-description --write-info-json --write-annotations --write-sub --write-thumbnail https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45"
    # out_dir_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\youtube_utils\\ignore\\herb_test"
    # Path(out_dir_path).mkdir(parents=True, exist_ok=True)
    # # cmd = f"youtube-dl --write-auto-sub --sub-format srt --write-description --write-info-json --write-annotations --write-sub --write-thumbnail https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45 -o {out_dir_path}"
    # # cmd = f"youtube-dl --write-auto-sub https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45 -o {out_dir_path}"
    # # cmd = f"youtube-dl --write-auto-sub --write-sub --sub-lang en,id --sub-format srt/sub/ssa/vtt/ass/best --convert-subs srt https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45 -o {out_dir_path}"
    # # cmd = f"youtube-dl --write-auto-sub --write-sub --sub-lang en --sub-format srt/sub/ssa/vtt/ass/best --embed-subs https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45 -o {out_dir_path}"
    # # cmd = f"youtube-dl --write-auto-sub https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45"
    # # cmd = f"youtube-dl --write-auto-sub https://www.youtube.com/watch?v=HVzdSPhcMUo"
    # # cmd = f"yt-dlp --write-auto-subs --sub-format srt --no-playlist https://www.youtube.com/watch?v=HVzdSPhcMUo"
    # # cmd = f"yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best --write-auto-subs --sub-format srt --no-playlist https://www.youtube.com/watch?v=HVzdSPhcMUo"
    # # cmd = f"yt-dlp -f bestvideo[ext=mp4] --write-auto-subs --sub-format ttml --no-playlist https://www.youtube.com/watch?v=HVzdSPhcMUo" # WORKS!!!!!!!!!!
    # # cmd = f'yt-dlp -f bestvideo[ext=mp4] --write-auto-subs --sub-format ttml --no-playlist -o "%(playlisttitle)s/%(title)s.%(ext)s" https://www.youtube.com/watch?v=HVzdSPhcMUo'
    # cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=ttml]/best[ext=mp4]/best --write-auto-subs --sub-format ttml --no-playlist -o "test_dir/title.%(ext)s" https://www.youtube.com/watch?v=HVzdSPhcMUo'
    # # cmd = f"yt-dlp --write-auto-subs --no-playlist https://www.youtube.com/watch?v=Roc89oOZOF4&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=45"
    # print(f"{cmd=}")
    # subprocess.call(cmd, shell=True)

    # # playlist_url = "https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J"
    # playlist_url = "https://www.youtube.com/playlist?list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ"
    # out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore"
    # dl_all_videos_in_playlist(playlist_url, out_dir_path, replace_spaces_with = "_", separate_sub_file = True)


    # ttml_test_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/vl_178__Family_Guy__Winning_Ticket_(Clip)___TBS__PERFECT_SUB_PLACEMENT_EXAMPLE/Family_Guy__Winning_Ticket_(Clip)___TBS_tsbfd_40.ttml"
    # _fix_ttml_sub_times(ttml_test_path)

    # re_time_subs_for_separate_sub_yt_playlist_dl_dir("C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/Family_Guy___TBS__OG_w_seperate_sub_file__time_fixed")

    # Great 3 short vid test playlist: https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J
    dl_all_videos_in_playlist(playlist_url = "https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J",
                                 out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/embed_subs_pl_test",
                                  replace_spaces_with = "_",
                                  sub_style = "embed_subs")


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






