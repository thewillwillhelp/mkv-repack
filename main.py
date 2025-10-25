import curses
import os
import subprocess
import sys
import logging
import json

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

class StreamInfo:
    def __init__(self, stream_data):
        stream_info = {
            "index": stream_data["index"],
            "codec_type": stream_data["codec_type"],
            "codec_name": stream_data["codec_name"],

        }

        if "tags" in stream_data:
            stream_info["tags"] = stream_data["tags"]
        else:
            stream_info["tags"] = {}

        self.container = stream_info

    def __str__(self):
        stream_info = self.container
        return (f"Stream {stream_info['index']} ({stream_info["codec_type"]}={stream_info['codec_name']}): " +
            f"{stream_info["tags"].get("title", '')} ({stream_info["tags"].get("language", '')})")


def main(stdscr):
    """
    Main function to run the TUI.
    """
    curses.curs_set(0)

    stdscr.clear()
    stdscr.refresh()

    current_path = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    selected_index = 0
    selected_streams_index = 0

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

        draw_list(stdscr, dir_content, selected_index)
        draw_list(stdscr, stream_lines, selected_streams_index, left_offset=width // 2)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(dir_content) - 1, selected_index + 1)
        elif key == curses.KEY_RIGHT or key == ord("\n"):
            selected_path = os.path.join(current_path, dir_content[selected_index])
            if os.path.isdir(selected_path):
                current_path = selected_path
                selected_index = 0
            else:
                streams_json = get_streams(selected_path)
                streams_data = json.loads(streams_json)
                stdscr.addstr(
                    height - 2, 0, f"Streams for {dir_content[selected_index]}:"
                )

                streams = []
                stream_lines = []
                for stream in streams_data["streams"]:
                    stream_info = StreamInfo(stream)
                    streams.append(stream_info)
                    stream_lines.append(
                        str(stream_info)
                    )
                    # stdscr.addstr(i + lines_offset, width // 2, line[:(width // 2 - 1)])

                stdscr.addstr(height - 1, 0, str(len(streams)))
                # stdscr.refresh()
                # stdscr.getch()
        elif key == curses.KEY_LEFT:
            current_path = os.path.dirname(current_path)
            selected_index = 0
        elif key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(wrapped_main)