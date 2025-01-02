# built-in module
import os
import time
import re
from datetime import datetime
from typing import Literal, Optional, List

# graphical module
import survey as sv
from rich.console import Console
from rich.theme import Theme
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, SpinnerColumn, \
    TimeElapsedColumn
import termcolor

# home made module
from DesignPattern.singleton import Singleton
from Model.ModelObjects.action import Action
from Model.ModelObjects.component import Component
from Model.ModelObjects.option import Option
from Utils.os_info import get_os_type

if get_os_type() == "Windows": os.system("color")  # permet de pouvoir afficher la couleur sous windows

def colored(text: str, color: Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan",
                                      "light_grey", "dark_grey", "light_red", "light_green", "light_yellow",
                                      "light_blue", "light_magenta", "light_cyan", "white"] | None = None) -> str:
    """
    Colorize a text with the given color.

    Args:
        text (str): The text to colorize.
        color (str): The color to apply.

    Returns:
        str: The colorized text.
    """
    return termcolor.colored(text, color)


class View(metaclass=Singleton):
    DEFAULT_STYLES = {
        "fatal": ("error", ":skull:"),
        "error": ("error", ":x:"),
        "success": ("success", ":white_check_mark:"),
        "warning": ("warning", ":warning:"),
        "info": ("info", ":speech_balloon:"),
    }

    def __init__(self, verbosity=2) -> None:
        # verbosity :
        # 0 -> fundamental
        # 1 -> important
        # 2 -> normal
        # 3 -> detail
        # 4 -> debug
        self.verbosity = verbosity

        self.theme = Theme({
            "info": "white",
            "warning": "bold yellow",
            "error": "bold red",
            "success": "bold green",
            "banner": "cyan",
            "highlight": "bright_cyan",
        })
        self.console = Console(theme=self.theme)

    def set_verbosity(self, level):
        self.verbosity = level

    def display(self, message: str, level: int = 2, context: str = None, color: str = None, indent: int = 0):
        """print message depending of the verbosity of the programme and the message level info

        Args:
            message (str): message content
            level (int): level of the importance of the message
            context (str): Préfix pour qualifier le message ex : [WARNING] Incompatible prompt, where "warning" is the context
            color (str): Color of the text to display
            indent (int): indentation of the message
        """

        if self.verbosity >= level:
            if context and context.lower() == "debug":
                now = datetime.now().strftime("[%H:%M:%S]")
                full_message = (
                    f"{' ' * indent}"  # indentation
                    f"{now} "  # horodatage
                    f"[:robot: {context.upper()}] "
                    f"[{color if color else 'info'}]{message}[/{color if color else 'info'}]"
                )
                self.console.print(full_message, highlight=False,  )
                return

            if context is None:
                self.console.print(" " * indent + message, style=color if color else "info",highlight=False)
                return
            style, emoji = self.DEFAULT_STYLES.get(context.lower(), ("info", ":speech_balloon:"))
            style = color if color else style
            formatted_context = f"[{emoji} {context.upper()}]" if context.lower() in self.DEFAULT_STYLES else f"[{context.upper()}]"
            indentation = " " * indent

            self.console.print(f"{indentation}{formatted_context} [{style}]{message}[/]",highlight=False)

    def display_pretty_dict(self, dictionary: dict, level: int = 0, indent: int = 0):
        """
        Affiche un dictionnaire avec une mise en forme stylisée à l'aide de rich.

        Args:
            dictionary (dict): Le dictionnaire à afficher.
            level (int): Niveau de verbosité requis pour afficher le dictionnaire.
            indent (int): Nombre d'espaces pour l'indentation.
        """
        if self.verbosity >= level:
            for key, value in dictionary.items():
                # Gérer la couleur et le style en fonction du type de valeur
                if isinstance(value, bool):
                    value_str = f"[magenta]{value}[/magenta]"
                elif isinstance(value, str):
                    value_str = f"[bright_cyan]\"{value}\"[/bright_cyan]"
                elif isinstance(value, (int, float)):
                    value_str = f"[bright_blue]{value}[/bright_blue]"
                elif isinstance(value, dict):
                    # Afficher le sous-dictionnaire avec une indentation supplémentaire
                    self.console.print(" " * indent + f"[bold]{key}[/bold]:")
                    self.display_pretty_dict(value, level, indent + 3)
                    continue
                else:
                    # Autres types sans style spécifique
                    value_str = f"{value}"

                # Afficher la clé et la valeur avec l'indentation appropriée
                self.display(f"{' ' * indent}[bold]{key}[/bold]: {value_str}")

            # Ajouter une ligne vide après le dictionnaire principal
            if indent == 0:
                self.display("")

    def display_banner(self):
        banner_lines = ["[blue]\n   )                     (          )            [/blue]",
                        "[blue]( /(                      )\\ )   ( /(      (    [/blue]",
                        "[bright_blue] )\\())             (      (()/(   )\\())     )\\  [/bright_blue]",
                        "[cyan]((_\\     (        ))\\      /(_)) ((_)\\    (((_) [/cyan]",
                        "[cyan]  (([/cyan][white]_[/white][cyan])    )\\ )   /((_)    ([/cyan][white]_[/white][cyan]))     (([/cyan][white]_[/white][cyan])   )\\\[/cyan][white]___[/white][cyan]\\ [/cyan]",
                        "[white] / _ \\   _[/white][bright_cyan]([/bright_cyan][white]_[/white][bright_cyan]/(  ([/bright_cyan][white]_[/white][bright_cyan]))      [/bright_cyan][white]/ __|   / _ \\  [/white][bright_cyan](([/bright_cyan][white]/ __|[/white]",
                        "[white]| (_) | | ' \\\[/white][bright_cyan]))[/bright_cyan][white] / -_)  -  \\__ \\  | (_) |  | (__ [/white]",
                        "[white] \\___/  |_||_|  \\___|     |___/   \\___/    \\___|[/white]",
                        "[cyan]\n------------------ [/cyan][white]By OnlySOC[/white][cyan] ------------------\n[/cyan]",
                        ]

        for line in banner_lines:
            self.display(line)

    def display_introduction(self):

        if self.verbosity >= 2:
            introduction_message = ["[highlight]General overview : \n[/highlight]",
                                    "The goal of this project is to create a single installation script that provides "
                                    "flexibility in deploying a SOC. ",
                                    "You can either deploy Wazuh on a single server or distribute its components (manager, "
                                    "indexer, dashboard) across multiple machines. ",
                                    "The script handles the interconnection between components automatically or via a provided "
                                    "configuration file.",
                                    "The SOC also includes Suricata (integrated through SELKS), and the script manages its "
                                    "integration with Wazuh as well.\n"]

            for line in introduction_message:
                self.display(line)

    def display_recommendation(self):
        if self.verbosity >= 2:
            recommendation_message = [
                "[highlight]Recommendation : \n[/highlight]",
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

            for line in recommendation_message:
                self.display(line)

    def list_component(self, data: list[Component]):
        """
        Affiche la liste des composants avec un regroupement par type d'OS, puis par distribution.

        Args:
            data (list[Component]): Liste des composants à afficher.
        """
        if not data:
            self.display("No components available to display.", level=2, color="yellow", indent=0)
            return

        self.display("The different components we take in charge are the following:\n", level=2, color="bright_cyan",
                     indent=0)

        for component in data:
            self.display(f" - {component.name}:", level=2, color="bold", indent=0)
            self.display(f"{component.role}", level=2, color="cyan", indent=3)
            self.display("Supported OS are grouped by platform and distribution:", level=2, indent=3)

            grouped_platforms = {}
            for platform in component.supported_platform:
                grouped_platforms.setdefault(platform.os_type, {}).setdefault(platform.recommended_os, []).append(
                    platform)

            for os_type, distributions in grouped_platforms.items():
                self.display(f"{os_type}:", level=2, indent=5)
                for distro, platforms in distributions.items():
                    self.display(f"{distro}:", level=2, color="cyan", indent=7)
                    for platform in platforms:
                        version_info = f"{platform.version} - {platform.package}"
                        if platform.architecture != "None":
                            version_info += f" - {platform.architecture}"
                        self.display(version_info, level=2, indent=9)


            self.display("", level=2)

    def list_option(self, options_dict: dict[str, list[Option]]):
        """
        Affiche les options disponibles par composant.

        Args:
            options_dict (dict[str, list[Option]]): Dictionnaire des options par composant.
        """
        # Introduction
        self.display("The possible options that you can modify are:\n", level=2, color="highlight", indent=0)

        # Parcourir les composants et leurs options
        for component_name, option_list in options_dict.items():
            self.display(f"- Component \"{component_name}\":", level=2, color="white bold", indent=1)
            for option in option_list:
                self.display(f"{option.key}:[cyan] {option.value}[/cyan]", level=2, indent=3)
            self.display("", level=2)

        # Instructions supplémentaires
        self.display(
            "You can modify these parameters when installing a component with "
            "[cyan]--install-option 'component1-ip=10.0.0.1' 'component2-ip=10.0.0.2'[/cyan]\n"
            "or when configuring with [cyan]--config-option 'component1-ip=10.0.0.1'[/cyan].",
            level=2,
        )

    def list_action(self, actions: list[Action]):
        """
        Affiche les actions disponibles avec leurs descriptions.

        Args:
            actions (list[Action]): Liste des actions à afficher.
        """
        # Introduction
        self.display("The possible actions you can do are:\n", level=2, color="highlight", indent=0)

        # Parcourir les actions et afficher leurs détails
        for action in actions:
            self.display(f"- {action.name}:", level=2, color="bold", indent=1)
            self.display(f"{action.command_description}", level=2, color="cyan", indent=3)
            self.display(action.description.replace(r'\n', '\n  ') + "\n", level=2, indent=3)

    @staticmethod
    def display_selector_multiple(prompt: str, choices: list[str]):
        indexes = sv.routines.basket(prompt, options=choices, index=0,
                                     mark='', permit=True, escapable=False,
                                     positive_mark='[' + colored("X", "cyan") + ']')
        return indexes

    @staticmethod
    def display_input(prompt: str, value: str , indent:int=0) -> str :
        return sv.routines.input(" "*indent + prompt, mark="", value=value)


    def display_wait(self, message: str, duration: float = 2.0, spinner_type: str = "balloon2", indent: int = 0):
        """
        Affiche un spinner avec un préfixe pendant une durée définie.

        Args:
            message (str): Texte à afficher avant le spinner.
            duration (float): Durée en secondes pendant laquelle afficher le spinner (par défaut 2.0 secondes).
            spinner_type (str): Type de spinner (par défaut 'dots'). Voir la documentation de rich pour d'autres options.
            indent (int): Niveau d'indentation.
        """

        indentation = " " * indent
        with self.console.status(f"{indentation}{message}...", spinner=spinner_type,spinner_style = "bold white") :
            time.sleep(duration)

    def display_with_type(self, value, level=2,indent: int = 0, color: str = "bright_cyan"):
        """
        Affiche une valeur avec son type détecté depuis une chaîne.

        Args:
            value (str): La valeur à analyser et afficher.
            level (int): Niveau de verbosité requis pour afficher la valeur.
            indent (int): Niveau d'indentation pour l'affichage.
            color (str): Couleur pour la sortie via Rich.

        """

        if isinstance(value, str):
            # Détection d'une adresse IP
            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", value):
                detected_type = "IP"
            # Détection d'un float
            elif re.match(r"^-?\d+\.\d+$", value):
                detected_type = "float"
            # Détection d'un int
            elif re.match(r"^-?\d+$", value):
                detected_type = "int"
            # Détection d'une chaîne générique
            else:
                detected_type = "string"
        else:
            detected_type = type(value).__name__

        # Formatage du message
        formatted_message = f"({detected_type}) : {str(value)}"

        # Affichage avec indentation
        self.display(formatted_message, level=level, color=color, indent=indent)

    @staticmethod
    def display_agree(prompt: str, default=True,indent=0) -> bool:
        return sv.routines.inquire(" "*indent+prompt, default=default, mark="")

    def display_progress(self, main_task_prefix: str, indent: int = 0, total_size: int = 100):
        """
        Retourne un context manager Rich pour gérer les tâches principales et secondaires,
        en plaçant l'indentation avant le SpinnerColumn.
        """

        class ProgressBarManager:
            def __init__(p_self):
                # On crée une console Rich
                p_self.console = self.console

                # On ajoute une colonne de texte pour l'indentation, puis le spinner, etc.
                p_self.progress = Progress(
                    TextColumn(" " * indent),  # <-- Colonne d'indentation (vide ou contenant X espaces)
                    #SpinnerColumn(spinner_name="balloon2",style = "bold white"),  # Spinner
                    "[cyan]{task.description}[/cyan] |",  # Description
                    BarColumn(bar_width=40,complete_style="cyan",finished_style="bright_cyan",),  # Barre de progression
                    "[progress.percentage][bold white]{task.percentage:>3.0f}% [/bold white]|",
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                    console=p_self.console,
                    transient=False
                )

                p_self.main_prefix = main_task_prefix
                p_self.main_total = total_size
                p_self.main_task_id: Optional[int] = None
                p_self.subtasks: List[int] = []

            def __enter__(p_self):
                # On démarre l'affichage de la barre
                p_self.progress.start()
                # On crée la tâche principale et on stocke son ID
                p_self.main_task_id = p_self.progress.add_task(
                    p_self.main_prefix,
                    total=p_self.main_total
                )
                return p_self

            def __exit__(p_self, exc_type, exc_val, exc_tb):
                # On arrête proprement la barre de progression
                p_self.progress.stop()

            # --- Méthodes pour la barre principale ---

            def update_main(
                    p_self,
                    advance: float = 1.0,
                    new_prefix: Optional[str] = None
            ) -> None:
                if p_self.main_task_id is None:
                    return

                if new_prefix:
                    p_self.progress.update(
                        p_self.main_task_id,
                        description=new_prefix
                    )
                p_self.progress.advance(p_self.main_task_id, advance=advance)

            # --- Méthodes pour les sous-tâches ---

            def add_subtask(
                    p_self,
                    prefix: str = "Subtask",
                    total: float = 100.0
            ) -> int:
                subtask_id = p_self.progress.add_task(prefix, total=total)
                p_self.subtasks.append(subtask_id)
                return subtask_id

            def update_subtask(
                    p_self,
                    subtask_id: int,
                    advance: float = 1.0,
                    new_prefix: Optional[str] = None
            ) -> None:
                if new_prefix:
                    p_self.progress.update(subtask_id, description=new_prefix)
                p_self.progress.advance(subtask_id, advance=advance)

            def remove_subtask(p_self, subtask_id: int) -> None:
                time.sleep(1)
                p_self.progress.remove_task(subtask_id)
                p_self.subtasks.remove(subtask_id)

        # On retourne l'instance du gestionnaire
        return ProgressBarManager()


    # Easter Egg
    @staticmethod
    def display_themis_the_cat():
        print("\n" + colored(" _._     _,-'\"\"`-._\n"
                             "(,-.`._,'(       |\`-/|\n"
                             "    `-.-' \ )-`( , o o)\n"
                             "           `-    \`_`\"'-\n",
                             'yellow') + "\n")
        return ""


