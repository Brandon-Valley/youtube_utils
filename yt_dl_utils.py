from __future__ import unicode_literals
import os
from pathlib import Path
from pprint import pprint
import youtube_dl
import subprocess

from sms.logger import txt_logger
from sms.file_system_utils import file_system_utils as fsu
#


from pytube import Playlist
from pytube import YouTube

# https://www.youtube.com/channel/UCxfpjrP56c2ADNXK9RQ1zAg
# https://www.youtube.com/channel/UCB7Fk050iWZ2LBfgi9tro3A/videos
# https://www.youtube.com/channel/UCjXbR88mPHHcuBLHBGKmrjw
# https://www.youtube.com/watch?v=YvnPxqZEWVs



####################################################################################################
# Should probably be in separate utility file/submodule
####################################################################################################
def _get_path_safe_str(in_str, replace_spaces_with = None):
    """ # Replace any special chars that can't be in path with '_' """
    path_safe_str = in_str.translate({ord(c): "_" for c in ":*<>?|`"})

    if replace_spaces_with != None:
        path_safe_str = path_safe_str.replace(" ", replace_spaces_with)

    return path_safe_str

# LATER REALLY SHOULD ADD THIS TO VID_EDIT_UTILS
def convert_subs(in_sub_path, out_sub_path):
    cmd = f'tt convert -i "{in_sub_path}" -o "{out_sub_path}"'
    print(f"Running {cmd}...")

    subprocess.call(cmd, shell=True)

# LATER REALLY SHOULD ADD THIS TO VID_EDIT_UTILS
def combine_mp4_and_sub_into_mkv(in_mp4_path, in_sub_path, out_mkv_path):
    """ Sub MAY need to be .srt """
    cmd = f'ffmpeg -i {in_mp4_path} -i {in_sub_path} -c copy -c:s copy {out_mkv_path}'
    print(f"Running {cmd}...")
    subprocess.call(cmd, shell=True)

# LATER REALLY SHOULD ADD THIS TO VID_EDIT_UTILS
def get_lone_ext_file_path_in_dir(dir_path, ext):
    """ Only works if there is exactly 1 file of given ext in dir non-recurs"""
    file_path_l = list(Path(dir_path).glob(f"*{ext}"))
    
    if len(file_path_l) == 0:
        raise Exception(f"Error: There are 0 files with ext `{ext}` in dir: {dir_path}")
    elif len(file_path_l) == 1:
        file_path = file_path_l[0].__str__()
        return file_path
    else:
        raise Exception(f"Error: There is more than 1 file with `{ext=}` in dir: {dir_path}, {file_path_l=}")


####################################################################################################
# Audio Only
####################################################################################################
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


####################################################################################################
# Download Individual Videos
####################################################################################################
def dl_yt_vid_and_sub__as__mp4_and_sub__w_vid_title(vid_url, out_parent_dir_path, replace_spaces_with = "_", return_val = "mp4_and_sub_path"):
    Path(out_parent_dir_path).mkdir(parents=True, exist_ok=True)

    vid = YouTube(vid_url)
    path_safe_vid_title = _get_path_safe_str(vid.title, replace_spaces_with)

    out_template = os.path.join(out_parent_dir_path, path_safe_vid_title) + ".%(ext)s"

    # if replace_spaces_with != None:
    #     out_template = out_template.replace(" ", replace_spaces_with)

    # DL with separate mp4 and srt sub file
    cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=ttml]/best[ext=mp4]/best --write-auto-subs --sub-lang "en.*" --sub-format ttml --no-playlist -o "{out_template}" {vid.watch_url}'
    print(f"Running cmd: {cmd}...")
    subprocess.call(cmd, shell = True)

    if return_val == "mp4_and_sub_path":
        # corrected_out_parent_dir_path = out_parent_dir_path.replace(" ", replace_spaces_with)
        out_mp4_path = get_lone_ext_file_path_in_dir(out_parent_dir_path, ".mp4")
        out_ttml_path = get_lone_ext_file_path_in_dir(out_parent_dir_path, ".en.ttml")
        return out_mp4_path, out_ttml_path

def dl_yt_vid_as_mkv_w_embedded_subs_w_vid_title(vid_url, out_parent_dir_path, replace_spaces_with = "_", re_time_subs = True):
    # dl with separate mp4 and srt sub file
    mp4_path, ttml_path = dl_yt_vid_and_sub__as__mp4_and_sub__w_vid_title(vid_url, out_parent_dir_path, replace_spaces_with)

    # re-time subs if needed
    if re_time_subs:
        _fix_ttml_sub_times(ttml_path)

    # Convert sub to srt 
    srt_sub_path = mp4_path.replace(".mp4", ".srt")

    convert_subs(ttml_path, srt_sub_path)

    # Combine mp4 and srt to make final mkv
    out_mkv_path = mp4_path.replace(".mp4", ".mkv")
    combine_mp4_and_sub_into_mkv(mp4_path, srt_sub_path, out_mkv_path)

    # Delete old files
    fsu.delete_if_exists(mp4_path)
    fsu.delete_if_exists(ttml_path)
    fsu.delete_if_exists(srt_sub_path)


