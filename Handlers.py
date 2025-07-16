from abc import ABC, abstractmethod

class BaseIOHandler(ABC):
    @abstractmethod
    def get_user_input(self, *args, **kwargs):
        pass

    @abstractmethod
    def display_output(self, *args, **kwargs):
        pass

class CLIIOHandler(BaseIOHandler):
    def get_user_input(self, message):
        x = input(message)
        return x


    def display_output(self, *args, **kwargs):
        for i in args:
            print(i)
        for key, value in kwargs.items():
            print (f"{key}:{value}")

