class Book:
    def __init__(self, category, name, author, word, recommend, update):
        self.cover = None
        self.hot = None
        self.status = None
        self.allList = None
        self.chapters = None
        self.description = None
        self.name = name
        self.category = category
        self.author = author
        self.word = word
        self.recommend = recommend
        self.update = update

    def setDescription(self, description):
        self.description = description

    def setCategory(self, category):
        self.category = category

    def setWord(self, word):
        self.word = word

    def addChapter(self, chapter):
        self.chapters.append(chapter)

    def setAllList(self, num):
        self.allList = num

    def setStatus(self, status):
        self.status = status

    def setHot(self, hot):
        self.hot = hot

    def setCover(self, cover):
        self.cover = cover

    def toString(self):
        print(self.name, self.category, self.author, self.word, self.recommend, self.update, self.hot, self.status,
              self.allList, self.cover, self.description)
