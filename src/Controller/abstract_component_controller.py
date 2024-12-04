from abc import ABC, abstractmethod

from Controller.host_controller import HostController
from Model.main_model import Model
from View.main_view import View

class AbstractComponentController(ABC):
    def __init__(self,options:list):
        self.host = HostController().get_host()
        self.model = Model()
        self.view = View()
        self.component = None

    def parse_option(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def healthcheck(self):
        pass

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def repair(self):
        pass