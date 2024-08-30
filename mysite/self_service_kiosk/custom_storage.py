from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
import os


class SecurePDFStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'invoices'))
        super(SecurePDFStorage, self).__init__(*args, **kwargs)

    def get_valid_name(self, name):
        # Normalize the file name and ensure it doesn't contain any unsafe characters
        name = super(SecurePDFStorage, self).get_valid_name(name)
        if '..' in name or name.startswith('/'):
            raise SuspiciousFileOperation("Detected path traversal attempt")
        return name

    def _save(self, name, content):
        # Ensure the file is saved within the specified directory
        name = self.get_valid_name(name)
        return super(SecurePDFStorage, self)._save(name, content)

    def path(self, name):
        # Ensure the path is within the designated location
        path = super(SecurePDFStorage, self).path(name)
        if not path.startswith(self.location):
            raise SuspiciousFileOperation("Detected path traversal attempt")
        return path

    def url(self, name):
        # Hier wird der korrekte URL-Pfad zurückgegeben
        return os.path.join('/invoices', name)