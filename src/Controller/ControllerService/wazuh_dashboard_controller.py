import subprocess
import time
from shutil import which

from Controller.ControllerService.abstract_component_service_controller import AbstractComponentServiceController
 


class Wazuh_Dashboard_Controller(AbstractComponentServiceController):  # L'odre est important
    def __init__(self, options=None):
        super().__init__(options)

    def info(self):
        pass

    def healthcheck(self):
        pass

    def install(self):
        super().install()
        with self.view.display_progress(f"Installation initialization of {self.component_name}...", indent=1,
                                        total_size=9) as progress:

            # ----------------------------------------------------------------------------
            # Étape 0 : Installation of curl and tar grep + dependencies
            # ----------------------------------------------------------------------------
            # Sur rpm : coreutils
            # Sur deb : sed, gnupg, apt-transport-https, curl, tar
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

            elif "yum" in packages or "dnf" in packages:
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

            progress.update_subtask(dependencies_subtask, new_prefix="(2/3) Installing dependencies...")

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", package_path, "update"], check=True, capture_output=True, text=True)  # cwd
                    subprocess.run(["sudo", package_path, "install", "-y", "debhelper", "gnupg","libcap2-bin"
                                    "apt-transport-https", "curl", "tar"], check=True, text=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}", context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "libcap","coreutils", "curl", "tar", "grep"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error: {e}", context="fatal", indent=2, level=0)
                    exit(1)

            required_commands = ["curl", "tar", "grep"]
            for command in required_commands:
                if not which(command):
                    self.view.display(f"Dependency {command} is missing after installation", context="fatal", indent=2,
                                      level=0)
                    exit(1)

            progress.update_subtask(dependencies_subtask, new_prefix="(3/3) Dependencies installed successfully.")
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
            # Étape 3 : Installation du package Wazuh Dashboard
            # ----------------------------------------------------------------------------
            progress.update_main(new_prefix="Installing Wazuh Dashboard package...")

            install_subtask = progress.add_subtask("(1/1) Installing wazuh-dashboard...", total=2)

            packages = self.host.get_host().package  # package is a list

            if "apt" in packages:
                try:
                    subprocess.run(["sudo", "/usr/bin/apt", "install", "-y", "wazuh-dashboard"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh dashboard on debian based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)


            elif "yum" in packages or "dnf" in packages:
                try:
                    subprocess.run(["sudo", package_path, "install", "-y", "wazuh-dashboard"],
                                   check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    self.view.display(f"Error while installing the wazuh dashboard on redhat based system: {e}",
                                      context="fatal", indent=2, level=0)
                    exit(1)

            progress.update_subtask(install_subtask, new_prefix="(1/1) Wazuh dashboard installed!")
            progress.remove_subtask(install_subtask)

            # ----------------------------------------------------------------------------
            # Étape 4 : Configuring the wazuh dashboard
            # ----------------------------------------------------------------------------

            # server.host = ip ou domaine ou 0.0.0.0

            # opensearch.hosts : les indexers en list

            # changement du fichier /etc/wazuh-dashboard/opensearch_dashboards.yml


            # ----------------------------------------------------------------------------
            # Étape 5 : Déploiement des certificats
            # ----------------------------------------------------------------------------

            # verif des certificats comme avec le serveur

            # install des certificats dans /etc/wazuh-dashboard/certs


            # ----------------------------------------------------------------------------
            # Étape 6 : Lancement du service Wazuh Dashboard
            # ----------------------------------------------------------------------------

            # systemctl start wazuh-dashboard

            # edit /usr/share/wazuh-dashboard/data/wazuh/config/wazuh.yml

            # avec l'ip du master node

            #



        pass

    def config(self):
        pass

    def repair(self):
        pass