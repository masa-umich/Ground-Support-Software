


from ClientWidget import ClientWidget


class LiveDataHandler:

    def __init__(self, gui: None):

        self._gui = gui
        self._client = ClientWidget(True, self._gui)

    def sendCommand(self, cmd_id: int, args: dict):
        self._client.command(cmd_id, args)

    def getClient(self):
        return self._client