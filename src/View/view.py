from termcolor import colored

class View:
    def __init__(self, verbosity = 2) -> None:
        # verbosity : 
        # 0 -> fundamental
        # 1 -> important
        # 2 -> normal
        # 3 -> detail
        # 4 -> debug
        self.verbosity = verbosity
        
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
                        context = symbol + context
                        break
                else:
                    color = "white"

            # Ajoute le contexte au message s'il est fourni
            full_message = f"{context} {message}" if context else message

            # Affiche le message mieux que HTLM et CSS ;)
            print(colored(full_message, color))