# Could improve with threading
# Great 3 short vid test playlist: https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J
def dl_all_videos_in_playlist(playlist_url, out_dir_path, replace_spaces_with = "_", sub_style = "no_subs", vid_ext = "mp4"):
    """ fixing sub timing is outside the scope of this func """
    # https://www.codegrepper.com/tpc/python+download+youtube+playlist
    p = Playlist(playlist_url)

    print(f'Downloading all videos in playlist: {p.title}...')

    path_safe_playlist_title = _get_path_safe_str(p.title, replace_spaces_with)

    # playlist_dir_path = os.path.join(out_dir_path, path_safe_playlist_title).replace(" ", replace_spaces_with)
    playlist_dir_path = os.path.join(out_dir_path, path_safe_playlist_title)
    fsu.delete_if_exists(playlist_dir_path)
    Path(playlist_dir_path).mkdir(parents=True, exist_ok=True)

    for video in p.videos:
        # Replace any special chars that can't be in path with '_'
        # Must do this here instead of the whole out_vid_path b/c will mess up C: drive on Windows
        path_safe_video_title = _get_path_safe_str(video.title)
        # path_safe_video_title = _get_path_safe_str(video.title).replace(" ", replace_spaces_with)

        # print(video.caption_tracks())
        # for caption_track in video.caption_tracks():
        #     print(f"{caption_track=}")
        # print(video.initial_data)
        # print(video.initial_data)

        # Very lazy way of doing things, should probably use pytube for everything
        # LATER should check if yt vid has actual subtitles before just downloading auto-subs
        if sub_style == "separate_file__mp4_ttml":
            dl_dir_path = os.path.join(playlist_dir_path, path_safe_video_title)
            dl_yt_vid_and_sub__as__mp4_and_sub__w_vid_title(video.watch_url, dl_dir_path)
            # out_template = os.path.join(playlist_dir_path, path_safe_video_title, path_safe_video_title) + ".%(ext)s"

            # if replace_spaces_with != None:
            #     out_template = out_template.replace(" ", replace_spaces_with)

            # cmd = f'yt-dlp -f bestvideo[ext={vid_ext}]+bestaudio[ext=ttml]/best[ext={vid_ext}]/best --write-auto-subs --sub-lang "en.*" --sub-format ttml --no-playlist -o "{out_template}" {video.watch_url}'
            # print(f"Running cmd: {cmd}...")
            # subprocess.call(cmd, shell = True)

        elif sub_style == "embed_subs_as_mp4":
            out_template = os.path.join(playlist_dir_path, path_safe_video_title) + ".%(ext)s"

            # if replace_spaces_with != None:
            #     out_template = out_template.replace(" ", replace_spaces_with)

            cmd = f'yt-dlp -f bestvideo[ext={vid_ext}]+bestaudio[ext=ttml]/best[ext={vid_ext}]/best --write-auto-subs --sub-lang "en.*" --embed-subs --no-playlist -o "{out_template}" {video.watch_url}'
            print(f"Running cmd: {cmd}...")
            subprocess.call(cmd, shell = True)

        elif sub_style == "no_subs":
            out_vid_path = os.path.join(playlist_dir_path, path_safe_video_title + f".{vid_ext}")

            # if replace_spaces_with != None:
            #     out_vid_path = out_vid_path.replace(" ", replace_spaces_with)

            # Create parent dir and nested parents if needed
            Path(out_vid_path).parent.mkdir(parents=True, exist_ok=True)

            print(f"Downloading {video.title} to {out_vid_path}...")
            st = video.streams.get_highest_resolution()
            st.download(filename=out_vid_path)

        else:
            raise Exception(f"ERROR: Invalid {sub_style=}")

    return playlist_dir_path

####################################################################################################
# Work from playlist_dl_dir
####################################################################################################
def make_mkv_vid_w_embedded_subs_vids_from_separate_sub_yt_playlist_dl_dir(in_pl_dir_path, out_dir_path):
    print(f"{in_pl_dir_path=}")
    if not Path(in_pl_dir_path).is_dir():
        raise Exception(f"Error: Input dir does not exit: {in_pl_dir_path=}")

    fsu.delete_if_exists(out_dir_path)
    Path(out_dir_path).mkdir(parents=True, exist_ok=True)

    vid_dl_dir_path_l = fsu.get_dir_content_l(in_pl_dir_path, "dir")
    print(f"{in_pl_dir_path=}")
    print(f"{vid_dl_dir_path_l=}")

    for vid_dl_dir_path in vid_dl_dir_path_l:
        mp4_path = get_lone_ext_file_path_in_dir(vid_dl_dir_path, ".mp4")
        ttml_path = get_lone_ext_file_path_in_dir(vid_dl_dir_path, ".en.ttml")
        print(f"{mp4_path=}")

        # out_mkv_path & tmp_srt_path
        safe_vid_title = Path(vid_dl_dir_path).name
        print(f"{safe_vid_title=}")
        out_mkv_path = os.path.join(out_dir_path, safe_vid_title + ".mkv")
        tmp_srt_path = os.path.join(out_dir_path, safe_vid_title + ".srt")
        print(f"{out_mkv_path=}")
        fsu.delete_if_exists(out_mkv_path)
        fsu.delete_if_exists(tmp_srt_path)

        # make srt from ttml
        convert_subs(ttml_path, tmp_srt_path)

        # make mkv
        combine_mp4_and_sub_into_mkv(mp4_path, tmp_srt_path, out_mkv_path)

        # Check to make sure mkv created
        if not Path(out_mkv_path).is_file():
            raise Exception(f"Error: .mkv file does not exist after it should have been created: {out_mkv_path=}")

        # Delete srt
        fsu.delete_if_exists(tmp_srt_path)



