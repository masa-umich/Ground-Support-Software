import json

# TODO: Actually implement this and update how objects are created


class ConfigurationManager:
    """
    This class handles the saving and loading of configurations
    """

    def __init__(self, gui, filepath: str = ""):

        self.gui = gui
        self.filepath = filepath
        self.jsonData = None

    def setFilename(self, filename: str):
        """
        Sets the filename the configuration is loaded from and saves to
        :param filename: filename
        """
        self.filename = filename

    def writeConfigurationToFile(self):
        with open(self.filepath, "w") as write_file:
            print()
            # json.dump(data, write_file, indent="\t")

    def loadConfigurationFromFile(self):
        # Open and read the loaded json file

        with open(self.filepath, "r") as read_file:
            self.jsonData = json.load(read_file)
