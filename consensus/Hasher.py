import hashlib


class Hasher:
    @staticmethod
    def hash(input_value):
        return hashlib.sha256(bytes(input_value, 'utf-8')).hexdigest()