####################################################################################################
# Fix timing for .ttml Auto-Subs
####################################################################################################

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

        sub_file_path_l = list(Path(vid_sub_dir_path).glob("*.en.ttml"))

        if len(sub_file_path_l) == 0:
            print("no subs in ", vid_sub_dir_path)
            continue
        elif len(sub_file_path_l) > 1:
            raise Exception(f"Error: more than 1 - {sub_file_path_l}")

        sub_file_path = sub_file_path_l[0].__str__()

        print(f"Fixing timing for {sub_file_path=}")
        _fix_ttml_sub_times(sub_file_path)

####################################################################################################
# Download Playlist
####################################################################################################

def dl_yt_playlist__fix_sub_times_convert_to_mkvs_w_embedded_subs(playlist_url, out_dir_path):
    """ Best for downloading YT playlist with auto-subs to be manually edited without losing subs """
    # Init out_dir_path
    fsu.delete_if_exists(out_dir_path)
    Path(out_dir_path).mkdir(parents=True, exist_ok=True)

    # Download playlist as separate .mp4 and .ttml files in their own dirs by vid in separate playlist dir
    tmp_pl_dl_dir_parent_path = Path(out_dir_path).parent
    tmp_pl_dl_dir_path = dl_all_videos_in_playlist(playlist_url, tmp_pl_dl_dir_parent_path, replace_spaces_with = "_", sub_style = "separate_file__mp4_ttml")
    print(f"Playlist videos with separate subtitle files have been downloaded to: {tmp_pl_dl_dir_path=}")

    # Correct .ttml sub times for all downloaded vids
    print(f"Fixing subtitle timing for downloaded playlist of YT vids: {tmp_pl_dl_dir_path=}")
    re_time_subs_for_separate_sub_yt_playlist_dl_dir(tmp_pl_dl_dir_path)

    # For each vid dir, convert re-timed .ttml to srt, then combine the .srt and .mp4 to make a .mkv with embedded subs
    make_mkv_vid_w_embedded_subs_vids_from_separate_sub_yt_playlist_dl_dir(in_pl_dir_path = tmp_pl_dl_dir_path,
                                                                           out_dir_path = out_dir_path)

    # Delete original playlist download
    fsu.delete_if_exists(tmp_pl_dl_dir_path)



if __name__ == "__main__":

    # re_time_subs_for_separate_sub_yt_playlist_dl_dir("C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/Family_Guy___TBS__OG_w_seperate_sub_file__time_fixed")

    # # Great 3 short vid test playlist: https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J
    # # dl_all_videos_in_playlist(playlist_url = "https://www.youtube.com/playlist?list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ",
    # dl_all_videos_in_playlist(playlist_url = "https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J",
    #                             #  out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/FG_TBS_pl_embed_auto_subs__just_files",
    #                              out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/test_sep_playlist3",
    #                             #  out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/FG_TBS_mkv_embedded_subs_re_timed",
    #                               replace_spaces_with = "_",
    #                               sub_style = "embed_subs_as_mkv")


    dl_yt_playlist__fix_sub_times_convert_to_mkvs_w_embedded_subs("https://www.youtube.com/playlist?list=PLfAIhxRGcgam-4wROzza_wfzdHoBJgj2J",
     out_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/all41test")

    # dl_yt_vid_as_mkv_w_embedded_subs_w_vid_title(vid_url = "https://www.youtube.com/watch?v=ORAymXqGREY&list=PLJBo3iyb1U0eNNN4Dij3N-d0rCJpMyAKQ&index=3",
    #  out_parent_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/INIV2_mkv_yt_dl_test",
    #   replace_spaces_with = "_")

    # convert_subs("C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/INIV_mkv_yt_dl_test/Invention_that_backfires_2.en.ttml",
    # "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/INIV_mkv_yt_dl_test/Invention_that_backfires_2.srt")
    # make_mkv_vid_w_embedded_subs_vids_from_separate_sub_yt_playlist_dl_dir("C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/Family_Guy___TBS__OG_w_seperate_sub_file__time_fixed",
    # "C:/Users/Brandon/Documents/Personal_Projects/youtube_utils/ignore/embed_pl_convert_test_dir")

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






