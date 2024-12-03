import os
import time

from termcolor import colored
import survey as sv

from Utils.os_info import get_os_type

from Model.ModelObjects.component import Component
from Model.ModelObjects.action import Action
from Model.ModelObjects.option import Option

from DesignPattern.singleton import Singleton

if get_os_type()=="Windows" : os.system("color") # permet de pouvoir afficher la couleur sous windows


class View(metaclass=Singleton):
    
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

    def display(self,message:str,level:int=2, context:str="", color:str=None) :
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

            context_mapping = {"fatal":   ("red",         "☠️ "),
                               "error":   ("red",         "❌ "),
                               "success": ("light_green",  "✅️"),
                               "warning": ("yellow",      "⚠️ "),
                               "info":    ("light_grey",   "💬")
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
        output = [
            colored("The different component we take in charges are the following :\n","light_cyan"),
        ]
        
        for component in data:
            output.append(" - "+component.name+" : ")
            output.append(colored("   "+component.role,"cyan"))
            output.append(colored("   "+component.description.replace(r'\n','\n  '),"light_grey"))
            output.append(colored("   Supported OS are : ","light_grey"))

            for platform in component.supported_platform:
                
                if platform.architecture=="None": # pas propre (regrouper par architecure)
                    output.append(colored("   "+str(platform.os_type)+": "+str(platform.recommended_os)+" "+str(platform.version)+" - "+str(platform.package),"light_grey"))
                else :
                    output.append(colored("   "+str(platform.os_type)+": "+str(platform.recommended_os)+" "+str(platform.version)+" - "+str(platform.package)+" - "+str(platform.architecture),"light_grey"))
            output.append(" ")
            
        for line in output:
            print (line)

    def list_option(self,options_dict:dict[str:Option]):
        output = [
            colored("The possible options that you can modify in :\n","light_cyan"),
        ]
        
        for component_name,option_list in options_dict.items():
            #print(type(component_name))
            output.append(" - Component \""+component_name+"\" :")
            for option in option_list:
                output.append(colored("   "+option.key, "cyan")+":"+colored(" "+str(option.value), "cyan"))
            output.append(" ")
                
        output.append(colored("you can modify these parameters when installing a component with","light_grey")+
                        colored(" --install-option 'component1-ip=10.0.0.1' 'component2-ip=10.0.0.2' ","cyan")+
                        colored("\nor when config with ","light_grey")+
                        colored("--config-option 'component1-ip=10.0.0.1' \n","cyan"))
                                
        for line in output:
            print(line)
            
    def list_action(self,actions:list[Action]):
        output = [
            colored("The possible actions you can do are :\n","light_cyan"),
        ]
        
        for action in actions:
            output.append(" - "+action.name+" :")
            output.append(colored("   "+action.command_description, "cyan"),)
            output.append(colored("   "+action.description.replace(r'\n','\n  ')+"\n","light_grey"))
            
        for line in output:
            print(line)

    def display_selector_multiple(self,prompt:str,choices:list[str]):
        indexes = sv.routines.basket(prompt,options=choices,mark='', permit = True,escapable = False,positive_mark='['+colored("X","cyan")+']')
        return indexes
    
    def display_input(self,prompt:str):
        return sv.routines.input(prompt,mark="")
      
    def display_wait(self,prefix:str):
        
        with sv.graphics.SpinProgress(prefix=prefix+": ",mark="",epilogue =prefix):
            for i in range(20):
                time.sleep(0.1)

    def display_agree(self,prompt:str,default=True):
        return sv.routines.inquire(prompt,default=default,mark="")


    # Easter Egg
    def display_themis_the_cat(self):
        print("\n"+colored( " _._     _,-'\"\"`-._\n"
                            "(,-.`._,'(       |\`-/|\n"
                            "    `-.-' \ )-`( , o o)\n"
                            "           `-    \`_`\"'-\n",
                            'yellow')+"\n")
        return ""

