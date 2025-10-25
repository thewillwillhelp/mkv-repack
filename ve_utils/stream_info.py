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