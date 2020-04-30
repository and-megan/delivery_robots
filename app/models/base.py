from app import db


class Base(object):
    @classmethod
    def create(cls, *args):
        raise NotImplemented()

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_all(cls, query_string=None):
        return cls.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if value:
                self.key = value

        db.session.add(self)
        db.session.commit()
        return self
