import logging

class VideoContainer:
    def __init__(self):
        self.streams = []

    def get_next_stream_relative_index(self, stream_info):
        stream_type = stream_info["codec_type"]
        counter = 0

        for i, stream in enumerate(self.streams):
            if stream["info"].container["codec_type"] == stream_type:
                counter += 1

        return counter


    def add_streams(self, video_data):
        for stream in video_data["streams"]:
            stream_info = StreamInfo(stream)
            stream_info.container["relative_index"] = self.get_next_stream_relative_index(stream_info.container)
            self.streams.append({
                "info": stream_info,
                "checked": True,
                "dragged": False
            })

    def get_stream_titles(self):
        result_list = []
        for i, stream in enumerate(self.streams):
            dragged_status = "> " if stream["dragged"] else "  "
            checked_status = "[X] " if stream["checked"] else "[ ] "
            result_list.append(dragged_status + checked_status + str(stream["info"]))

        return result_list

    def toggle_stream(self, index):
        self.streams[index]["checked"] = not self.streams[index]["checked"]

    def toggle_dragged(self, index):
        self.streams[index]["dragged"] = not self.streams[index]["dragged"]

    def move_dragged(self, direction):
        dragged_stream = None
        dragged_index = None
        for i, stream in enumerate(self.streams):
            if stream["dragged"]:
                dragged_stream = stream
                dragged_index = i
                break

        if dragged_stream is None or dragged_index is None:
            return

        if direction == "up" and dragged_index > 0:
            self.streams[dragged_index] = self.streams[dragged_index - 1]
            self.streams[dragged_index - 1] = dragged_stream
        elif direction == "down" and dragged_index < len(self.streams) - 1:
            self.streams[dragged_index] = self.streams[dragged_index + 1]
            self.streams[dragged_index + 1] = dragged_stream

    def get_streams_remapping(self):
        remapping_list = []
        for stream in self.streams:
            if not stream["checked"]:
                continue
            remapping_list.append("-map")
            if stream["info"].container["codec_type"] == "video":
                remapping_list.append(f"0:v:{stream['info'].container['relative_index']}")

            if stream["info"].container["codec_type"] == "audio":
                remapping_list.append(f"0:a:{stream['info'].container['relative_index']}")

            if stream["info"].container["codec_type"] == "subtitle":
                remapping_list.append(f"0:s:{stream['info'].container['relative_index']}")

        return remapping_list




class StreamInfo:
    def __init__(self, stream_data):
        stream_info = {
            "index": stream_data["index"],
            "codec_type": stream_data["codec_type"],
            "codec_name": stream_data["codec_name"],
            "relative_index": None
        }

        if "tags" in stream_data:
            stream_info["tags"] = stream_data["tags"]
        else:
            stream_info["tags"] = {}

        self.container = stream_info

    def __str__(self):
        stream_info = self.container
        return (f"Stream {stream_info['index']}" +
            f"({stream_info["codec_type"]}{stream_info.get("relative_index", '-1')}={stream_info['codec_name']}): " +
            f"{stream_info["tags"].get("title", '')} ({stream_info["tags"].get("language", '')})" +
            f" - {stream_info["tags"].get("filename", '')}" +
            f" - {stream_info["tags"].get("DURATION", '')}")