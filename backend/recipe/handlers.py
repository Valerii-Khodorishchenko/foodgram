from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.exceptions import ValidationError

MAX_SIZE_IMG = 1

class LimitFileSizeUploadHandler(FileUploadHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = 0

    def receive_data_chunk(self, raw_data, start):
        self.size += len(raw_data)
        if self.size > MAX_SIZE_IMG * 1024 * 1024:
            raise StopUpload(connection_reset=True)
        return raw_data

    def file_complete(self, file_size):
        if file_size > MAX_SIZE_IMG * 1024 * 1024:
            raise ValidationError(
                f'Максимальный размер файла {MAX_SIZE_IMG}MB)'
            )
