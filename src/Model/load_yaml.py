import yaml

class YamlLoader:
    def __init__(self, config_file:str) -> None:
        self.config_file = config_file
        self.data:dict = None
        self.load_config()
        
    def load_config(self):
        try : 
            with open(self.config_file,'r') as file : 
                self.data = yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception("Le fichier de configuration est introuvable.") # TODO on passe ca plutot avec la vue ?
        except yaml.YAMLError:
            raise Exception("Erreur de format dans le fichier de configuration")  # TODO on passe ca plutot avec la vue ?
        
        