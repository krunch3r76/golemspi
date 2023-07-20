# ./model.py
from .model_additions import ModelAdditions
from .model_retrievals import ModelRetrievals
from .model_updates import ModelUpdates
from model.database import connection
from model.flags.view_update_flags import view_update_flags

# from .objects.version_info import VersionInfo, HardwareResourceInfo



class Model:
    def __init__(self):
        self.connection = connection
        self.view_update_flags = view_update_flags
        self.additions = ModelAdditions(self)
        self.retrievals = ModelRetrievals(self)
        self.updates = ModelUpdates(self)
        self.version_info = None
        self.hardware_resource_cap_info = None
        self.payment_networks = []
        self.subnet = None
        
    def get_active_flags(self):
    # Return the update flags that are set to True
        return [ key for key, value in self.view_update_flags.items() if value ]

    def reset_view_update_flags(self):
        for attribute in self.view_update_flags:
            self.view_update_flags[attribute] = False

    # def get_task(self, task_id):
    #     # Retrieve task based on ID
    #     pass
