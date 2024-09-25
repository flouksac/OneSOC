import os
import platform
import subprocess
import shutil
from termcolor import colored
import psutil


def banner():
    banner_lines = [
        colored(r"  )                      (         )            ", "blue"),
        colored(r"( /(                      )\ )   ( /(      (    ", "blue"),
        colored(r" )\())             (      (()/(   )\())     )\  ", "light_blue"),
        colored(r"((_)\     (       ))\      /(_)) ((_)\    (((_) ", "cyan"),
        colored(r"  ((_)    )\ )   /((_)    (_))     ((_)   )\___ ", "cyan"),
        colored(r" / _ \   _(_/(  (_))      / __|   / _ \  ((/ __|", "light_cyan"),
        colored(r"| (_) | | ' \)) / -_)  -  \__ \  | (_) |  | (__ ", "white"),
        colored(r" \___/  |_||_|  \___|     |___/   \___/    \___|", "white"),
        colored("\n------------------ By OnlySOC ------------------\n", "cyan")]

    for lines in banner_lines:
        print(lines)


def introduction():
    introduction_message = [colored("General overview : \n", "light_cyan"),
                            "The goal of this project is to create a single installation script that provides "
                            "flexibility in deploying a SOC. ",
                            "You can either deploy Wazuh on a single server or distribute its components (manager, "
                            "indexer, dashboard) across multiple machines. ",
                            "The script handles the interconnection between components automatically or via a provided "
                            "configuration file.",
                            "The SOC also includes Suricata (integrated through SELKS), and the script manages its "
                            "integration with Wazuh as well.\n"]

    for message in introduction_message:
        print(message)

    recommendation_message = [colored("Recommendation : \n", "light_cyan"),
                              "To maximize the chances of a successful installation, here are our recommendations:",
                              " - Install Wazuh components on a clean Linux machine such as the ones below \n",
                              "   +- OS ------------------------------+ +- RAM (GB) -+- CPU (cores) -+  ",
                              "   | Amazon Linux 2                    | | 16         | 8             |  ",
                              "   | CentOS 7, 8                       | +------------+---------------+  ",
                              "   | Red Hat Enterprise Linux 7, 8, 9  | +- Storage (GB) -------------+  ",
                              "   | Ubuntu 16.04, 18.04, 20.04, 22.04 | | 250                        |  ",
                              "   +-----------------------------------+ +----------------------------+  ",
                              "\n - Respect these steps, whatever is it a all-in-one install or a cluster install :",
                              "   * Install the wazuh indexer first",
                              "   * Then install the wazuh server ",
                              "   * Then install the wazuh dashboard",
                              "   * Optionally you can install SELKS (Suricata)",
                              "   * Optionally you can install DFIR IRIS (Ticketing)",
                              "   * Optionally you can install Keepass (password manager)",
                              "   * Install agents"
                              ]

    for message in recommendation_message:
        print(message)


# = OS check ========================================================================================================= #


def os_check():
    print(colored("\nPerforming OS check...\n", "light_cyan"))

    compatible_os = ["Amazon Linux 2",
                     "CentOS 7", "CentOS 8",
                     "Red Hat Enterprise Linux 7", "Red Hat Enterprise Linux 8", "Red Hat Enterprise Linux 9",
                     "Ubuntu 16.04", "Ubuntu 18.04", "Ubuntu 20.04", "Ubuntu 22.04"]

    os_name, os_version = platform.system(), platform.release()

    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                os_info = {}
                for line in f:
                    key, value = line.rstrip().split("=")
                    os_info[key] = value.strip('"')

            current_os = f"{os_info.get('NAME', 'Unknown')} {os_info.get('VERSION_ID', 'Unknown')}"
        except Exception as e:
            current_os = f"Linux {os_version}"
    else:
        current_os = f"{os_name} {os_version}"

    print(f"Detected OS: {current_os}")

    if any(os_name in current_os for os_name in compatible_os):
        print(colored(f"{current_os} is compatible with Wazuh!", "light_green"))
    else:
        print(colored(f"WARNING: {current_os} is not officially supported by Wazuh.", "red"))


# = Hardware check =================================================================================================== #
def get_free_disk_space_gb():
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024 ** 3)
    return round(free_gb, 2)


