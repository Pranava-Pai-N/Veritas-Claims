class DBException(Exception):
    def __init__(self, status_code : int, errors : list[str] | str):
        super().__init__()
        self.status_code = status_code
        self.errors = errors