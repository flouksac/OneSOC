from abc import ABC, abstractmethod

from Controller.abstract_component_controller import AbstractComponentController
from Model.main_model import Model
from View.main_view import View


class AbstractComponentDockerController(AbstractComponentController,ABC):
    def __init__(self,options:list):
        super().__init__(options)


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