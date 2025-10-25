import curses
import os
import subprocess
import sys
import logging
import json
from ve_utils.selection import SelectionMode
from ve_utils.stream_info import StreamInfo

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

        logging.error(f"This ffprobe result: {result.stdout.strip()}")
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        logging.error(f"This is an error {str(exc)}")
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
        logging.error(f"Global error {str(exc)}")




def main(stdscr):
    curses.curs_set(0)

    stdscr.clear()
    stdscr.refresh()

    current_path = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    selection = SelectionMode()

    stream_lines = []

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
        selection.set_max("stream_info", len(stream_lines))

        draw_list(stdscr, dir_content, selection.get_index("file_list"))
        draw_list(stdscr, stream_lines, selection.get_index("stream_info"), left_offset=width // 2)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selection.selection_up()
        elif key == curses.KEY_DOWN:
            selection.selection_down()
        elif key == curses.KEY_RIGHT or key == ord("\n"):
            selected_path = os.path.join(current_path, dir_content[selection.get_index("file_list")])
            if os.path.isdir(selected_path):
                current_path = selected_path
                selection.set_index("file_list", 0)
            else:
                streams_json = get_streams(selected_path)
                streams_data = json.loads(streams_json)
                stdscr.addstr(
                    height - 2, 0, f"Streams for {dir_content[selection.get_index("file_list")]}:"
                )

                streams = []
                stream_lines = []
                for stream in streams_data["streams"]:
                    stream_info = StreamInfo(stream)
                    streams.append(stream_info)
                    stream_lines.append(
                        str(stream_info)
                    )

                stdscr.addstr(height - 1, 0, str(len(streams)))
                selection.set_mode("stream_info")
        elif key == curses.KEY_LEFT:
            if selection.mode == "file_list":
                current_path = os.path.dirname(current_path)
                selection.set_index("file_list", 0)
            selection.set_mode("file_list")
            stream_lines = []
        elif key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(wrapped_main)