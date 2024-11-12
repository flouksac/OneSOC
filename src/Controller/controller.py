import argparse
from View.view import View
from Model.load_yaml import YamlLoader
#from Model.platform import Platform


class Controller:
    def __init__(self) -> None:
        self.view = View()
        self.model = {}
    
    def parse_arguments (self):
        
        """
        Keyword Arguments:
            * prog -- The name of the program (default: sys.argv[0])
            * usage -- A usage message (default: auto-generated from arguments)
            * description -- A description of what the program does
            * epilog -- Text following the argument descriptions
            * parents -- Parsers whose arguments should be copied into this one
            * formatter_class -- HelpFormatter class for printing help messages
            * prefix_chars -- Characters that prefix optional arguments
            * fromfile_prefix_chars -- Characters that prefix files containing additional arguments
            * argument_default -- The default value for all arguments
            * conflict_handler -- String indicating how to handle conflicts
            * add_help -- Add a -h/-help option
            * allow_abbrev -- Allow long options to be abbreviated unambiguously
            * exit_on_error -- Determines whether or not ArgumentParser exits with error info when an error occurs
        
        """ 
        parser = argparse.ArgumentParser(description="a complete SOC deployement in one command")
                
        parser.add_argument('config',type=str,default="../config.yaml",help="Configuration File Path")
        parser.add_argument('-v', '--verbosity', action='count', default=0, help="Verbosity level of the script (-v basic information to -vvvvv very detailled)")

        args = parser.parse_args()
        return args
        
    def load_model(self,config_path):
        self.model["Config"] = YamlLoader(config_path)
        # self.model["Platform"] = Platform() # TODO -> do basic check now or later ??? can be null now ?
        
    def run(self):
        args = self.parse_arguments()
        
        self.view.set_verbosity(args.verbosity)
        self.load_model(args.config)
        
        self.view.display("Initialisation terminé",4,"success")
        