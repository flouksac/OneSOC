import argparse
import importlib

from termcolor import colored

from View.main_view import View
from Model.main_model import Model

class Controller:
    def __init__(self):
        self.view = View()
        self.model = Model()
        self.args = None

    def parse_arguments(self):
        parser = argparse.ArgumentParser(prog="OneSOC",description="OneSOC deployment script",add_help=False)

        group_positional_arguments = parser.add_argument_group(colored("Positional arguments","cyan"))
        group_positional_arguments.add_argument('config_path', type=str, default="./config.yaml", nargs='?' ,
                            help="configuration file path (default: %(default)s)")

        group_options = parser.add_argument_group(colored("Options","cyan"))
        group_options.add_argument('-h', '--help', action='help', help="Show this help message and exit")
        group_options.add_argument('-v', '--verbosity', type=int,choices=[0, 1, 2, 3, 4], default=2, required=False,
                            help="verbosity level (default: %(default)s)", metavar='Int')


        # List possibility
        group_list = parser.add_argument_group(colored("Listing flags","cyan"))
        group_list.add_argument('-lA','--list-action', action='store_true',
                            help="List all possible action")

        group_list.add_argument('-lO','--list-option',nargs='*', metavar='\"COMPONENT\"',type=str.lower, #action='store_true',
                            help="List all option for each action")

        group_list.add_argument('-lC','--list-component', action='store_true',
                            help="List all components that can be installed")



        # Actions "read only"
        group_read = parser.add_argument_group(colored("Read-only flags","cyan"))
        group_read.add_argument('--info', nargs='*',metavar='\"COMPONENT\"', help="Informations sur les composants installés")
        group_read.add_argument('--healthcheck', nargs='*', metavar='COMPONENT', help="Vérifie la santé des composants")


        # Action Installation
        group_install = parser.add_argument_group(colored("Installation flags","cyan"))
        group_install.add_argument('--install', nargs='+',metavar='\"COMPONENT\"', help="Installe un ou plusieurs composants")
        group_install.add_argument('--install-option', nargs='+',metavar='\"OPTION=VALUE\"', help="Options d'installation pour les composants")

        # Action Config
        group_config = parser.add_argument_group(colored("Configuration flags","cyan"))
        group_config.add_argument('--config', type=str, metavar='\"COMPONENT\"',help="Met à jour la configuration d'un composant")
        group_config.add_argument('--config-option', nargs='+',metavar='\"OPTION=VALUE\"', help="Options d'installation pour les composants")

        # Action Repair
        group_repair = parser.add_argument_group(colored("Reparation flags","cyan"))
        group_repair.add_argument('--repair', nargs='*',metavar='\"COMPONENT\"',
                            help="Répare un ou plusieurs composants ou tous les composants défectueux")

        self.args = parser.parse_args()


    def parse_action(self):


        # controlleur list, pcq j'aime bien:
        if self.args.list_action:
            self.view.list_action(self.model.get_all_actions())


        if self.args.list_option is not None:
            if len(self.args.list_option) == 0:
                self.view.list_option(self.model.get_all_options())
            else :
                components = self.model.get_options_of_components(self.args.list_option)
                if len(components) != len(self.args.list_option):
                    self.view.display("Wrong components name provided",level=0,context="Fatal")
                    exit(1)
                else :
                    self.view.list_option(components)

        if self.args.list_component:
            self.view.list_component(self.model.get_all_components())



        # appel de controlleur dynamique pour ci dessous:
        elif any([self.args.info, self.args.healthcheck, self.args.install, self.args.config, self.args.repair]):
            if self.args.info is not None:
                if len(self.args.info) == 0:

                    print("Informations pour tous les composants installés : [...]")
                else:
                    print(f"Informations pour les composants {', '.join(self.args.info)} : [...]")

            if self.args.healthcheck is not None:
                if len(self.args.healthcheck) == 0:
                    print("Vérification de la santé de tous les composants : [...]")
                else:
                    print(f"Vérification de la santé pour les composants {', '.join(self.args.healthcheck)} : [...]")

            if self.args.install:
                if not self.args.install:
                    print("Erreur : Aucun composant spécifié pour l'installation.")
                else:

                    for i in range(len(self.args.install)):
                        controller_instance = self.get_controller(self.args.install[i]) (self.args.install_option,self.model,self.view)
                        controller_instance.install()

            if self.args.config:
                print(f"Mise à jour de la configuration pour le composant {self.args.config}.")

            if self.args.repair is not None:
                if len(self.args.repair) == 0:
                    print("Réparation de tous les composants défectueux : [...]")
                else:
                    print(f"Réparation des composants {', '.join(self.args.repair)} : [...]")

        else : # modifier configuration
            self.ask_manually()

    def ask_manually(self):
        self.view.display("As no arguments has been passed, here is the manual menu :",level=0,color="light_cyan")

        # help
        allowed_actions = [action.name for action in self.model.get_all_actions()]

        chosen_actions = set()
        while len(chosen_actions) == 0:
            chosen_actions = self.view.display_selector_multiple("Which action do you want to do ? ",allowed_actions)

        print([allowed_actions[index] for index in chosen_actions])


        # for action in chose_actions ...
            # remplacer ça par la liste des composants qui peuvent etre installer sur la machine
            allowed_components = [component.name for component in self.model.get_all_components()]

            chosen_components = set()
            while len(chosen_components) == 0:
                chosen_components = self.view.display_selector_multiple("Which component do you want to do ? ",allowed_components)

            print([allowed_components[index] for index in chosen_components])
            # for component in components :
                # option 1, 2,3...

        # component
        # param

        pass

    def get_controller(self,string_user):  # -> renvoie dynamiquement la bonne class controller après l'avoir importé
        controller = None
        string_controller = (string_user.replace("-","_").lower() + "_controller")  # -> wazuh-indexer, Wazuh_Indexer_Controller

        possible_paths = [
            "Controller.ControllerService." + string_controller,
            "Controller.ControllerDocker." + string_controller
        ]

        for module_path in possible_paths:
            try:
                module = importlib.import_module(module_path)
                controller = getattr(module, string_controller.title())
                return controller

            except (ModuleNotFoundError, AttributeError) as e:
                continue

        self.view.display("Wrong Component name :"+string_user,level=0,context="Fatal")
        exit(1)


    def run(self):
        self.parse_arguments()
        self.view.set_verbosity(self.args.verbosity)

        self.view.display_banner()
        self.view.display_introduction()
        self.view.display_recommendation()


        self.view.display("Initialisation completed\n", level=4, context="Success")

        # vérifier que la commande est exécuté avec des permis d'administration


        self.view.display("Chargement des configurations et des informations de la machine...", level=3 ,context="Info")
        try:
            self.model.init(self.args.config_path)
        except Exception as e:
            self.view.display("Wrong Configuration File, is the path correct ?\n"+str(e),level=0,context="Fatal")
            exit(1)
        self.view.display("Informations récupérées avec succès !\n", level=3,context="Success")
        '''
        self.view.display("Information of this device : \n",level=3,color="light_cyan")
        self.view.display_pretty_dict(self.model["Platform"].data, level=3)


        self.view.display(f"Contenu de la configuration : ", level=4)
        self.view.display_pretty_dict(self.model["Configuration"].data, level=4)

        self.view.display(f"\nContenu de la platform : ", level=4)
        self.view.display_pretty_dict(self.model["Platform"].data, level=4)
        '''
        self.parse_action()


