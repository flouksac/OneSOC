from abc import ABC, abstractmethod

from Controller.host_controller import HostController
from Model.main_model import Model, Component
from View.main_view import View

class AbstractComponentController(ABC):
    def __init__(self, options=None):
        if options is None:
            options = []
        self.host:HostController = HostController()
        self.component_name=str(self.__class__.__name__.replace("_Controller","").replace("_","-"))
        self.model = Model()
        self.view = View()
        self.component:Component = self.model.get_component_by_name(self.component_name)

    def parse_option(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def healthcheck(self):
        pass

    def install(self):
        for platform in self.component.supported_platform:
            try:
                if self.host.is_minimum_compatible(platform):
                    break
            except Exception:
                continue
        else:
            self.view.display("Your host is not compatible with the minimum requirements of this component",
                              context="fatal", indent=2, level=0)
            exit(1)

    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def repair(self):
        pass