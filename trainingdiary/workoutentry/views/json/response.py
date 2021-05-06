class TrainingDiaryResponse:

    STATUS = 'status'
    MESSAGES = 'messages'
    DATA = 'data'

    ERROR = 'error'
    SUCCESS = 'success'
    WARNING = 'warning'

    MSG_INFO = 'info'
    MSG_WARNING = 'warning'
    MSG_ERROR = 'error'

    @classmethod
    def error_response_dict(cls, message):
        response = TrainingDiaryResponse()
        response.set_status(cls.ERROR)
        response.add_message(cls.MSG_ERROR, message)
        return response.as_dict()

    def __init__(self, status=SUCCESS):
        self.__status = status
        self.__messages = list();
        self.__data = dict();

    def get_status(self):
        return self.__status

    def get_data(self):
        return self.__data

    def get_messages(self):
        return self.__messages

    def set_status(self, status):
        self.__status = status

    def add_message(self, type, text):
        self.__messages.append({'type': type, 'text': text})

    def add_data(self, key, value):
        self.__data[key] = value

    def as_dict(self):
        if self.__status == self.ERROR and len(self.__messages) == 0:
            # nothing been set to explain the error
            self.add_message(self.ERROR, 'Unexplained response. Contact Statera support with description of what you were doing that caused this. ')
        return {'status': self.__status,
                'messages': self.__messages,
                'data': self.__data}