def get_ram_in_gb():
    ram = psutil.virtual_memory()
    ram_gb = ram.total / (1024 ** 3)
    return round(ram_gb, 2)


def get_cpu_core_count():
    return os.cpu_count()


def hardware_check():
    print(colored("\nPerforming hardware check...\n", "light_cyan"))
    
    # Check Disk Free Space
    free_disk_space = get_free_disk_space_gb()
    if free_disk_space >= 250:
        print(colored(f"Free disk space: {free_disk_space} GB (sufficient)", "light_green"))
    else:
        print(colored(f"Free disk space: {free_disk_space} GB (not as much as we recommend, should be > 250 GB)",
                      "yellow"))

    # Check RAM
    ram_gb = get_ram_in_gb()
    if ram_gb >= 15.5:
        print(colored(f"RAM: {ram_gb} GB (sufficient)", "light_green"))
    else:
        print(colored(f"RAM: {ram_gb} GB (not as much as we recommend, should be > 16 GB)", "yellow"))

    # Check CPU cores
    cpu_cores = get_cpu_core_count()
    if cpu_cores >= 8:
        print(colored(f"CPU cores: {cpu_cores} (sufficient)", "light_green"))
    else:
        print(colored(f"CPU cores: {cpu_cores} (not as much as we recommend, should be > 8 cores)", "yellow"))


