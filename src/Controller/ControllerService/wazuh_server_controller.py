import ast
import os
import shutil
import subprocess
import time
from shutil import which

import requests
import yaml

from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
from Model.loaderYAML import YamlLoader


class Wazuh_Server_Controller(AbstractComponentServiceController):
    def __init__(self, options=None):
        super().__init__(options)

    def info(self):
        pass

    def healthcheck(self):
        pass

    def install(self):
        super().install()
        # TODO : ajouter le support des systems basés sur rpm
        with self.view.display_progress(f"Installation initialization of {self.component_name}...", indent=1,
                                        total_size=9) as progress:

            # ----------------------------------------------------------------------------
            # Étape 0 : Installation of curl and tar grep + dependencies
            # ----------------------------------------------------------------------------
            # Sur rpm : coreutils
            # Sur deb : sed, gnupg, apt-transport-https, curl, tee, tar

            progress.update_main(new_prefix="Installation of dependencies...")
            dependencies_subtask = progress.add_subtask("(1/3) Getting your host package manager...", 3)

            if self.host.get_host().package is None:
                self.view.display("No package manager found on this system", context="fatal", indent=2, level=0)
                exit(1)

            packages = self.host.get_host().package

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
                    subprocess.run(["sudo", package_path, "install", "-y", "sed", "gnupg",
                                   "apt-transport-https","curl","tar"], check=True,text=True, capture_output=True)
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
            # Étape 2 : Installation du repository Wazuh
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
                                   check=True, capture_output=True, text=True)
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

            progress.update_subtask(repo_subtask, new_prefix="(3/3) Repository Installed...")
            progress.remove_subtask(repo_subtask)

            # ----------------------------------------------------------------------------
            # Étape 3 : Installation du package Wazuh Manager (Server)
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Installing Wazuh Manager package...")

            install_subtask = progress.add_subtask("(1/1) Installing wazuh-manager...", total=2)

            packages = self.host.get_host().package  # package is a list

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", "/usr/bin/apt", "install", "-y", "wazuh-manager"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh manager on debian based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "wazuh-manager"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh manager on redhat based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)

            progress.update_subtask(install_subtask, new_prefix="(1/1) Wazuh manager installed!")
            progress.remove_subtask(install_subtask)

            # ----------------------------------------------------------------------------
            # Étape 4 : Installation du package filebeat
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Installing filebeat package...")

            install_subtask = progress.add_subtask("(1/1) Installing filebeat...", total=2)

            packages = self.host.get_host().package  # package is a list

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", "/usr/bin/apt", "install", "-y", "filebeat"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the filebeat on debian based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "filebeat"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the filebeat on redhat based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)

            progress.update_subtask(install_subtask, new_prefix="(1/1) filebeat installed!")
            progress.remove_subtask(install_subtask)

            # ----------------------------------------------------------------------------
            # Étape 5 : Configuration de FileBeat
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Adjusting filebeat's config.yml file from the provided settings...")
            filebeat_subtask = progress.add_subtask("(1/7) Getting Wazuh filebeat file...", 7)

            url = f"https://packages.wazuh.com/{self._get_option('version', True).value}/tpl/wazuh/filebeat/filebeat.yml"
            response = requests.get(url, stream=True)
            filebeat_path = "/etc/filebeat/filebeat.yml"


            if response.status_code == 200:
                with open(filebeat_path, 'wb') as f:
                    f.write(response.content)
            else:
                self.view.display(f"Error: Couldn't retrieve filebeat.yml file, status code : {response.status_code}",
                                  context="fatal", indent=2, level=0)
                exit(1)

            progress.update_subtask(filebeat_subtask, new_prefix="(2/7) Modifying filebeat.yml...")

            try :
                loader = YamlLoader(filebeat_path)
                config:dict = loader.data
            except yaml.YAMLError as e:
                self.view.display(f"Error: Couldn't parse filebeat.yml file, {e}", context="fatal", indent=2, level=0)
                if os.path.exists(filebeat_path):
                    os.remove(filebeat_path)
                exit(1)
            except FileNotFoundError as e:
                self.view.display(f"Error: Couldn't find filebeat.yml file, {e}", context="fatal", indent=2, level=0)
                exit(1)

            # Ajout des ips des indexer wazuh
            config["output.elasticsearch"]["hosts"] = ast.literal_eval(self._get_option("list-of-indexers-ip",True).value)
            #config["output.elasticsearch"]["username"] = self._get_option("indexer-username",True).value
            #config["output.elasticsearch"]["password"] = self._get_option("indexer-password",True).value

            self.view.display(f"filebeat.yml file updated with the provided settings :", context="info", indent=2, level=3)
            self.view.display_pretty_dict(config, level=3, indent=2)

            loader.save(config)



            try:
                progress.update_subtask(filebeat_subtask, new_prefix="(3/7) Creating keystore for filebeat...")

                subprocess.run([
                    "filebeat","keystore","create", "--force"
                ], check=True, capture_output=True, text=True)

                subprocess.run([
                    "filebeat", "keystore", "add", "username", "--stdin", "--force"
                ], input=self._get_option("indexer-username", True).value, check=True,
                    capture_output=True, text=True)

                subprocess.run([
                    "filebeat", "keystore", "add", "password", "--stdin", "--force"
                ], input=self._get_option("indexer-password", True).value, check=True,
                    capture_output=True, text=True)

                progress.update_subtask(filebeat_subtask, new_prefix="(4/7) Getting Wazuh template for filebeat...")

                subprocess.run([
                    "curl", "-so", "/etc/filebeat/wazuh-template.json",
                    f"https://raw.githubusercontent.com/wazuh/wazuh/v{self._get_option("version",True).value}.1/extensions/elasticsearch/7.x/wazuh-template.json"
                ], check=True,capture_output=True, text=True)

                subprocess.run([
                    "chmod", "go+r", "/etc/filebeat/wazuh-template.json"
                ], check=True, capture_output=True, text=True)

                progress.update_subtask(filebeat_subtask, new_prefix="(5/7) Getting Wazuh module for filebeat...")


                filebeat_tar = subprocess.run([
                    "curl", "-s", "https://packages.wazuh.com/4.x/filebeat/wazuh-filebeat-0.4.tar.gz"
                ], check=True, capture_output=True)

                progress.update_subtask(filebeat_subtask, new_prefix="(6/7) UnTar Wazuh module for filebeat...")

                subprocess.run([
                    "tar", "-xvz", "-C", "/usr/share/filebeat/module",
                ], input=filebeat_tar.stdout, check=True,  capture_output=True)

            except subprocess.CalledProcessError as e:
                self.view.display(
                    f"Error while applying certificates: {e}",
                    context="fatal", indent=2, level=0
                )
                exit(1)


            progress.update_subtask(filebeat_subtask, new_prefix="(7/7) Filebeat ready")
            progress.remove_subtask(filebeat_subtask)


            # ----------------------------------------------------------------------------
            # Étape 6 : Appliquer les certificats (commandes successives)
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Applying certificates...")
            cert_subtask = progress.add_subtask("(1/3) Copying / applying certs...", total=3)


            # si les certificats ne sont pas sur le chemin entrée, on exit
            certs_tar_path = self._get_option("certificates-path",True).value

            if not os.path.exists(certs_tar_path):
                self.view.display(f"Please, copy the certificates generated by the first wazuh indexer to "
                                  f"the path : {certs_tar_path}", context="warning", indent=2, level=0)
                self.view.display(f"Error: The path {certs_tar_path} does not exist", context="fatal",
                                  indent=2, level=0)
                exit(1)

            # sinon on les déploient
            node_name = self._get_option("node-name-you-are-currently-installing",True).value

            try:
                subprocess.run(["mkdir", '-p',"/etc/filebeat/certs"], check=True,
                               capture_output=True, text=True)

                subprocess.run([
                    "tar", "-xf", certs_tar_path, "-C", "/etc/filebeat/certs/", f"./{node_name}.pem",
                    f"./{node_name}-key.pem", "./root-ca.pem"
                ], check=True, capture_output=True, text=True)

                subprocess.run([
                    "mv", "-n", f"/etc/filebeat/certs/{node_name}.pem", "/etc/filebeat/certs/filebeat.pem"
                ], check=True, capture_output=True, text=True)

                subprocess.run([
                    "mv", "-n", f"/etc/filebeat/certs/{node_name}-key.pem", "/etc/filebeat/certs/filebeat-key.pem"
                ], check=True, capture_output=True, text=True)

                progress.update_subtask(cert_subtask, new_prefix="(2/3) Changing permissions...")

                subprocess.run([
                    "chmod", "500", "/etc/filebeat/certs"
                ], check=True, capture_output=True, text=True)

                #subprocess.run([
                #   "chmod", "400", "/etc/filebeat/certs/*"
                #], check=True, capture_output=True, text=True)

                subprocess.run([
                    "chown", "-R", "root:root", "/etc/filebeat/certs"
                ], check=True, capture_output=True, text=True)


            except subprocess.CalledProcessError as e:
                self.view.display(
                    f"Error while applying certificates: {e}",
                    context="fatal", indent=2, level=0
                )
                exit(1)

            progress.update_subtask(cert_subtask, new_prefix="(3/3) Certificates applied successfully!")
            progress.remove_subtask(cert_subtask)

            # ----------------------------------------------------------------------------
            # Étape 7 : Configuration des connections avec les indexers wazuh
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Configuring connections with the indexers...")
            connection_indexers = progress.add_subtask("(1/3) Save the Wazuh indexer username and password", total=3)


            try:
                subprocess.run([
                    "/var/ossec/bin/wazuh-keystore", "-f", "indexer", "-k", "username", "-v",
                ], input=self._get_option("indexer-username",True).value,
                check=True, capture_output=True, text=True)

                subprocess.run([
                    "/var/ossec/bin/wazuh-keystore", "-f", "indexer", "-k", "password", "-v",
                ], input=self._get_option("indexer-password", True).value,
                    check=True, capture_output=True, text=True)


            except subprocess.CalledProcessError as e:
                self.view.display(
                    f"Error while applying certificates: {e}",
                    context="fatal", indent=2, level=0
                )
                exit(1)

            progress.update_subtask(connection_indexers, new_prefix="(2/3) Edit the local /var/ossec/etc/ossec.conf file...")

            indexers_ip = ast.literal_eval(self._get_option("list-of-indexers-ip", True).value)

            try:
                with open("/var/ossec/etc/ossec.conf", "r") as file:
                    ossec_conf = file.readlines()

                # Find the indexer hosts section
                start_index = next(i for i, line in enumerate(ossec_conf) if "<hosts>" in line)
                end_index = next(i for i, line in enumerate(ossec_conf) if "</hosts>" in line)

                # Replace the hosts section with the new IPs
                new_hosts = ["<hosts>\n"]
                for ip in indexers_ip:
                    new_hosts.append(f"  <host>https://{ip}/</host>\n")
                new_hosts.append("</hosts>\n")

                ossec_conf[start_index:end_index + 1] = new_hosts

                with open("/var/ossec/etc/ossec.conf", "w") as file:
                    file.writelines(ossec_conf)

            except (FileNotFoundError, StopIteration) as e:
                self.view.display(f"Error: Couldn't update /var/ossec/etc/ossec.conf file, {e}", context="fatal",
                                  indent=2, level=0)
                exit(1)

            progress.update_subtask(connection_indexers, new_prefix="(3/3) /var/ossec/etc/ossec.conf edited successfuly...")
            progress.remove_subtask(connection_indexers)

            # ----------------------------------------------------------------------------
            # Étape 8 : Lancement du service Wazuh (systemd ou sysv)
            # ----------------------------------------------------------------------------

            progress.update_main(new_prefix="Starting Wazuh Manager service...")

            service_subtask = progress.add_subtask("(1/1) Starting service...", total=1)

            if shutil.which("systemctl"):
                try:
                    subprocess.run(["systemctl", "daemon-reload"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["systemctl", "enable", "wazuh-manager"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["systemctl", "start", "wazuh-manager"], check=True, capture_output=True,
                                   text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while starting the wazuh manager service: {e}", context="fatal",
                                      indent=2, level=0)
                    exit(1)
            elif shutil.which("service"):
                if "apt" in packages:
                    try:
                        subprocess.run(["update-rc.d", "wazuh-manager", "defaults", "95", "10"], check=True,
                                       capture_output=True,
                                       text=True)
                        subprocess.run(["service", "wazuh-manager", "start"], check=True, capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(
                            f"Error while starting the wazuh manager service, using service on debian like: {e}",
                            context="fatal", indent=2, level=0)
                        exit(1)
                elif "yum" in packages or "dnf" in packages:
                    try:
                        subprocess.run(["chkconfig", "--add", "wazuh-manager"], check=True, capture_output=True,
                                       text=True)
                        subprocess.run(["service", "wazuh-manager", "start"], check=True, capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(
                            f"Error while starting the wazuh manager service, using service on redhat like: {e}",
                            context="fatal", indent=2, level=0)
                        exit(1)

            progress.update_subtask(service_subtask, new_prefix="(1/1) Service started!")
            progress.remove_subtask(service_subtask)


            # ----------------------------------------------------------------------------
            # Étape 9 : Lancement du service Filebeat (systemd ou sysv)
            # ----------------------------------------------------------------------------

            progress.update_main(new_prefix="Starting Filebeat service...")

            service_subtask = progress.add_subtask("(1/1) Starting service...", total=1)

            if shutil.which("systemctl"):
                try:
                    subprocess.run(["systemctl", "daemon-reload"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["systemctl", "enable", "filebeat"], check=True, capture_output=True,
                                   text=True)
                    subprocess.run(["systemctl", "start", "filebeat"], check=True, capture_output=True,
                                   text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while starting the Filebeat service: {e}", context="fatal",
                                      indent=2, level=0)
                    exit(1)
            elif shutil.which("service"):
                if "apt" in packages:
                    try:
                        subprocess.run(["update-rc.d", "filebeat", "defaults", "95", "10"], check=True,
                                       capture_output=True,
                                       text=True)
                        subprocess.run(["service", "filebeat", "start"], check=True, capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(
                            f"Error while starting the Filebeat service, using service on debian like: {e}",
                            context="fatal", indent=2, level=0)
                        exit(1)
                elif "yum" in packages or "dnf" in packages:
                    try:
                        subprocess.run(["chkconfig", "--add", "filebeat"], check=True, capture_output=True,
                                       text=True)
                        subprocess.run(["service", "filebeat", "start"], check=True, capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError as e:
                        self.view.display(
                            f"Error while starting the Filebeat service, using service on redhat like: {e}",
                            context="fatal", indent=2, level=0)
                        exit(1)

            progress.update_subtask(service_subtask, new_prefix="(1/1) Service started!")
            progress.remove_subtask(service_subtask)


        pass

    def config(self):
        pass

    def repair(self):
        pass