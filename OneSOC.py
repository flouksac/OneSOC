import os
import platform
import subprocess

from termcolor import colored


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


def compatibility_check():
    print(colored("\nPerforming compatibility check...\n", "light_cyan"))

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


def identify_service(components):
    for component, info in components.items():
        service_name = info["service"]
        try :
            result = subprocess.run(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if result.stdout.decode('utf-8').strip() == "active":
                info["status"] = "Active"
            else:
                info["status"] = "Inactive"
        except Exception as e:
            info["status"] = "Inactive"

    return components


def health_check():
    components = {
        "Wazuh Manager": {"service": "wazuh-manager", "status": None},
        "Wazuh Indexer": {"service": "wazuh-indexer", "status": None},
        "Wazuh Dashboard": {"service": "wazuh-dashboard", "status": None},
        "Wazuh Agent": {"service": "wazuh-agent", "status": None},
        #"SELKS":
        # keepass
        # dfir iris
    }

    components = identify_service(components)

    active_components = []
    for component, info in components.items():
        if info["status"] == "Active":
            active_components.append(component.keys())

    if active_components :
        print(colored(f"The following Wazuh service are already active : ", "light_green"))
        for component in active_components:
            print(f"{component.keys()}")

    else:
        print(colored("No Wazuh components found on this machine.", "yellow"))


if __name__ == "__main__":
    banner()
    # 1. Announce the goal of the script
    introduction()
    # 2. Check OS compatibility, does it support Wazuh?
    compatibility_check()
    # TODO  inform user of what component there already is on the computer ...
    health_check()
    # 3. Ask which component the user wants to install
    retrieve_user_needs()
    # 3'.Ask other configuration settings (ip, name...) or use configuration file
    # 4. Verify that the selected component is valid and coherent
    # 5. Install dependencies + verify and troubleshoot
    # 6. Install the selected component(s) + verify and troubleshoot
    # 7. Configure connections + verify and troubleshoot
    # 8. Add custom configuration to improve Wazuh + verify and troubleshoot
    # 9. Deploy the agents in propagation mode
