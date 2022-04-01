class Chapter:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.content = None

    def getId(self):
        return self.id

    def setContent(self, content):
        self.content = content

    def toString(self):
        print(self.id, self.name, self.content)
