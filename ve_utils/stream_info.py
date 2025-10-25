class VideoContainer:
    def __init__(self):
        self.streams = []

    def add_streams(self, video_data):
        for stream in video_data["streams"]:
            stream_info = StreamInfo(stream)
            self.streams.append({
                "info": stream_info,
                "checked": True
            })

    def get_stream_titles(self):
        result_list = []
        for i, stream in enumerate(self.streams):
            checked_status = "[X] " if stream["checked"] else "[ ] "
            result_list.append(checked_status + str(stream["info"]))

        return result_list

    def toggle_stream(self, index):
        self.streams[index]["checked"] = not self.streams[index]["checked"]


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