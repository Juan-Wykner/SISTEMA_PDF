"""
Custom file upload handlers to prevent UTF-8 encoding issues with binary files.
"""
from django.core.files.uploadhandler import TemporaryFileUploadHandler


class BinarySafeUploadHandler(TemporaryFileUploadHandler):
    """
    Custom upload handler that ensures binary files are treated as binary data,
    preventing UTF-8 decoding errors.
    """
    
    def receive_data_chunk(self, raw_data, start):
        """
        Override to handle binary data without any text decoding.
        """
        # Ensure we treat the data as raw bytes, never try to decode as text
        if hasattr(raw_data, 'read'):
            # If it's a file-like object, read as bytes
            return raw_data.read()
        elif isinstance(raw_data, str):
            # If somehow we get a string, encode it to bytes
            return raw_data.encode('utf-8', errors='ignore')
        else:
            # Otherwise, treat as raw bytes
            return raw_data
    
    def file_complete(self, file_size):
        """
        Return the uploaded file without any text processing.
        """
        self.file.seek(0)
        return self.file