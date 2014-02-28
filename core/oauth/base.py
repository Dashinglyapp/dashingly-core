class OauthBase(object):
    handler = None

    def __init__(self, handler_obj):
        self.handler_obj = handler_obj

    def get_or_create(self, name, **kwargs):
        from core.database.models import Authorization
        from flask.ext.login import current_user
        from app import db

        inst = db.session.query(Authorization).filter_by(name=name, user=current_user).first()
        if inst:
            for k in kwargs:
                setattr(inst, k, kwargs[k])
        else:
            inst = Authorization(name=name, user=current_user, **kwargs)
            db.session.add(inst)
        db.session.commit()