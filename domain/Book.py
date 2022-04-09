class Book:
    def __init__(self, category, name, author):
        self.id = None
        self.cover = None
        self.hot = None
        self.status = None
        self.attribute = None
        self.chapters = []
        self.description = None
        self.name = name
        self.category = category
        self.author = author
        self.word = None
        self.update = None

    def set_description(self, description):
        self.description = description

    def set_category(self, category):
        self.category = category

    def set_word(self, word):
        self.word = word

    def add_chapter(self, chapter):
        self.chapters.append(chapter)

    def add_attribute(self, attr):
        self.attribute = attr

    def get_attribute(self):
        return self.attribute

    def set_status(self, status):
        self.status = status

    def set_hot(self, hot):
        self.hot = hot

    def set_update(self, update):
        self.update = update

    def set_cover(self, cover):
        self.cover = cover

    def get_chapter(self):
        return self.chapters

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def tostring(self):
        print(self.name, self.category, self.author, self.word, self.update, self.hot, self.status,
              self.attribute, self.cover, self.description)
