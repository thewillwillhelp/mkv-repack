import curses
import os
import subprocess
import sys
import logging
import json
from ve_utils.selection import SelectionMode
from ve_utils.stream_info import VideoContainer

logging.basicConfig(
    level=logging.DEBUG,

    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="app.log",  # Optional: write to file
    filemode="w"         # Overwrite each run; use "a" to append
)

def get_streams(file_path):
    """
    Get the streams of a file using ffprobe.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=index,codec_type,codec_name:stream_tags",
                "-of",
                "json",
                # "default=noprint_wrappers=0",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        logging.error("This ffprobe result: %s", result.stdout.strip())
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logging.error("This is an error %s", str(exc))
        return str(exc)


def update_streams(inp_file, out_file, streams_remapping):
    try:
        # streams_remapping = [
        #     "-map", "0:v:0",
        #     "-map", "0:a:1",
        #     "-map", "0:s:3",
        #     "-map", "0:s:4",
        #     "-map", "0:s:1",
        # ]
        # logging.error("Update streams ffmpeg result: %s", streams_remapping)

        result = subprocess.run(
            [
                "ffmpeg", "-i", inp_file,
                *streams_remapping,
                "-c", "copy",
                "-disposition:s:0", "0",
                out_file,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        logging.error("Update streams ffmpeg result: %s", result.stdout.strip())
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logging.error("Update streams error %s", str(exc))
        return str(exc)




def split_by_width(text, width):
    return [text[i:i+width] for i in range(0, len(text), width)]


def print_long_text(stdscr, text):
    lines = text.splitlines()
    height, width = stdscr.getmaxyx()

    lines_offset = 0
    for i, line in enumerate(lines):
        sublines = split_by_width(line, width // 2 - 1)

        if i + lines_offset >= height - 2:
            break

        for subline in sublines:
            stdscr.addstr(i + lines_offset, width // 2, subline)
            lines_offset += 1


            if i + lines_offset >= height - 2:
                break

def draw_list(stdscr, list_data, selected_index, left_offset=0):
    height, width = stdscr.getmaxyx()

    for i, item in enumerate(list_data):
        if i + 2 >= height:
            break
        display_str = item
        if i == selected_index:
            stdscr.addstr(i + 2, left_offset, display_str, curses.A_REVERSE)
        else:
            stdscr.addstr(i + 2, left_offset, display_str)


def wrapped_main(stdscr):
    try:
        main(stdscr)
    except KeyboardInterrupt as exc:
        raise exc
    except Exception as exc:
        logging.error("Global error %s", str(exc))


def show_loading_status(stdscr, show=True):
    height, width = stdscr.getmaxyx()
    loading_text = "...processing"
    if not show:
        loading_text = len("...processing") * " "

    stdscr.addstr(
        height - 1, 0, loading_text,
    )
    stdscr.refresh()

def parse_video(file_path):
    if not file_path.endswith(".mkv"):
        return VideoContainer()

    streams_json = get_streams(file_path)
    streams_data = json.loads(streams_json)

    video_container = VideoContainer()
    video_container.add_streams(streams_data)

    return video_container


def main(stdscr):
    curses.curs_set(0)

    stdscr.clear()
    stdscr.refresh()

    current_path = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    selection = SelectionMode()
    video_container = VideoContainer()

    while True:
        height, width = stdscr.getmaxyx()

        stdscr.clear()

        # Display current path
        stdscr.addstr(0, 0, f"Current path: {current_path} {height}x{width}", curses.A_BOLD)

        # Get directory content
        try:
            dir_content = sorted(os.listdir(current_path))
        except FileNotFoundError:
            current_path = os.path.dirname(current_path)
            return

        selection.set_max("file_list", len(dir_content))
        selection.set_max("stream_info", len(video_container.get_stream_titles()))

        draw_list(stdscr, dir_content, selection.get_index("file_list"))
        draw_list(stdscr, video_container.get_stream_titles(), selection.get_index("stream_info"), left_offset=width // 2)

        new_file_name = "tmp"
        if selection.mode == "stream_info":
            file_name = dir_content[selection.get_index("file_list")]
            new_file_name = file_name.split(".")
            new_file_name.insert(-1, "_2")
            # new_file_name.append("_2")
            new_file_name = ".".join(new_file_name)

            stdscr.addstr(
                height - 2, 0, f"Save update (S): {new_file_name}",
            )

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selection.selection_up()
            video_container.move_dragged("up")

            if selection.mode == "file_list":
                selected_path = os.path.join(current_path, dir_content[selection.get_index("file_list")])
                video_container = parse_video(selected_path)
        elif key == curses.KEY_DOWN:
            selection.selection_down()
            video_container.move_dragged("down")

            if selection.mode == "file_list":
                selected_path = os.path.join(current_path, dir_content[selection.get_index("file_list")])
                video_container = parse_video(selected_path)
        elif key == curses.KEY_RIGHT or key == ord("\n"):
            if selection.mode == "file_list":
                selected_path = os.path.join(current_path, dir_content[selection.get_index("file_list")])
                if os.path.isdir(selected_path):
                    current_path = selected_path
                    selection.set_index("file_list", 0)
                else:
                    streams_json = get_streams(selected_path)
                    streams_data = json.loads(streams_json)

                    video_container = VideoContainer()
                    video_container.add_streams(streams_data)

                    selection.set_mode("stream_info")
            elif selection.mode == "stream_info":
                video_container.toggle_dragged(selection.get_index("stream_info"))

        elif key == curses.KEY_LEFT:
            if selection.mode == "file_list":
                current_path = os.path.dirname(current_path)
                selection.set_index("file_list", 0)
            selection.set_mode("file_list")
            video_container = VideoContainer()
        elif key == ord(" "):
            if selection.mode == "stream_info":
                video_container.toggle_stream(selection.get_index("stream_info"))
        elif key == ord("s"):
            if selection.mode != "stream_info":
                continue

            logging.warning("Output format: ")
            # for stream in video_container.streams:
            #     if stream["checked"]:
            #         logging.warning(str(stream["info"]))
            # logging.warning(" ".join(video_container.get_streams_remapping()))
            selected_path = os.path.join(current_path, dir_content[selection.get_index("file_list")])
            show_loading_status(stdscr)
            update_streams(selected_path, new_file_name, video_container.get_streams_remapping())
            # show_loading_status(stdscr)

        elif key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(wrapped_main)