# = Service Check ==================================================================================================== #
def is_docker_installed():
    try:
        result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def identify_service(components):  # in the future we should verify also the status "error, running ..."
    for component, info in components.items():
        service_name = info["service"]
        try:
            result = subprocess.run(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if result.stdout.decode('utf-8').strip() == "active":
                info["status"] = "Active"
            else:
                info["status"] = "Inactive"
        except Exception as e:
            info["status"] = "Inactive"

    return components


def check_docker_status(containers):
    for container, info in containers.items():
        try:
            result_image = subprocess.run(['docker', 'images', '-q', info['image']], stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            if result_image.returncode == 0 and result_image.stdout.strip():
                info["status"] = "Image Found"
            else:
                info["status"] = "Image Not Found"

            if info["status"] == "Image Found":
                result_container = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={info["name"]}', '--format', '{{.Names}}'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result_container.returncode == 0 and info["name"] in result_container.stdout.decode().strip().split(
                        '\n'):
                    info["status"] = "Container running"
                else:
                    info["status"] = "Container not running"
        except Exception as e:
            print(f"Erreur lors de la vérification Docker pour {info['name']} : {e}")
    return containers


def service_check():
    print(colored("\nPerforming service check...\n", "light_cyan"))

    components = {
        "Wazuh Manager": {"service": "wazuh-manager", "status": None},
        "Wazuh Indexer": {"service": "wazuh-indexer", "status": None},
        "Wazuh Dashboard": {"service": "wazuh-dashboard", "status": None},
        "Wazuh Agent": {"service": "wazuh-agent", "status": None},
        # "KeePass": {"image": "keepass", "status": None},
    }
    containers = {
        "SELKS": {"image": "ghcr.io/stamusnetworks/scirius", "name": "scirius", "status": None},
        "DFIR-IRIS": {"image": "iriswebapp_app", "name": "iriswebapp_app", "status": None},
        "MISP": {"image": "ghcr.io/nukib/misp", "name": "misp", "status": None},

    }

    components = identify_service(components)

    active_components = []
    for component, info in components.items():
        if info["status"] == "Active":
            active_components.append(component)

    if active_components:
        print(colored("The following Wazuh service are already active : ", "light_green"))
        for component in active_components:
            print(f" - {component}")
    else:
        print(colored("No Wazuh components found on this machine.", "yellow"))

    if is_docker_installed():
        containers = check_docker_status(containers)

        print(colored("Status of Docker containers :", "light_green"))
        for container, info in containers.items():
            print(f" - {container} : {info['status']}")
    else:
        print(colored("Docker is not installed on this machine ", "yellow"))


# = Global check ===================================================================================================== #
def health_check():
    
    os_check()
    hardware_check()
    service_check()


# = User need ======================================================================================================== #

def retrieve_user_needs():
    options = {
        "1": "Full install of Wazuh in all-in-one architecture (Indexer + Manager + Dashboard)",
        "2": "Install Wazuh Indexer",
        "3": "Install Wazuh Manager",
        "4": "Install Wazuh Dashboard",
        "5": "Install SELKS (Suricata IDS)",
        "6": "Install DFIR IRIS (Ticketing)",
        "7": "Install KeePass (password manager)",
        "8": "Deploy all agents in propagation mode",
        "9": "Deploy agent on this computer",
        "X": "Abort installation process"
    }

    options_message = [colored("\nWhat do you want to do?", "light_cyan"),
                       colored("\n- Wazuh -", "white")]

    for key, value in options.items():
        if key == "5":
            options_message.append(colored("\n- Other -", "white"))
        if key == "8":
            options_message.append(colored("\n- Agents -", "white"))
        if key == "X":
            options_message.append(colored(f"\n{key}. To Abort", "light_red"))
        else:
            options_message.append(f"{key}. {value}")

    for message in options_message:
        print(message)

    choice = input(colored("\nSelect the option you want or abort (1-9/X): ", "white")).strip().upper()

    if choice in options:
        if choice == "X":
            print(colored("Aborting installation process.", "light_red"))
            return
        else:
            selected_option = options[choice]
            print(colored("You have selected :", "cyan"), selected_option, "\n")

            confirmation = input(colored("Are you sure of this choice? (y/N): ", "white")).strip().lower()

            if confirmation == "y":
                print(colored(f"\nProceeding with: {selected_option}...", "light_green"))
            else:
                retrieve_user_needs()
    else:
        print(colored("Invalid choice. Please try again.", "red"))
        retrieve_user_needs()

    match choice:
        # 3'. Ask other configuration settings (ip, name...) or use configuration file
        # depending on  the type of installation if necessary

        case "1":  # FULL INSTALL OF WAZUH
            # at each steps display information, each comments is for a function.
            # verify_able_to_full_install_wazuh()
            # install_dependencies_wazuh ()
            # full_install_wazuh()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "2":  # INSTALL OF WAZUH INDEXER
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_wazuh_indexer()
            # install_dependencies_wazuh_indexer ()
            # install_wazuh_indexer()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass

        case "3":  # INSTALL OF WAZUH MANAGER
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_wazuh_manager()
            # install_dependencies_wazuh_manager ()
            # install_wazuh_manager()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "4":  # INSTALL OF WAZUH DASHBOARD
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_wazuh_dashboard()
            # install_dependencies_wazuh_dashboard ()
            # install_wazuh_dashboard()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "5":  # INSTALL OF SELKS
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_selks()
            # install_dependencies_selks ()
            # install_selks()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "6":  # INSTALL OF IRIS
            # at each steps display information, each comments is for a function.
            # verify_able_to_full_install_wazuh()
            # install_dependencies_iris ()
            # install_iris()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "7":  # INSTALL OF Keepass
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_keepass()
            # install_dependencies_keepass ()
            # install_keepass()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass
        case "8":  # Deploy wazuh agent in propagation mode
            # TBD
            pass
        case "9":  # INSTALL OF WAZUH AGENT LOCALLY
            # at each steps display information, each comments is for a function.
            # verify_able_to_install_agent()
            # install_dependencies_wazuh_agent()
            # install_wazuh_agent()
            # verify that everything is installed correctly ()
            # do network configuration ()
            # do custom configuration to improve wazuh ()
            # display success and recap ()
            # done -> ask for next step installation or retrieve_user_needs()
            pass


if __name__ == "__main__":
    banner()
    # 1. Announce the goal of the script
    introduction()
    # 2. Check OS compatibility, does it support Wazuh? Verify the health of the already installed services
    health_check()  # TODO -> rendre cross plateform && améliorer le healthcheck
    # 3. Ask which component the user wants to install
    retrieve_user_needs()

    """ # Old comments
    # 4. Verify that the selected component is valid and coherent
    # 5. Install dependencies + verify and troubleshoot
    # 6. Install the selected component(s) + verify and troubleshoot
    # 7. Configure connections + verify and troubleshoot
    # 8. Add custom configuration to improve Wazuh + verify and troubleshoot
    # 9. Deploy the agents in propagation mode
    """
