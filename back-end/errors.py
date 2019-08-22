class ServiceError(Exception):

    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload

    def __str__(self):
        return str(self.message)


class ConfigurationError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class ServerError(Exception):

    def __init__(self, message, status=None):
        self.message = message
        self.status = status

    def __str__(self):
        return str(self.message)
