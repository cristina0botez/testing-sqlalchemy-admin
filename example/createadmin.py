from getpass import getpass
from example.models import Session, User


if __name__ == '__main__':
    username = input('Username: ').strip()
    password = getpass()
    user = User(username=username, password=password, is_admin=True)
    with Session() as session:
        session.add(user)
        session.commit()
