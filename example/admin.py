from datetime import datetime, timezone
import logging
from secrets import token_urlsafe

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm.exc import NoResultFound
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from example.models import User, Person, Actor, Director, Movie, Session, engine


logger = logging.getLogger(__name__)


class MyBackend(AuthenticationBackend):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs['same_site'] = 'strict'
        kwargs['https_only'] = True
        self.middlewares = [Middleware(SessionMiddleware, **kwargs)]

    async def login(self, request):
        form = await request.form()
        username, password = form['username'], form['password']
        session_token = token_urlsafe(64)
        login_time = datetime.now(timezone.utc)
        with Session() as session:
            user = session.query(User).filter(User.username==username).one()
            user.session_token = session_token
            user.last_login = login_time
            session.commit()
        request.session.update({'token': session_token})
        return True

    async def logout(self, request):
        try:
            session_token = request.session.pop('token')
        except KeyError:
            pass
        with Session() as session:
            user = session.query(User).filter(User.session_token==session_token).one()
            user.session_token = None
            session.commit()
        request.session.clear()
        return True

    async def authenticate(self, request):
        try:
            session_token = request.session['token']
        except KeyError:
            return False
        else:
            with Session() as session:
                try:
                    user = session.query(User).filter(User.session_token==session_token).one()
                except NoResultFound:
                    logger.warning(f'No user found for session: {request.session}')
                    return False
            if user.is_admin:
                return True
            else:
                return False


class PersonAdmin(ModelView, model=Person):
    column_list = [Person.id, Person.name, Person.nickname]


app = FastAPI()
authentication_backend = MyBackend(secret_key='&48loo=al*sx3)0ruvvtqv)9-#u3f5_h$9*l9rhi_tg(udumb_')
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(PersonAdmin)
