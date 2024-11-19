from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
from Model.main_model import Model
from View.main_view import View


class Wazuh_Indexer_Controller(AbstractComponentServiceController):  # L'odre est important
    def __init__(self, options: list, model: Model, view: View):
        super().__init__(options, model, view)

    def info(self):
        pass

    def healthcheck(self):
        pass

    def install(self):
        self.view.display("ZAZA",level=0)

        pass

    def config(self):
        pass

    def repair(self):
        pass