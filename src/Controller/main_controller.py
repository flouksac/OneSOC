from Controller.host_controller import HostController
from Controller.parser import Parser
from View.main_view import View
from Model.main_model import Model


class Controller:
    def __init__(self):
        self.view = View()
        self.model = Model()
        self.parser = Parser(self.view, self.model)
        self.host_controller = HostController()

    def run(self):
        self.parser.parse_arguments()

        self.view.set_verbosity(self.parser.get_verbosity())

        self.view.display_banner()
        self.view.display_introduction()
        self.view.display_recommendation()

        self.view.display("Initialisation completed\n", level=4, context="Success")

        # vérifier que la commande est exécuté avec des permis d'administration
        if not self.host_controller.host.admin_rights_needed:
            self.view.display("This script should be run with admin rights, run it again with sudo or as administrator",
                              level=0, context="Fatal")
            exit(1)


        self.view.display("Chargement des configurations et des informations de la machine...", level=3, context="Info")

        try:
            self.model.init(self.parser.get_config_path())
        except Exception as e:
            self.view.display("Wrong Configuration File, is the path correct ?\n" + str(e), level=0, context="Fatal")
            exit(1)

        self.view.display("Informations récupérées avec succès !\n", level=3, context="Success")

        self.parser.parse()


        """
        self.view.display("Information of this device : \n",level=3,color="light_cyan")
        self.view.display_pretty_dict(self.model["Platform"].data, level=3)


        self.view.display(f"Contenu de la configuration : ", level=4)
        self.view.display_pretty_dict(self.model["Configuration"].data, level=4)

        self.view.display(f"\nContenu de la platform : ", level=4)
        self.view.display_pretty_dict(self.model["Platform"].data, level=4)
        """
