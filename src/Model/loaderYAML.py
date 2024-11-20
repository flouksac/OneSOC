import yaml

class YamlLoader:
    def __init__(self, file:str) -> None:
        self.file = file
        self.data:dict = {}
        self.load_config()
        
    def load_config(self):
        try : 
            with open(self.file,'r') as file : 
                self.data = yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception("Le fichier de configuration est introuvable.") # TODO on passe ca plutot avec la vue ?
        except yaml.YAMLError:
            raise Exception("Erreur de format dans le fichier de configuration")  # TODO on passe ca plutot avec la vue ?
        
        