import subprocess
import time
from shutil import which
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
        with self.view.display_progress(f"Installation initialization of {self.component_name}...", indent=1,
                                        total_size=10) as progress:

            # ----------------------------------------------------------------------------
            # Étape 0 : Installation of curl and tar grep + dependencies
            # ----------------------------------------------------------------------------
            # Sur rpm : coreutils
            # Sur deb : debconf, adduser, procps, gnupg, apt-transport-https, ...
            progress.update_main(new_prefix="Installation of dependencies...")
            dependencies_subtask = progress.add_subtask("(1/3) Getting your host package manager...", 3)

            if self.host.package is None:
                self.view.display("No package manager found on this system", context="fatal", indent=2, level=0)
                exit(1)

            packages =  self.host.package  # package is a list

            if "apt" in packages:
                if which("apt"):
                    self.view.display("Debian based system", context="debug", indent=2, level=4)
                    package_path = "/usr/bin/apt"
                else:
                    self.view.display("Apt not found", context="fatal", indent=2, level=0)
                    exit(1)

            elif "yum" in packages or "dnf" in packages :
                if which("dnf"):
                    self.view.display("Redhat based system", context="debug", indent=2, level=4)
                    package_path = "/usr/bin/dnf"
                elif which("yum"):
                    self.view.display("Redhat based system", context="debug", indent=2, level=4)
                    package_path = "/usr/bin/yum"
                else:
                    self.view.display("Dnf and Yum not found", context="fatal", indent=2, level=0)
                    exit(1)
            else:
                self.view.display("Unknown package manager", context="fatal", indent=2, level=0)
                exit(1)

            progress.update_subtask(dependencies_subtask, new_prefix="(2/3) Installing dependencies..." )

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", package_path, "update"], check=True) # capture output !!!! do not want to print
                    subprocess.run(["sudo", package_path, "install", "-y", "curl", "tar", "grep", "debconf",
                                     "adduser", "procps", "gnupg", "apt-transport-https"], check=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}",context="fatal", indent=2, level=0)
                    raise


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "coreutils", "curl", "tar", "grep"],
                                   check=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}",context="fatal", indent=2, level=0)

            required_commands = ["curl", "tar", "grep"]
            for command in required_commands:
                if not which(command):
                    self.view.display(f"Dependency {command} is missing after installation", context="fatal", indent=2,
                                      level=0)
                    exit(1)

            progress.update_subtask(dependencies_subtask, new_prefix="(3/3) Dependencies installed successfully." )
            progress.remove_subtask(dependencies_subtask)


            # ----------------------------------------------------------------------------
            # Étape 1 : Récupérer certs tools (selon last version), récupérer config.yml,
            #           selon nos parametres (avoir un dict dans le fichier yaml)
            # ----------------------------------------------------------------------------
            # TODO: (placeholder) Télécharger / copier config.yml
            # TODO: Mettre à jour config.yml selon paramétrage (dict)
            progress.update_main(new_prefix="Installation of wazuh certifications tools...")
            wazuh_tools_subtask = progress.add_subtask("(1/7) Getting Wazuh certs tools...", 7)
            time.sleep(1)

            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(2/7) Retrieving certs tools..." )
            time.sleep(1)
            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(3/7) Certs tools retrieved..." )
            time.sleep(1)

            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(4/7) Retrieving config.yml..." )
            time.sleep(1)
            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(5/7) config.yml retrieved..." )
            time.sleep(1)

            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(6/7) Configuring config.yml..." )
            time.sleep(1)
            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(7/7) config.yml retrieved..." )
            progress.remove_subtask(wazuh_tools_subtask)


            # ----------------------------------------------------------------------------
            # Étape 2 : Création des certificats
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Generating certificates...")
            certificates_subtask = progress.add_subtask("(1/2) Generating certificates...", 2)

            # TODO: Générer les certificats avec Wazuh cert tools
            # TODO: dire de copier ces certificats !!!!!
            time.sleep(1)

            progress.update_subtask(certificates_subtask, new_prefix="(2/2)Certificates generated successfully..."  )
            progress.remove_subtask(certificates_subtask)


            # ----------------------------------------------------------------------------
            # Étape 3 : Installation du repository Wazuh
            # ----------------------------------------------------------------------------
            # installer le repository wazuh
            # rpm -> Import the GPG key.
            #     -> Add the repository.
            # deb -> Install the GPG key.
            #     -> Add the repository.
            #     -> Update the packages information.
            progress.update_main(new_prefix="Installation du repository Wazuh...")
            repo_subtask = progress.add_subtask("(1/3) Importing the GPG key...", total=3)
            # TODO: (placeholder) Sur RPM : Import GPG key, add repo
            #      Sur DEB : Install GPG key, add repo, apt-get update...
            time.sleep(1)

            progress.update_subtask(repo_subtask, new_prefix="(2/3) Adding the repository...")
            time.sleep(1)

            progress.update_subtask(repo_subtask, new_prefix="(3/3) Repository ready...")
            progress.remove_subtask(repo_subtask)


            # ----------------------------------------------------------------------------
            # Étape 4 : Installation du package Wazuh indexer
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Installing Wazuh indexer package...")

            install_subtask = progress.add_subtask("(1/1) Installing wazuh-indexer...", total=1)
            # TODO: (placeholder) Démarrer le téléchargement / installation via package manager
            time.sleep(1)

            progress.update_subtask(install_subtask, new_prefix="(1/1) Wazuh indexer installed!")
            progress.remove_subtask(install_subtask)


            # ----------------------------------------------------------------------------
            # Étape 5 : Configuration du Wazuh indexer
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Configuring Wazuh indexer...")

            config_subtask = progress.add_subtask("(1/1) Editing indexer configuration...", total=1)
            # TODO: (placeholder) Éditer /etc/wazuh-indexer/opensearch.yml (ou autre fichier de config)
            time.sleep(1)

            progress.update_subtask(config_subtask, new_prefix="(1/1) Wazuh indexer config updated!")
            progress.remove_subtask(config_subtask)

            # ----------------------------------------------------------------------------
            # Étape 6 : Appliquer les certificats (commandes successives)
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Applying certificates...")

            cert_subtask = progress.add_subtask("(1/1) Copying / applying certs...", total=1)
            # TODO: (placeholder) Copier / lier les certificats générés
            time.sleep(1)

            progress.update_subtask(cert_subtask, new_prefix="(1/1) Certificates applied successfully!")
            progress.remove_subtask(cert_subtask)


            # ----------------------------------------------------------------------------
            # Étape 7 : Lancement du service Wazuh (systemd ou sysv)
            # ----------------------------------------------------------------------------
            # On avance la barre principale (8/10).
            progress.update_main(new_prefix="Starting Wazuh indexer service...")

            service_subtask = progress.add_subtask("(1/1) Starting service...", total=1)
            # TODO: (placeholder) systemctl enable wazuh-indexer && systemctl start wazuh-indexer
            time.sleep(1)

            progress.update_subtask(service_subtask, new_prefix="(1/1) Service started!")
            progress.remove_subtask(service_subtask)


            # ----------------------------------------------------------------------------
            # Étape 8 : Initialisation du cluster
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Initializing Wazuh cluster...")

            init_subtask = progress.add_subtask("(1/1) Launching indexer-security-init.sh...", total=1)
            # TODO: (placeholder) /usr/share/wazuh-indexer/bin/indexer-security-init.sh
            time.sleep(1)

            progress.update_subtask(init_subtask, new_prefix="(1/1) Cluster initialized!")
            progress.remove_subtask(init_subtask)


            # ----------------------------------------------------------------------------
            # Étape 9 : Health-check (vérification)
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Performing final health check...")
            # TODO: healtcheck verif avec curl -k -u admin:admin https://<WAZUH_INDEXER_IP_ADRESS>:9200
            # TODO: curl -k -u admin:admin https://<WAZUH_INDEXER_IP_ADDRESS>:9200/_cat/nodes?v

            health_subtask = progress.add_subtask("(1/1) Checking cluster health...", total=1)
            time.sleep(1)
            progress.update_subtask(health_subtask, new_prefix="(1/1) Health check done!")
            progress.remove_subtask(health_subtask)


            progress.update_main(new_prefix="Installation completed!")

            """
            if self.host.package == "deb":
                self.view.display("Debian based system",context="debug",indent=2,level=4)
                # try apt from /usr/bin/apt ...

            elif self.host.package == "rpm":
                # d'abord yum, sinon dnf, sinon zypper
                self.view.display("Redhat based system",context="debug",indent=2,level=4)


            else :
                self.view.display("Unknown package manager",context="debug",indent=2,level=4)
                exit(1)
            """

            # self.host -> quel os,version,.. ?
            #self.model.get_component_by_name( self.component_name)


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
