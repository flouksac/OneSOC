from termcolor import colored
from Utils.os_info import get_os_type
import os

if get_os_type()=="Windows" : os.system("color")

class View:
    def __init__(self, verbosity = 2) -> None:
        # verbosity : 
        # 0 -> fundamental
        # 1 -> important
        # 2 -> normal
        # 3 -> detail
        # 4 -> debug
        self.verbosity = verbosity

    def set_verbosity(self, level):
        self.verbosity = level

    def display(self,message:str,level:int, context:str="", color:str=None) :
        """print message depending of the verbosity of the programme and the message level info

        Args:
            message (str): message content
            level (int): level of the importance of the message
            context (str): Préfix pour qualifier le message ex : [WARNING] Incompatible prompt, where "warning" is the context
            color (str): Color of the text to display
        """
        
        # definir des règles , en tant que fundamental, on voudrait seulement voir les erreurs et les succées
        
        # si context = certain type on peut définir une couleur particulière ? 
        
        if self.verbosity >= level:

            context_mapping = {"fatal":   ("red",    "☠️ "),
                               "error":   ("red",    "❌ "),
                               "success": ("green",  "✔️ "),
                               "warning": ("yellow", "⚠️ "),}

            # Assigne la couleur et le symbole basés sur le contexte si aucune couleur n'est spécifiée
            if not color:

                for keyword, (default_color, symbol) in context_mapping.items():
                    if keyword in context.lower():
                        color = default_color
                        context = "[" + symbol + " " + context.upper() + "]"
                        break
                else:
                    color = "white"

            # Ajoute le contexte au message s'il est fourni
            full_message = f"{context} {message}" if context else message

            # Affiche le message mieux que HTLM et CSS ;)
            print(colored(full_message, color))


    def display_banner(self):
        banner_lines = [colored("\n  )                      (         )            ", "blue"),
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


    def display_introduction(self):

        if self.verbosity >= 2:
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
                                      "   * Install the wazuh indexer first", "   * Then install the wazuh server ",
                                      "   * Then install the wazuh dashboard",
                                      "   * Optionally you can install SELKS (Suricata)",
                                      "   * Optionally you can install DFIR IRIS (Ticketing)",
                                      "   * Optionally you can install Keepass (password manager)", "   * Install agents"]

            for message in recommendation_message:
                print(message)