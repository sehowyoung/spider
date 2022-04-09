class Chapter:
    def __init__(self, name, content):
        self.id = None
        self.name = name
        self.content = content

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_content(self, content):
        self.content = content

    def get_name(self):
        return self.name

    def get_content(self):
        return self.content

    def tostring(self):
        print(self.id, self.name, self.content)
