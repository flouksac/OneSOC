from Controller.host_controller import HostController
from Controller.parser import Parser
from View.main_view import View
from Model.main_model import Model
from DesignPattern.singleton import Singleton

class Controller(metaclass=Singleton):
    
    def __init__(self):
        self.view = View()
        self.model = Model()
        self.host_controller = HostController()

    def run(self):
        parser = Parser()

        parser.parse_arguments()

        self.view.set_verbosity(parser.get_verbosity())

        self.view.display_banner()
        self.view.display_introduction()
        self.view.display_recommendation()
        
        """
        # vérifier que la commande est exécuté avec des permis d'administration
        if not self.host_controller.host.admin_rights_needed:
            self.view.display("This script should be run with admin rights, run it again as admin/sudo", level=0, context="Fatal")
            exit(1)
        """
        
        self.view.display("Initialization completed\n", level=4, context="Success")
        
        self.view.display("Configuration loading...\n", level=3, context="Info")

        try:
            self.model.init(parser.get_config_path())
        except Exception as e:
            self.view.display("Wrong Configuration File, is the path correct ?\n" + str(e), level=0, context="Fatal")
            exit(1)

        self.view.display("Configuration loaded with success !\n", level=3, context="Success")

        parser.parse() # identify if the args or ask user manually to run actions on given components





        """
        self.view.display("Information of this device : \n",level=3,color="light_cyan")
        self.view.display_pretty_dict(self.model["Platform"].data, level=3)


        self.view.display(f"Contenu de la configuration : ", level=4)
        self.view.display_pretty_dict(self.model["Configuration"].data, level=4)

        self.view.display(f"\nContenu de la platform : ", level=4)
        self.view.display_pretty_dict(self.model["Platform"].data, level=4)
        """
