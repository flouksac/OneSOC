from abc import ABC, abstractmethod

from Controller.abstract_component_controller import AbstractComponentController


class AbstractComponentDockerController(AbstractComponentController,ABC):
    def __init__(self):
        super().__init__()
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