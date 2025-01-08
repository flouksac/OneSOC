from abc import ABC, abstractmethod

from Controller.host_controller import HostController
from Model.ModelObjects.option import Option
from Model.main_model import Model, Component
from View.main_view import View

class AbstractComponentController(ABC):
    def __init__(self, options:list[Option]=None):

        self.host:HostController = HostController()
        self.component_name=str(self.__class__.__name__.replace("_Controller","").replace("_","-"))
        self.model = Model()
        self.view = View()
        self.component:Component = self.model.get_component_by_name(self.component_name)
        if not options:
            self.options = self.component.options
        else:
            self.options = []
            for option in options:
                if not self.component.is_option_supported(option):
                    self.view.display(
                        f"Option {option} is not supported by {self.component_name}, "
                        f"but if you choose to install many components in one go it may occur. "
                        f"If you are not sure, verify the options with flag -lO.",
                        context="warning",
                        indent=0,
                        level=2
                    )
                else:
                    self.options.append(option)

            for default_option in self.component.options:
                if not any(default_option.key == option.key.lower() for option in self.options):
                    self.options.append(default_option)

    def _get_option(self,option_name:str,autocomplete=False):
        if autocomplete:
            for option in self.options:
                if option.key == (self.component_name + "-" + option_name).lower():
                    return option
        else :
            for option in self.options:
                if option.key == option_name.lower():
                    return option




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