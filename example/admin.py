from datetime import datetime, timezone
from secrets import token_urlsafe

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from example.models import User, Person, Actor, Director, Movie, Session


app = FastAPI()


class MyBackend(AuthenticationBackend):
    def login(self, request):
        form = request.form()
        username, password = form['username'], form['password']
        session_token = token_urlsafe(64)
        login_time = datetime.now(timezone.utc)
        with Session() as session:
            user = session.query(User).filter(User.username==username).one()
            user.session_token = session_token
            user.last_login = login_time
            session.commit()
        request.session.update({'token': user.session_token})

        return True

    def logout(self, request):
        session_token = request.session['token']
        with Session() as session:
            user = session.query(User).filter(User.session_token==session_token).one()
            user.session_token = None
            session.commit()
        request.session.clear()
        return True

    def authenticate(self, request):
        token = request.session.get('token')

        if not token:
            return False

        # Check the token
        return True

class PersonAdmin(ModelView, model=Person):
    column_list = [Person.id, Person.name, Person.nickname]


authentication_backend = MyBackend(secret_key='&48loo=al*sx3)0ruvvtqv)9-#u3f5_h$9*l9rhi_tg(udumb_')
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(PersonAdmin)
