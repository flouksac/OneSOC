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
        parser = argparse.ArgumentParser(description="OneSOC deployement script ")
        parser.add_argument('config', type=str, default="../config.yaml", nargs='?' ,
                            help="configuration file path -> default : '../config.yaml'")
        parser.add_argument('-v', '--verbosity', type=int, default=2, required=False,
                            help="verbosity level (specify an integer, default: 2)")

        self.args = parser.parse_args()

    def load_model(self, config_path):
        try :
            self.model["Platform"] = Platform()
            self.model["Configuration"] = YamlLoader(config_path)
        except Exception as e:
            self.view.display(str(e),0,"fatal")
            exit(1)

    def run(self):
        self.parse_arguments()
        self.view.set_verbosity(self.args.verbosity)

        self.view.display_banner()
        self.view.display_introduction()

        self.view.display("Initialisation completed\n", level=4, context="Success")


        # charge les infos de la machine dans la class self.model["Platform"]

        # vérifier que la commande est exécuté avec des permis d'administration


        # Charge le modèle et affiche des messages selon le niveau de verbosité
        self.view.display("Chargement du fichier de configuration...", level=3)
        self.load_model(self.args.config)
        self.view.display("Configuration chargée avec succès !", level=3,context="Success")

        self.view.display(f"Contenu de la configuration : {self.model["Configuration"].data}", level=2)

        print(self.model["Platform"].data)
