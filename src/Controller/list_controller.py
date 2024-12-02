from Controller.host_controller import HostController
from View.main_view import View
from Model.main_model import Model


class ListController:
    def __init__(self) -> None:
        self.model = Model()
        self.view = View()
        self.host = HostController()
        
    def get_actions(self):
        self.view.list_action(self.model.get_all_actions())
    
    def get_options(self,options:list[str]=[]):
        
        
        if len(options) == 0: 
            self.view.list_option(self.model.get_all_options())
        else:
            components = self.model.get_options_of_components(options)
            if len(components) != len(options):
                self.view.display("Wrong components name provided", level=0, context="Fatal")
                exit(1)
            else:
                self.view.list_option(components)
    
    def get_components(self):
        # afficher uniquement les composants compatible avec la machine
        self.view.list_component(self.model.get_all_components())
