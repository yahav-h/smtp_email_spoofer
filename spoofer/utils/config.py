from os.path import join, abspath, dirname, exists


class Config:
    __ROOT_DIR__ = dirname(dirname(dirname(abspath(__file__))))
    __ATTACHMENTS__ = 'attachments'
    __TEMPLATES__ = 'templates'

    @staticmethod
    def get_attachments():
        _exec = lambda: join(Config.__ROOT_DIR__, Config.__ATTACHMENTS__)
        return _exec()

    @staticmethod
    def get_templates():
        _exec = lambda: join(Config.__ROOT_DIR__, Config.__TEMPLATES__)
        return _exec()
