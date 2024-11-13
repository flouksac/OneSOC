from Utils.os_info import get_os, get_os_type, get_os_version

class Platform:
    def __init__(self):
        self.data = {}
        self.retrieve_os()

    def retrieve_os(self):
        self.data['os_name'] = get_os()
        self.data['os_type'] = get_os_type()
        self.data['os_version'] = get_os_version()


