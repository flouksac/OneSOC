import argparse
import importlib
import os

from Controller.host_controller import HostController
from Controller.list_controller import ListController
from Model.ModelObjects.option import Option
from View.main_view import View,colored
from Model.main_model import Model

class Parser:
    def __init__(self):
        self.args = self.parse_arguments()
        self.view = View()
        self.model = Model()

    def get_verbosity(self): return self.args.verbosity

    def get_config_path(self): return self.args.config_path

    def get_controller(self, string_user):
        """ Returns the correct controller class dynamically after importing it. """
        string_controller = (
                string_user.replace("-", "_").lower() + "_controller")  # -> wazuh-indexer, Wazuh_Indexer_Controller

        possible_paths = [
            "Controller.ControllerService." + string_controller,
            "Controller.ControllerDocker." + string_controller
        ]

        for module_path in possible_paths:
            try:
                module = importlib.import_module(module_path)
                return getattr(module, string_controller.title())
            except (ModuleNotFoundError, AttributeError) as e:
                continue

        self.view.display("Wrong component name : " + string_user +
                          ". It could be a missing controller or a wrong spelling.", level=0, context="Fatal")
        exit(1)

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(prog="OneSOC", description="OneSOC deployment script", add_help=False)

        group_positional_arguments = parser.add_argument_group(colored("Positional arguments", "cyan"))
        group_positional_arguments.add_argument('config_path', type=str,
                                                default=os.path.join(os.path.dirname(__file__), "./../../config.yaml"),
                                                nargs='?', help="configuration file path (default: %(default)s)")

        group_options = parser.add_argument_group(colored("Options", "cyan"))
        group_options.add_argument('-h', '--help', action='help', help="Show this help message and exit")
        group_options.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2, 3, 4], default=2,
                                   required=False, help="verbosity level (default: %(default)s)", metavar='Int')

        # List possibility
        group_list = parser.add_argument_group(colored("Listing flags", "cyan"))
        group_list.add_argument('-lA', '--list-action', action='store_true',
                                help="List all possible action")

        group_list.add_argument('-lO', '--list-option', nargs='*', metavar='\"COMPONENT\"', type=str.lower,
                                help="List all option for each action")

        group_list.add_argument('-lC', '--list-component', action='store_true',
                                help="List all components that can be installed")

        # Actions "read only"
        group_read = parser.add_argument_group(colored("Read-only flags", "cyan"))
        group_read.add_argument('--info', nargs='*', metavar='\"COMPONENT\"',
                                help="Informations sur les composants installés")
        group_read.add_argument('--healthcheck', nargs='*', metavar='COMPONENT',
                                help="Vérifie la santé des composants")

        # Action Installation
        group_install = parser.add_argument_group(colored("Installation flags", "cyan"))
        group_install.add_argument('--install', nargs='+', metavar='\"COMPONENT\"',
                                   help="Installe un ou plusieurs composants")
        group_install.add_argument('--install-option', nargs='+', metavar='\"OPTION=VALUE\"',
                                   help="Options d'installation pour les composants")

        # Action Config
        group_config = parser.add_argument_group(colored("Configuration flags", "cyan"))
        group_config.add_argument('--config', type=str, metavar='\"COMPONENT\"',
                                  help="Met à jour la configuration d'un composant")
        group_config.add_argument('--config-option', nargs='+', metavar='\"OPTION=VALUE\"',
                                  help="Options d'installation pour les composants")

        # Action Repair
        group_repair = parser.add_argument_group(colored("Reparation flags", "cyan"))
        group_repair.add_argument('--repair', nargs='*', metavar='\"COMPONENT\"',
                                  help="Répare un ou plusieurs composants ou tous les composants défectueux")

        return parser.parse_args()


    def parse_list(self):
        list_controller = ListController()
        
        if self.args.list_action:
            list_controller.get_actions()

        if self.args.list_component:
            list_controller.get_components()

        if self.args.list_option is not None:
            list_controller.get_options(self.args.list_option)
  
    @staticmethod
    def parse_option(options):
        if not options:
            return []

        instanced_options = []
        for option in options:
            key, value = option.split("=")
            instanced_options.append( Option(key, value))
        return instanced_options

    def parse_action(self):
        if self.args.info is not None:
            targets = [comp.name for comp in self.model.get_all_components()] if len(
                self.args.info) == 0 else self.args.info
            for target in targets:
                self.get_controller(target)().info()

        if self.args.healthcheck is not None:
            targets = [comp.name for comp in self.model.get_all_components()] if len(
                self.args.healthcheck) == 0 else self.args.healthcheck
            for target in targets:
                self.get_controller(target)().healthcheck()

        if self.args.install is not None:
            if not self.args.install:
                self.view.display("Error : No component specified for installation.", level=0, context="Fatal")
                exit(1)
            else:
                for i in range(len(self.args.install)): # in the controller install, we have to pick the options we need
                    self.get_controller(self.args.install[i])(self.parse_option(self.args.install_option)).install()

        if self.args.config is not None:
            if not self.args.config:
                self.view.display("Error : No component specified for configuration.", level=0, context="Fatal")
                exit(1)
            else:
                for i in range(len(self.args.config)): # in the controller install, we have to pick the options we need
                    self.get_controller(self.args.config[i])(self.parse_option(self.args.config_option)).config()

        if self.args.repair is not None:
            targets = [comp.name for comp in self.model.get_all_components()] if len(
                self.args.repair) == 0 else self.args.repair
            for target in targets:
                self.get_controller(target)().repair()


    def parse_manually(self):
        self.view.display("As no arguments has been passed, here is the manual menu :\n", level=0,
                          color="bright_cyan")

        host_controller = HostController()
        all_components = self.model.get_all_components()

        mapping_component_and_supported_version = {}
        self.view.display("Checking compatibility with your system to determine which component you can work with",level=3,context="info")
        self.view.display(f"Your system is interpreted as {host_controller.get_host()}: ",level=3,context="info")

        for component in all_components:
            self.view.display(f"Checking compatibility for {component.name} with your system",level=3,context="info")
            for platform in component.supported_platform:
                try:
                    if host_controller.is_fully_compatible(platform):
                        mapping_component_and_supported_version[component] = ["fully_compatible",platform]
                        self.view.display(f"{component.name} is fully compatible with {platform}",level=3,
                                          context="info",color="bright_green",indent=2)
                        break
                    elif host_controller.is_minimum_compatible(platform):
                        mapping_component_and_supported_version[component] = ["minimum_compatible", platform]
                        self.view.display(f"{component.name} as the minimum compatibility with system, interpreted as {platform}",
                                          level=3,context="Debug",color="yellow",indent=2)

                except Exception as e:
                    self.view.display(f"Finding compatibility as {platform} failed : {e} ", level=4, context="Debug",color="red",indent=2)

        possible_action = []
        for component in mapping_component_and_supported_version.keys():
            for component_action in component.actions:
                if component_action.name  not in [action.name for action in possible_action] :
                        possible_action.append(component_action)

        chosen_actions = set()
        while len(chosen_actions) == 0:
            chosen_actions = self.view.display_selector_multiple("Which action do you want to do ? ",
                                                                 [action.name for action in possible_action])
            self.view.display('')

        for action in [action for index,action in enumerate(self.model.get_all_actions()) if index in chosen_actions ]:

            all_action_components = self.model.get_all_components_by_action(action.name)
            supported_components = [c for c in all_action_components if c in mapping_component_and_supported_version]
            allowed_names = [c.name for c in supported_components]

            chosen_components = set()
            while len(chosen_components) == 0:
                chosen_components = self.view.display_selector_multiple("With the action : " +
                                                                        colored(f"{action.name}","light_cyan")+
                                                                        ",\nSelect the component that you need : ",
                                                                        allowed_names)

            for component in [component for index,component in enumerate(supported_components) if index in chosen_components ]:
                
                options = []
                if action.name.lower() in ["install","config"]:
                    self.view.display("")
                    self.view.display_wait("You will have to configure the [bright_cyan]"+component.name+"[/bright_cyan] component ")
                    self.view.display("Configuration of '[bright_cyan]"+component.name+"[/bright_cyan]' ",indent=2)

                    for option in component.options:
                    
                        value = self.view.display_input(f"Enter a custom value for {option.key} (or keep default) : ",
                                                        str(option.value), indent=2) or str(option.value)

                        self.view.display_with_type( value,2,color="bright_cyan",indent=2)
                        options.append(Option(option.key,value))

                    # self.view.display(f"\nThis is the configuration you have chosen for {component.name} : ",2,indent=2)
                    # self.view.display_pretty_dict(options)

                    self.view.display("")
                    if mapping_component_and_supported_version[component][0] == "minimum_compatible":
                        self.view.display("This component is not fully compatible with your system, "
                                          "but it is the minimum required.",2,indent=2,context="warning")

                    if mapping_component_and_supported_version[component][0] == "fully_compatible":
                        self.view.display("This component fully compatible with your system, "
                                          "but it is the minimum required.",3,indent=2,context="info")

                    user_has_confirm = self.view.display_agree(f"Do you want to keep this configuration and run '" +
                                                               colored(action.name,"light_cyan") + "' on '" +
                                                               colored(component.name,"light_cyan") +
                                                               "' with the current configuration ? ",True,
                                                               indent=2)
                    if not user_has_confirm:
                        self.view.display("Silent Aborting without causing any error",0,context="Fatal")
                        exit(1)

                #self.view.display_wait(f"\nRunning the action '"+colored(action.name,"light_cyan")+ "' on the component '"+
                #                        colored(component.name,"light_cyan")+"' ")
                self.view.display("Please wait and do nothing while the action is not done.",2,indent=2)

                try :
                    getattr(self.get_controller(component.name)(options),action.name.lower())()
                except Exception as e:
                    self.view.display(f"A problem occured while trying to {action.name} on {component.name} : {e}",
                                      level=0, context="Fatal")
                    exit(1)

            self.view.display("\n")

    def parse(self):

        if any([self.args.list_action, self.args.list_option, self.args.list_component]) or self.args.list_option == []:
            self.parse_list()

        # appel de controlleur dynamique pour ci dessous:
        elif any(
                arg is not None or arg == [] for arg in [
                    self.args.info,
                    self.args.healthcheck,
                    self.args.install,
                    self.args.config,
                    self.args.repair,
                ]):
            self.parse_action()

        else:  # modifier configuration
            self.parse_manually()
