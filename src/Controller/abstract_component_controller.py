from abc import ABC, abstractmethod

from Controller.host_controller import HostController
from Model.main_model import Model
from View.main_view import View

class AbstractComponentController(ABC):
    def __init__(self, options=None):
        if options is None:
            options = []
        self.host = HostController().get_host()
        self.component_name=str(self.__class__.__name__.replace("_Controller","").replace("_","-"))
        self.model = Model()
        self.view = View()
        self.component = self.model.get_component_by_name(self.component_name)

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