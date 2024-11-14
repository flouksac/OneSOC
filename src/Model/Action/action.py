from Model.load_yaml import YamlLoader

def get_actions():
    yaml = YamlLoader(__file__+"/../action.yaml")
    return yaml.data
