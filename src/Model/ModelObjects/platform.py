class Platform:
    def __init__(self,values:dict):
        
        self.minimum_ram = None
        self.minimum_cpu_core = None
        self.minimum_free_space = None
        
        self.recommended_ram = None
        self.recommended_free_space = None
        self.recommended_cpu_core = None
        
        self.os_type = None
        self.recommended_os = None
        self.package = None
        self.version = None
        self.architecture = None
        
        self.admin_rights_needed = None
       
        self.load_platform(values)
    
    def load_platform(self,values:dict):
        for key, value in values.items():
            if hasattr(self, key):  # Vérifie si l'attribut existe
                setattr(self, key, value)
            else:
                print(f"Clé inconnue ignorée : {key}")
            

    def __str__(self):
        details = [
            #f"OS Type: {self.os_type or 'Unknown'}",
            #f"OS Version: {self.os_type or 'Unknown'}",
            f"{self.recommended_os or 'Unknown'} [",
            f"Package Manager: {self.package or 'Unknown'} ,",
            f"Architecture: {self.architecture or 'Unknown'}] ",
            #f"Admin Rights: {'Yes' if self.admin_rights_needed else 'No'}",

        ]
        return "".join(details)