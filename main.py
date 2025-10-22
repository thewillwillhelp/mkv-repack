import curses
import os
import subprocess
import sys

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
                "default=noprint_wrappers=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "NA"


def list_dir(stdscr, dir_content, selected_index):
    height, width = stdscr.getmaxyx()

    # Display directory content
    for i, item in enumerate(dir_content):
        if i + 2 >= height:
            break
        display_str = item
        if i == selected_index:
            stdscr.addstr(i + 2, 0, display_str, curses.A_REVERSE)
        else:
            stdscr.addstr(i + 2, 0, display_str)


def main(stdscr):
    """
    Main function to run the TUI.
    """
    curses.curs_set(0)

    stdscr.clear()
    stdscr.refresh()

    current_path = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    selected_index = 0

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

        list_dir(stdscr, dir_content, selected_index)

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
                streams = get_streams(selected_path)
                stdscr.addstr(
                    height - 2, 0, f"Streams for {dir_content[selected_index]}:"
                )
                # print(streams)
                lines = streams.splitlines()
                for i, line in enumerate(lines[:height]):
                    stdscr.addstr(i, width // 2, line[:(width // 2 - 1)])

                stdscr.addstr(height - 1, 0, str(len(streams)))
                stdscr.refresh()
                stdscr.getch()
        elif key == curses.KEY_LEFT:
            current_path = os.path.dirname(current_path)
            selected_index = 0
        elif key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(main)