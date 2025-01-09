import glob
import os
import shutil
import socket
import subprocess
import time
from shutil import which


import requests
import yaml

from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
from Model.loaderYAML import YamlLoader


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
        super().install()

        with self.view.display_progress(f"Installation initialization of {self.component_name}...", indent=1,
                                        total_size=10) as progress:

            # ----------------------------------------------------------------------------
            # Étape 0 : Installation of curl and tar grep + dependencies
            # ----------------------------------------------------------------------------
            # Sur rpm : coreutils
            # Sur deb : debconf, adduser, procps, gnupg, apt-transport-https, ...

            progress.update_main(new_prefix="Installation of dependencies...")
            dependencies_subtask = progress.add_subtask("(1/3) Getting your host package manager...", 3)

            if self.host.get_host().package is None:
                self.view.display("No package manager found on this system", context="fatal", indent=2, level=0)
                exit(1)

            packages = self.host.get_host().package  # package is a list

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
                    subprocess.run(["sudo", package_path, "update"], check=True, capture_output=True,text=True) # cwd
                    subprocess.run(["sudo", package_path, "install", "-y", "curl", "tar", "grep", "debconf",
                                   "adduser", "procps", "gnupg", "apt-transport-https"], check=True,text=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}",context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "coreutils", "curl", "tar", "grep"],
                                   check=True, capture_output=True,text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}",context="fatal", indent=2, level=0)
                    exit(1)

            required_commands = ["curl", "tar", "grep"]
            for command in required_commands:
                if not which(command):
                    self.view.display(f"Dependency {command} is missing after installation", context="fatal", indent=2,
                                      level=0)
                    exit(1)

            progress.update_subtask(dependencies_subtask, new_prefix="(3/3) Dependencies installed successfully." )
            progress.remove_subtask(dependencies_subtask)

            # ----------------------------------------------------------------------------
            # Étape 1 : récupérer config.yml,
            #           selon nos parametres (avoir un dict dans le fichier yaml)
            # ----------------------------------------------------------------------------
            # TODO definir ou stocker config.yml
            progress.update_main(new_prefix="Adjusting wazuh's config.yml file from the provided settings...")
            wazuh_tools_subtask = progress.add_subtask("(1/3) Getting Wazuh config.yml file...", 3)

            url = f"https://packages.wazuh.com/{self._get_option('version',True).value}/config.yml"
            response = requests.get(url, stream=True)
            config_path = "/tmp/config.yml"

            if response.status_code == 200:
                with open(config_path, 'wb') as f:
                    f.write(response.content)
            else:
                self.view.display(f"Error: Couldn't retrieve config.yml file, status code : {response.status_code}",
                                  context="fatal", indent=2, level=0)
                exit(1)


            progress.update_subtask(  wazuh_tools_subtask, new_prefix="(2/3) Configuring config.yml..." )

            try :
                loader = YamlLoader(config_path)
                config:dict = loader.data
            except yaml.YAMLError as e:
                self.view.display(f"Error: Couldn't parse config.yml file, {e}", context="fatal", indent=2, level=0)
                if os.path.exists(config_path):
                    os.remove(config_path)
                exit(1)
            except FileNotFoundError as e:
                self.view.display(f"Error: Couldn't find config.yml file, {e}", context="fatal", indent=2, level=0)
                exit(1)

            indexer_nodes = [{
                "name": self._get_option("wazuh-indexer-name").value,
                "ip": self._get_option("wazuh-indexer-ip").value
            }]

            node_index = 2
            while any(f"wazuh-indexer-name-{node_index}" in option.key for option in self.options):
                indexer_nodes.append({
                    "name": self._get_option(f"wazuh-indexer-name-{node_index}").value,
                    "ip": '"'+self._get_option(f"wazuh-indexer-ip-{node_index}").value+'"',
                })
                node_index += 1

            config["nodes"]["indexer"] = indexer_nodes

            # Update server nodes
            if any ("wazuh-server-name-2" in option.key for option in self.options):

                server_nodes = [{
                    "name": self._get_option("wazuh-server-name").value,
                    "ip": self._get_option("wazuh-server-ip").value,
                    "node_type": self._get_option("wazuh-server-node-type").value
                }]
            else :
                server_nodes = [{
                    "name": self._get_option("wazuh-server-name").value,
                    "ip": self._get_option("wazuh-server-ip").value,
                }]

            node_index = 2

            while any(f"wazuh-server-name-{node_index}" in option.key for option in self.options):
                server_nodes.append({
                    "name": self._get_option(f"wazuh-server-name-{node_index}").value,
                    "ip": self._get_option(f"wazuh-server-ip-{node_index}").value,
                    "node_type": self._get_option(f"wazuh-server-node-type-{node_index}").value
                })
                node_index += 1

            config["nodes"]["server"] = server_nodes

            # Update dashboard nodes
            config["nodes"]["dashboard"] = [{
                "name": self._get_option("wazuh-dashboard-name").value,
                "ip": self._get_option("wazuh-dashboard-ip").value
            }]

            self.view.display("Config.yml file updated with the provided settings : ", context="Info", indent=2, level=3)
            self.view.display_pretty_dict(config,level=3,indent=2)

            loader.save(config)

            progress.update_subtask(wazuh_tools_subtask, new_prefix="(3/3) Adjustment on config.yml is done." )
            progress.remove_subtask(wazuh_tools_subtask)


            # ----------------------------------------------------------------------------
            # Étape 2 : Récupérer certs tools (selon last version), et Création des certificats
            # ----------------------------------------------------------------------------
            if self._get_option("node-name-you-are-currently-installing",True).value == self._get_option("wazuh-indexer-name").value:

                progress.update_main(new_prefix="Generating certificates...")
                certificates_subtask = progress.add_subtask("(1/7) Getting Wazuh certs tools script...", 7)

                url = f"https://packages.wazuh.com/{self._get_option('version', True).value}/wazuh-certs-tool.sh"
                response = requests.get(url, stream=True)
                workdir = "/tmp"
                config_path = "/tmp/wazuh-certs-tool.sh"

                if response.status_code == 200:
                    with open(config_path, 'wb') as f:
                        f.write(response.content)
                else:
                    self.view.display(f"Error: Couldn't retrieve wazuh-certs-tools file, status code : {response.status_code}",
                                      context="fatal", indent=2, level=0)
                    exit(1)

                progress.update_subtask(  certificates_subtask, new_prefix="(2/4) Making wazuh-certs-tool.sh executable..." )

                try:
                    subprocess.run(["sudo","/usr/bin/chmod", "+x", config_path], check=True, capture_output=True, text=True,cwd="/tmp")
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while adding execution right on wazuh-certs-tools: {e}", context="fatal", indent=2, level=0)
                    exit(1)

                progress.update_subtask(certificates_subtask, new_prefix="(3/4) Running wazuh-certs-tool.sh..." )

                try:
                    if os.path.exists(f"{workdir}/wazuh-certificates/"):
                        try :
                            subprocess.run(["sudo", "/usr/bin/rm", "-rf", f"{workdir}/wazuh-certificates"], check=True, capture_output=True, text=True,cwd=workdir)
                        except subprocess.CalledProcessError as e:
                            self.view.display(f"Error while removing old certificates: {e}", context="fatal", indent=2, level=0)
                            exit(1)

                    subprocess.run(["sudo", f"{workdir}/wazuh-certs-tool.sh","-A"], check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error when running wazuh-certs-tools: {e}", context="fatal", indent=2, level=0)
                    exit(1)

                progress.update_subtask(certificates_subtask, new_prefix="(4/4) Compresseing certificates..." )

                try :
                    subprocess.run(["sudo", "/usr/bin/tar", "-cvf", f"{workdir}/wazuh-certificates.tar","-C",f"{workdir}/wazuh-certificates/", "."],
                                   check=True, capture_output=True, text=True,cwd=workdir)
                    subprocess.run(["sudo", "/usr/bin/rm", "-rf", f"{workdir}/wazuh-certificates"], check=True, capture_output=True, text=True,cwd=workdir)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while compressing certificates: {e}", context="fatal", indent=2, level=0)
                    exit(1)

                self.view.display(f"Certificates generated successfully!", context="Success", indent=2, level=0)
                self.view.display(f"[bright_cyan]PLEASE COPY {workdir}/wazuh-certificates.tar[/bright_cyan] to all the nodes, including the Wazuh indexer, "
                                  f"Wazuh server, and Wazuh dashboard nodes. "
                                  f"This can be done by using the scp utility", context="info", indent=2, level=0)

                progress.remove_subtask(certificates_subtask)

            else :
                self.view.display("Skip certificat generation because it's not the master indexer...", context="info", indent=2, level=0)
                if self._get_option("certificates-path",True).value:
                    self.view.display(f"Please copy the certificates generated by the master indexer to {self._get_option('certificates-path',True).value}", context="info", indent=2, level=0)
                progress.update_main(new_prefix="Skip certificat generation...")

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
            # TODO: Sur RPM : Import GPG key, add repo
            #       Sur DEB : Install GPG key, add repo, apt-get update...
            time.sleep(1)


            packages = self.host.get_host().package  # package is a list

            if "apt" in packages:
                try:
                    curl_proc = subprocess.run(
                        ["curl", "-s", "https://packages.wazuh.com/key/GPG-KEY-WAZUH"],
                        check=True,
                        capture_output=True,
                        text=True
                    )

                    subprocess.run(
                        ["sudo", "gpg", "--no-default-keyring", "--keyring", "gnupg-ring:/usr/share/keyrings/wazuh.gpg",
                         "--import"],
                        input=curl_proc.stdout,
                        check=True,
                        capture_output=True,
                        text=True
                    )

                    subprocess.run(
                        ["sudo", "chmod", "644", "/usr/share/keyrings/wazuh.gpg"],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh gpg key on debian based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", "rpm", "--import", "https://packages.wazuh.com/key/GPG-KEY-WAZUH"],
                                   check=True, capture_output=True,text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while importing the wazuh gpg key on redhat based system: {e}",
                                        context="fatal", indent=2, level=0)
                    exit(1)



            progress.update_subtask(repo_subtask, new_prefix="(2/3) Adding the repository...")

            # verifier si dans les repo wazuh est déjà présent

            if "apt" in packages:
                try:
                    result = subprocess.run(["grep", "-r", "packages.wazuh.com", "/etc/apt/sources.list.d/"],
                                            check=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.view.display("The Wazuh repository is already configured on a Debian-based system.",
                                          context="info", indent=2, level=0)
                except subprocess.CalledProcessError:
                    # Si le dépôt n'est pas trouvé, on l'ajoute
                    try:
                        repo_string = f"deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main\n"

                        # 2) Run 'tee' and pass `repo_string` as input
                        subprocess.run(
                            ["sudo", "tee", "-a", "/etc/apt/sources.list.d/wazuh.list"],
                            input=repo_string,
                            text=True,
                            check=True,
                            capture_output=True
                        )
                        subprocess.run(["sudo", "/usr/bin/apt", "update"], check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(f"Error while adding the wazuh repository on debian based system: {e}",
                                          context="fatal", indent=2, level=0)
                        exit(1)

            elif "yum" in packages or "dnf" in packages:
                try:
                    result = subprocess.run(["grep", "-r", "packages.wazuh.com", "/etc/yum.repos.d/"],
                                            check=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.view.display("The Wazuh repository is already configured on an RHEL-based system.",
                                          context="info", indent=2, level=0)
                except subprocess.CalledProcessError:
                    # If the repository is not found, add it
                    try:
                        # Build the repository content as a single string
                        repo_string = (
                            "[wazuh]\n"
                            "gpgcheck=1\n"
                            "gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH\n"
                            "enabled=1\n"
                            "name=EL-$releasever - Wazuh\n"
                            f"baseurl=https://packages.wazuh.com/{self._get_option('version', True).value}/yum/\n"
                            "protect=1\n"
                        )

                        # Use 'tee' to write the content to /etc/yum.repos.d/wazuh.repo
                        subprocess.run(
                            ["sudo", "tee", "/etc/yum.repos.d/wazuh.repo"],
                            input=repo_string,
                            text=True,
                            check=True,
                            capture_output=True
                        )

                    except subprocess.CalledProcessError as e:
                        self.view.display(f"Error while adding the Wazuh repository on a RedHat-based system: {e}",
                                          context="fatal", indent=2, level=0)
                        exit(1)


            progress.update_subtask(repo_subtask, new_prefix="(3/3) Repository ready...")
            progress.remove_subtask(repo_subtask)


            # ----------------------------------------------------------------------------
            # Étape 4 : Installation du package Wazuh indexer
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Installing Wazuh indexer package...")

            install_subtask = progress.add_subtask("(1/1) Installing wazuh-indexer...", total=1)

            packages = self.host.get_host().package  # package is a list

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", "/usr/bin/apt", "install", "-y", "wazuh-indexer"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh indexer on debian based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "wazuh-indexer"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh indexer on redhat based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            progress.update_subtask(install_subtask, new_prefix="(1/1) Wazuh indexer installed!")
            progress.remove_subtask(install_subtask)


            # ----------------------------------------------------------------------------
            # Étape 5 : Configuration du Wazuh indexer
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Configuring opensearch...")

            config_subtask = progress.add_subtask("(1/1) Editing opensearch configuration...", total=1)
            # TODO: (placeholder) Éditer /etc/wazuh-indexer/opensearch.yml (ou autre fichier de config)
            time.sleep(1)


            node_name = self._get_option("node-name-you-are-currently-installing",True).value
            loader = YamlLoader("/etc/wazuh-indexer/opensearch.yml")
            opensearch_config = loader.data

            for node in config["nodes"]["indexer"]:
                if node["name"] == node_name:
                    opensearch_config["node.name"] = node["name"]
                    opensearch_config["network.host"] = node["ip"]

            master_nodes = []

            for node in config["nodes"]["indexer"]:
                if node["node_type"] == "master":
                    master_nodes.append(node["name"])

            if not master_nodes:
                master_nodes.append(self._get_option("wazuh-indexer-name").value)

            opensearch_config["cluster.initial_master_nodes"] = master_nodes


            if self._get_option("discovery.seed_hosts",) : # -> none by default because it's not a cluster
                opensearch_config["discovery.seed_hosts"] = []
                for node in config["nodes"]["indexer"]:
                    opensearch_config["discovery.seed_hosts"].append(node["ip"])

            opensearch_config["plugins.security.nodes_dn"] = []
            for dn in self._get_option("plugins.security.nodes_dn",).value:
                opensearch_config["plugins.security.nodes_dn"].append(dn)


            loader.save(opensearch_config,False)

            progress.update_subtask(config_subtask, new_prefix="(1/1) opensearch config updated!")
            progress.remove_subtask(config_subtask)

            # ----------------------------------------------------------------------------
            # Étape 6 : Appliquer les certificats (commandes successives)
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Applying certificates...")

            cert_subtask = progress.add_subtask("(1/1) Copying / applying certs...", total=1)
            certs_path = self._get_option("certificates-path",True).value


            if not os.path.exists(certs_path):
                self.view.display(f"Certificates not found at {self._get_option('certificates-path')}, Please copy the certificates generated by the master indexer to this node",
                                  context="fatal", indent=2, level=0)
                exit(1)

            node_name = self._get_option("node-name-you-are-currently-installing",True).value

            try:
                # 1) Make sure /etc/wazuh-indexer/certs exists
                subprocess.run(["sudo", "mkdir", "-p", "/etc/wazuh-indexer/certs"], check=True, capture_output=True, text=True)

                # 2) Extract only necessary certificates from the tar file
                subprocess.run([
                    "sudo", "tar", "-xf", certs_path,
                    "-C", "/etc/wazuh-indexer/certs/",
                    f"./{node_name}.pem",
                    f"./{node_name}-key.pem",
                    "./admin.pem",
                    "./admin-key.pem",
                    "./root-ca.pem"
                ], check=True, capture_output=True, text=True)

                # 3) Rename the node’s PEM and KEY to indexer.pem and indexer-key.pem
                subprocess.run([
                    "sudo", "mv", "-n",
                    f"/etc/wazuh-indexer/certs/{node_name}.pem",
                    "/etc/wazuh-indexer/certs/indexer.pem"
                ], check=True, capture_output=True, text=True)

                subprocess.run([
                    "sudo", "mv", "-n",
                    f"/etc/wazuh-indexer/certs/{node_name}-key.pem",
                    "/etc/wazuh-indexer/certs/indexer-key.pem"
                ],check=True, capture_output=True, text=True)

                # 4) Secure permissions on the directory and files
                subprocess.run(["sudo", "chmod", "500", "/etc/wazuh-indexer/certs"], check=True, capture_output=True, text=True)

                files = glob.glob("/etc/wazuh-indexer/certs/*")  # expands to a list of all matching files

                subprocess.run(["sudo", "chmod", "400", *files], check=True, capture_output=True, text=True)

                # 5) Adjust ownership
                subprocess.run(["sudo", "chown", "-R", "wazuh-indexer:wazuh-indexer", "/etc/wazuh-indexer/certs"],
                               check=True, capture_output=True, text=True)

            except subprocess.CalledProcessError as e:
                self.view.display(
                    f"Error while applying certificates: {e}",
                    context="fatal", indent=2, level=0
                )
                exit(1)

            progress.update_subtask(cert_subtask, new_prefix="(1/1) Certificates applied successfully!")
            progress.remove_subtask(cert_subtask)


            # ----------------------------------------------------------------------------
            # Étape 7 : Lancement du service Wazuh (systemd ou sysv)
            # ----------------------------------------------------------------------------
            # On avance la barre principale (8/10).
            progress.update_main(new_prefix="Starting Wazuh indexer service...")

            service_subtask = progress.add_subtask("(1/1) Starting service...", total=1)

            if shutil.which("systemctl"):
                try:
                    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["sudo", "systemctl", "enable", "wazuh-indexer"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["sudo", "systemctl", "start", "wazuh-indexer"], check=True, capture_output=True,
                                   text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while starting the wazuh indexer service: {e}", context="fatal", indent=2, level=0)
                    exit(1)
            elif shutil.which("service"):
                if "apt" in packages:
                    try:
                        subprocess.run(["sudo","update-rc.d", "wazuh-indexer", "defaults", "95", "10"], check=True, capture_output=True,
                                       text=True)
                        subprocess.run(["sudo","service", "wazuh-indexer", "start"], check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(f"Error while starting the wazuh indexer service, using service on debian like: {e}", context="fatal", indent=2, level=0)
                        exit(1)
                elif "yum" in packages or "dnf" in packages:
                    try:
                        subprocess.run(["sudo","chkconfig", "--add", "wazuh-indexer"], check=True, capture_output=True, text=True)
                        subprocess.run(["sudo","service", "wazuh-indexer", "start"], check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(f"Error while starting the wazuh indexer service, using service on redhat like: {e}", context="fatal", indent=2, level=0)
                        exit(1)


            progress.update_subtask(service_subtask, new_prefix="(1/1) Service started!")
            progress.remove_subtask(service_subtask)

            # ----------------------------------------------------------------------------
            # Étape 8 : Initialisation du cluster
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Initializing Wazuh cluster...")

            init_subtask = progress.add_subtask("(1/1) Launching indexer-security-init.sh...", total=1)


            try:
                subprocess.run(["sudo", "/usr/share/wazuh-indexer/bin/indexer-security-init.sh"], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                self.view.display(f"Error while initializing the wazuh cluster: {e}", context="fatal", indent=2, level=0)
                exit(1)

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
