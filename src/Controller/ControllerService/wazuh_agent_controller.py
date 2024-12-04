 
from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
 


class Wazuh_Agent_Controller(AbstractComponentServiceController):  # L'odre est important
    def __init__(self, options: list):
        super().__init__(options)

    def info(self):
        super().info()



        
        # connaitre la version du support
        # parcourir les services en listant les installer
        # et version
        pass

    def healthcheck(self):
        # info
        # est ce que les containers sont sain
        # voir les configs
        pass

    def install(self):
        # self.host -> quel os,version,... ?
        # est ce que c'est compatible
        # non -> fatal
        # bof -> on demande confirmation/on essaye
        # oui -> on essaye d'installer

        # différer par gestionnaire de packet (APT VS DNF+YUM)

        # méthode apt ou methode dnf
        # on vérifie que c'est pas déjà installer
        # (info)
        #
        # mise a jour des paquets
        # installation des dépendances
        #
        # install
        #
        # healthcheck
        # -> si problème repair
        #
        # -> config selon les options
        # (config)
        #
        # renvoi un résumé

        self.view.display("ZAZA", level=0)

        pass

    def config(self):
        # healthcheck
        # on regarde les options de config
        # on change les options différentes
        # et on refait healtcheck
        pass

    def repair(self):
        # healtcheck
        # pour les infos pas bonnes
        # cas par cas on essaye de patch ou juste de conseiller des actions a l'utilisateur
        # healthcheck
        # ou exit
        pass
