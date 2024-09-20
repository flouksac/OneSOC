import platform

from termcolor import colored


def banner():
    banner_lines = [
        colored(r"  )                      (         )            ", "blue"),
        colored(r"( /(                      )\ )   ( /(      (    ", "blue"),
        colored(r" )\())             (      (()/(   )\())     )\  ", "cyan"),
        colored(r"((_)\     (       ))\      /(_)) ((_)\    (((_) ", "cyan"),
        colored(r"  ((_)    )\ )   /((_)    (_))     ((_)   )\___ ", "light_cyan"),
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
                              "   * Optionally you can install SELKS (Suricata)"]

    for message in recommendation_message:
        print(message)


def compatibility_check():
    print(colored("\nPerforming compatibility check...\n","light_cyan"))

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
        print(colored(f"{current_os} is compatible with Wazuh!", "green"))
    else:
        print(colored(f"WARNING: {current_os} is not officially supported by Wazuh.", "red"))


    # next step : verify the wazuh install

if __name__ == "__main__":
    banner()
    # 1. Announce the goal of the script
    introduction()
    # 2. Check OS compatibility, does it support Wazuh?
    compatibility_check()
    # 3. Ask which component the user wants to install
    # 3'.Ask other configuration settings (ip, name...) or use configuration file
    # 4. Verify that the selected component is valid and coherent
    # 5. Install dependencies + verify and troubleshoot
    # 6. Install the selected component(s) + verify and troubleshoot
    # 7. Configure connections + verify and troubleshoot
    # 8. Add custom configuration to improve Wazuh + verify and troubleshoot
    # 9. Deploy the agents in propagation mode
