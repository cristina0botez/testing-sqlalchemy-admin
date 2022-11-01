import logging
from datetime import datetime, timezone
from passlib.context import LazyCryptContext
from secrets import token_urlsafe

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils.types.password import Password
from starlette.datastructures import FormData
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from wtforms import StringField, Form
from wtforms.validators import NumberRange

from example.models import User, Person, Actor, Director, Movie, Session, engine


app = FastAPI()
logger = logging.getLogger(__name__)


class MyBackend(AuthenticationBackend):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs['same_site'] = 'strict'
        kwargs['https_only'] = True
        kwargs['max_age'] = 3600  # 1 hour
        self.middlewares = [Middleware(SessionMiddleware, **kwargs)]

    async def login(self, request):
        form = await request.form()
        username, password = form['username'], form['password']
        session_token = token_urlsafe(64)
        login_time = datetime.now(timezone.utc)
        with Session() as session:
            try:
                user = session.query(User).filter(User.username==username).one()
            except NoResultFound:
                return False
            if user.password == password:
                user.session_token = session_token
                user.last_login = login_time
                session.commit()
            else:
                return False
        request.session.update({'token': session_token})
        return True

    async def logout(self, request):
        try:
            session_token = request.session.pop('token')
        except KeyError:
            pass
        with Session() as session:
            try:
                user = session.query(User).filter(User.session_token==session_token).one()
            except NoResultFound:
                logger.debug(f'No user found for session: {request.session}')
            else:
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


class EditablePasswordField(StringField):

    def process_data(self, value):
        # We don't want to display the password in the form.
        self.data = ''


class UserForm(Form):

    def process(self, formdata=None, obj=None, data=None, extra_filters=None, **kwargs):
        if not formdata:
            super().process(formdata=formdata, obj=obj, data=data, extra_filters=extra_filters, **kwargs)
            return
        username = formdata['username']
        given_password = formdata['password']
        if given_password == '':
            context = LazyCryptContext(schemes=['pbkdf2_sha512'])
            with Session() as session:
                user = session.query(User).filter(User.username==username).one()
                password = Password(user.password.hash, context)
            input_items = dict(formdata.multi_items())
            input_items['password'] = password
            formdata = FormData(input_items)
        super().process(formdata=formdata, obj=obj, data=data, extra_filters=extra_filters, **kwargs)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.is_admin]
    icon = 'fa-solid fa-user-circle'
    form_base_class = UserForm
    form_overrides = dict(password=EditablePasswordField)
    column_details_list = [User.id, User.username, User.is_admin, User.last_login, User.session_token]


class PersonAdmin(ModelView, model=Person):
    column_list = [Person.id, Person.name, Person.age]
    form_args = dict(age=dict(validators=[NumberRange(0, 150)]))
    name_plural = 'People'
    icon = 'fa-solid fa-users'

class DirectorAdmin(ModelView, model=Director):
    column_list = [Director.id, Director.person]
    form_columns = [Director.person, Director.movies]


class ActorAdmin(ModelView, model=Actor):
    column_list = [Actor.id, Actor.person]
    form_columns = [Actor.person, Actor.movies]


class MovieAdmin(ModelView, model=Movie):
    column_list = [Movie.id, Movie.title, Movie.year]
    form_columns = [Movie.title, Movie.year, Movie.rating, Movie.director, Movie.actors]


authentication_backend = MyBackend(secret_key='&48loo=al*sx3)0ruvvtqv)9-#u3f5_h$9*l9rhi_tg(udumb_')
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(PersonAdmin)
admin.add_view(DirectorAdmin)
admin.add_view(ActorAdmin)
admin.add_view(MovieAdmin)
