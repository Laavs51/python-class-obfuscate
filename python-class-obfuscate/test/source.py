import os


class ProjectItemLocation:
    """ Положение узла в дереве """

    def __init__(self, path='/', id_path='/'):
        super()
        self.path = path
        self.id_path = id_path

    def child(self, item):
        """ Положение дочернего узла """
        path = self._item_path(self.path, item)
        id_path = self._item_path(self.id_path, item, use_id=True)

        return ProjectItemLocation(path, id_path)

    @staticmethod
    def _item_path(parent_path, item, use_id=False):
        """ Путь к дочернему элементу """
        if parent_path is None:
            return '/'

        if use_id:
            next_part = str(id(item))
        else:
            next_part = item

        if parent_path == '/':
            return next_part

        return os.path.join(parent_path, next_part)


if __name__ == '__main__':
    print(ProjectItemLocation().child('test'))
