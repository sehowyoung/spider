import logging


class Log:
    def __init__(self):
        self.LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    def log(self, target, level, msg):
        if target == 'download':
            logging.basicConfig(filename='doc/log/downloadCover.log', level=logging.DEBUG, format=self.LOG_FORMAT)
        elif target == 'reptile':
            logging.basicConfig(filename='doc/log/scrapingText.log', level=logging.DEBUG, format=self.LOG_FORMAT)

        logging.log(level, msg)
