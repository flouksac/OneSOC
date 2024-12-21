import time
from threading import Thread
from time import sleep

from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController



class Wazuh_Indexer_Controller(AbstractComponentServiceController):  # L'odre est important
    def __init__(self, options=None):
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
        # des erreurs dans les journaux ?
        # voir les configs
        pass

    def install(self):
        with self.view.display_progress(total_size=100) as progress:
            # Étape 1
            progress.update_main_task(advance=20, description="Initializing installation...")
            self.view.display("[INFO] [STEP 1/2] Initializing installation...")

            # Sous-tâche 1
            progress.add_sub_task(1, "Connecting to the server...")
            time.sleep(0.5)
            progress.update_sub_task(1, advance=1, description="Connecting to the server step 1...")
            time.sleep(0.5)
            progress.update_sub_task(1, advance=1, description="Connecting to the server step 2...")
            time.sleep(0.5)
            progress.update_sub_task(1, advance=1, description="Connecting to the server step 3...")

            # Étape 2
            progress.update_main_task(advance=80, description="Finalizing installation...")
            self.view.display("[INFO] [STEP 2/2] Finalizing installation...")

            # Sous-tâche 2
            progress.add_sub_task(2, "Updating configurations...")
            time.sleep(0.5)
            progress.update_sub_task(2, advance=1, description="Applying settings...")
            time.sleep(0.5)
            progress.update_sub_task(2, advance=1, description="Saving changes...")
            time.sleep(0.5)
            progress.update_sub_task(2, advance=1, description="Restarting services...")
            time.sleep(0.5)
            progress.update_sub_task(2, advance=1, description="Verification in progress...")

            # Supprime la barre principale
            progress.remove_main_task()

            # Message de fin
            self.view.display("[SUCCESS] Installation completed successfully!")

            # self.host -> quel os,version,.. ?
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
