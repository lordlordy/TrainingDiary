from abc import ABC, abstractmethod


class TrainingDiaryResource(ABC):

    def required_file_fields(self):
        return []

    def required_post_fields(self):
        return []

    @abstractmethod
    def call_resource(self, request):
        pass