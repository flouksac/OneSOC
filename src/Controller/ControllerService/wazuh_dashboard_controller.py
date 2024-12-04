from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
 


class Wazuh_Dashboard_Controller(AbstractComponentServiceController):  # L'odre est important
    def __init__(self, options: list):
        super().__init__(options)

    def info(self):
        pass

    def healthcheck(self):
        pass

    def install(self):
        self.view.display("ZOZO",level=0)

        pass

    def config(self):
        pass

    def repair(self):
        pass