class SelectionMode:
    def __init__(self):
        self.mode = "file_list"
        self.selection = {
            "file_list": {
                "index": 0,
                "max": 0
            },
            "stream_info": {
                "index": 0,
                "max": 0
            },
        }

    def get_index(self, mode):
        return self.selection[mode]["index"]

    def set_index(self, mode, index):
        self.selection[mode]["index"] = index

    def set_max(self, mode, max_value):
        self.selection[mode]["max"] = max_value

    def set_mode(self, mode):
        self.mode = mode

    def selection_up(self):
        selected_index = self.selection[self.mode]["index"]
        selected_index = max(0, selected_index - 1)
        self.selection[self.mode]["index"] = selected_index

    def selection_down(self):
        selected_index = self.selection[self.mode]["index"]
        selected_index = min(self.selection[self.mode]["max"] - 1, selected_index + 1)
        self.selection[self.mode]["index"] = selected_index
