import argparse
from Model.load_yaml import YamlLoader
from Model.platform import Platform

from View.view import View

class Controller:
    def __init__(self):
        self.view = View()
        self.model = {}
        self.args = None

    def parse_arguments(self):
        parser = argparse.ArgumentParser(prog="OneSOC",description="OneSOC deployment script",formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('config_path', type=str, default="../config.yaml", nargs='?' ,
                            help="configuration file path -> default : '../config.yaml'")

        parser.add_argument('-v', '--verbosity', type=int,choices=[0, 1, 2, 3, 4], default=2, required=False,
                            help="verbosity level (default: %(default)s)", metavar='Int')


        # List possibility
        parser.add_argument('-lA','--list-action', action='store_true',
                            help="List all possible action")

        parser.add_argument('-lO','--list-option', action='store_true',
                            help="List all option for each action")

        parser.add_argument('-lC','--list-component', action='store_true',
                            help="List all components that can be installed")

        parser.add_argument('-lIO','--list-install-option', nargs='*',
                            help="List all option of the given component to install")


        # Actions "read only"
        parser.add_argument('--info', nargs='*', help="Informations sur les composants installés")
        parser.add_argument('--healthcheck', nargs='*', help="Vérifie la santé des composants")

        # Action Installation
        parser.add_argument('--install', nargs='+', help="Installe un ou plusieurs composants")
        parser.add_argument('--install-option', nargs='+', help="Options d'installation pour les composants")

        # Action Config
        parser.add_argument('--config', type=str, help="Met à jour la configuration d'un composant")
        parser.add_argument('--config-option', nargs='+', help="Options d'installation pour les composants")

        # Action Repair
        parser.add_argument('--repair', nargs='*',
                            help="Répare un ou plusieurs composants ou tous les composants défectueux")

        self.args = parser.parse_args()

    def parse_action(self):
        if self.args.list_action:
            self.view.list_action()

        elif self.args.list_option:
            print("Liste des options disponibles pour les actions : [...]")

        elif self.args.list_install_option is not None:
            if len(self.args.list_install_option) == 0:
                print("Options d'installation générales pour tous les composants : [...]")

            else:
                print(f"Options d'installation pour les composants {', '.join(self.args.list_install_option)} : [...]")

        elif self.args.list_component:
            print("Liste des composants installables : [...]")



        elif any([self.args.info, self.args.healthcheck, self.args.install, self.args.apply_config, self.args.repair]):
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
                    print(
                        f"Installation des composants {', '.join(self.args.install)} avec les options {self.args.install_option}")

            if self.args.apply_config:
                print(f"Mise à jour de la configuration pour le composant {self.args.apply_config}.")

            if self.args.repair is not None:
                if len(self.args.repair) == 0:
                    print("Réparation de tous les composants défectueux : [...]")
                else:
                    print(f"Réparation des composants {', '.join(self.args.repair)} : [...]")

    def load_model(self, config_path):
        try :
            self.model["Platform"] = Platform()
            self.model["Configuration"] = YamlLoader(config_path)

            self.model["Action"] = None
            self.model["Options"] = None
            self.model["Components"] = None

        except Exception as e:
            self.view.display(str(e),0,"fatal")
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
        self.load_model(self.args.config_path)
        self.view.display("Informations récupérées avec succès !\n", level=3,context="Success")

        self.view.display("Information of this device : \n",level=3,color="light_cyan")
        self.view.display_pretty_dict(self.model["Platform"].data, level=3)


        self.view.display(f"Contenu de la configuration : ", level=5)
        self.view.display_pretty_dict(self.model["Configuration"].data, level=5)

        self.view.display(f"\nContenu de la platform : ", level=5)
        self.view.display_pretty_dict(self.model["Platform"].data, level=5)

        self.parse_action()