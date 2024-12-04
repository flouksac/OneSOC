from abc import ABC, abstractmethod

from Controller.abstract_component_controller import AbstractComponentController
from Model.main_model import Model
from Utils.service_info import find_service
from View.main_view import View


class AbstractComponentServiceController(AbstractComponentController,ABC): # L'odre est important
    def __init__(self,options:list):
        super().__init__(options)


    def info(self):
        if find_service(self.component_name):
            
            print(f"{self.component_name} is on the device")        
        else:
            print(f"{self.component_name} isn't on the device")

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