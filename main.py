import sys
import os
import subprocess
import shlex

def read_option(fn = int):
    try:
        option = fn(input())
        return option
    except KeyboardInterrupt as exc:
        raise KeyboardInterrupt from exc
    # pylint: disable=W0702
    except:
        print("Incorrect selection. Try again")
        return read_option()

def list_videos(working_dir):
    # result = subprocess.run(
    #     f"cd {working_dir} && ls -l",
    #     capture_output=True, text=True, shell=True
    # )

    files = os.listdir(os.path.expanduser(working_dir))
    # print("Files in working directory:", files)

    idx = 0
    for file_name in files:
        print(f" - {idx}) {file_name}")
        idx += 1


    print("Select file (O{N} - open directory, M{N} - media info):")
    selection = read_option(str)

    if selection[0] == "O":
        nested_dir = files[int(selection[1:])]
        list_videos(f"{working_dir}/{nested_dir}")

    if selection[0] == "M":
        file_name = files[int(selection[1:])]

        result = subprocess.run(
            f"ffprobe {shlex.quote(os.path.join(working_dir, file_name))}",
            capture_output=True, text=True, shell=True
        )
        print(result.stdout)
        #print(result.stderr)

        metadata_lines = result.stderr.split("\n")
        is_stream = False
        for line in metadata_lines:
            if line.strip().startswith("Stream"):
                is_stream = True

            if is_stream:
                print(line)



def main():
    working_dir = "~/"
    if len(sys.argv) > 1:
        working_dir = sys.argv[1]

    print("Working directory: " + working_dir)

    selection = 0
    while selection != 2:

        print("Select options: ")
        print("1) List videos")
        print("2) Exit")

        selection = read_option()

        if selection == 1:
            list_videos(working_dir)


if __name__ == '__main__':
    main()
