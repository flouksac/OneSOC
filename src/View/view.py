from termcolor import colored
from Utils.os_info import get_os_type
import os,re
from Model.component import Component 

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
                               "success": ("light_green",  "✅️"),
                               "warning": ("yellow", "⚠️ "),
                               "info":    ("light_grey", "💬")
                               }

            # Assigne la couleur et le symbole basés sur le contexte si aucune couleur n'est spécifiée
            if context.lower() not in context_mapping.keys() and context!="":
                context= f"[{context.upper()}]"
            else :
                for keyword, (default_color, symbol) in context_mapping.items():
                    if keyword in context.lower():
                        color = default_color
                        context = "[" + symbol + " " + context.upper() + "]"
                        break



            # Ajoute le contexte au message s'il est fourni
            full_message = f"{context} {message}" if context else message

            # Affiche le message mieux que HTLM et CSS ;)
            print(colored(full_message, color))

    def display_pretty_dict(self, dictionnary: dict, level: int = 0, color: str = None, indent: int = 0):

        if self.verbosity >= level:
            for key, value in dictionnary.items():

                # Gérer la couleur en fonction du type de valeur
                if isinstance(value, bool):
                    value_str = colored(str(value), 'light_magenta')
                elif isinstance(value, str):
                    value_str = colored(f'"{value}"', 'light_blue')
                elif isinstance(value, int) or isinstance(value, float):
                    value_str = colored(str(value), 'light_cyan')
                elif isinstance(value, dict):
                    print(" " * indent + f"{key}:")
                    self.display_pretty_dict(value, level, color, indent + 3)
                    continue
                else:
                    # Autres types sans couleur spécifique
                    value_str = str(value)

                print(" " * indent + f"{key}"+colored(":","white")+f" {value_str}")
            if indent == 0:
                print(" ")

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

    def display_recommendation(self):
        if self.verbosity >= 2:
            recommendation_message = [colored("Recommendation : \n", "light_cyan"),
                                      "To maximize the chances of a successful installation, here are our recommendations :",
                                    # " - Install Wazuh components on a clean Linux machine such as the ones below \n",
                                    # "   +- OS ------------------------------+ +- RAM (GB) -+- CPU (cores) -+  ",
                                    # "   | Amazon Linux 2                    | | 16         | 8             |  ",
                                    # "   | CentOS 7, 8                       | +------------+---------------+  ",
                                    # "   | Red Hat Enterprise Linux 7, 8, 9  | +- Storage (GB) -------------+  ",
                                    # "   | Ubuntu 16.04, 18.04, 20.04, 22.04 | | 250                        |  ",
                                    # "   +-----------------------------------+ +----------------------------+  ",
                                      "\n - Respect these steps, whatever is it a all-in-one install or a cluster install :",
                                      "   * Install the wazuh indexer first",
                                      "   * Then install the wazuh server ",
                                      "   * Then install the wazuh dashboard",
                                      "   * Optionally you can install SELKS (IDS), DFIR IRIS (Ticketing),Keepass (password manager)",
                                      "   * Install agents\n"]

            for message in recommendation_message:
                print(message)

   
    def list_component(self,data:list[Component]):
        output = []
        
        for component in data:
            output.append(component.name+" : ")
            output.append("  Description : ")
            
            output.append("    "+component.description.replace(r'\n','\n   '))
            
            output.append("  Options : ")
            for option in component.options : 
                output.append("    "+str(option))
            #for platform in component.supported_platform : 
            #    output.append("   "+platform)
            output.append(" ")
        for line in output:
            print (line)

    def list_action(self,data:dict):
        actions = [
            colored("The possible actions you can do are :\n","light_cyan"),
        ]
        
        for key,value in data.items():
            actions.append(" - "+key+" :")
            actions.append(colored("   "+value['command_description'], "cyan"),)
            actions.append(colored("   "+value['description'].replace(r'\n','\n  ')+"\n","light_grey"))
            
        for line in actions:
            print(line)

    # Easter Egg
    def display_themis_the_cat(self):
        print("\n"+colored( " _._     _,-'\"\"`-._\n"
                            "(,-.`._,'(       |\`-/|\n"
                            "    `-.-' \ )-`( , o o)\n"
                            "           `-    \`_`\"'-\n",
                            'yellow')+"\n")
        return ""