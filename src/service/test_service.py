from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
import pytest

from src.Exceptions import UserFindException, UserLoginException, UserPasswordException, UserRegisterException
from src.repository.db_models import User, GpsTrack
from src.service.main_service import MainService
from src.service.models.loginIn import LoginIn
from src.service.models.registerIn import RegisterIn
from src.service.service_models import TokenModel


def get_service():
    return MainService()


class TestLogic(IsolatedAsyncioTestCase):

    async def test_add_gps_successful(self):
        with (patch('src.service.main_service.get_user_by_id') as get_user_by_id,
              patch('src.service.main_service.add_gps') as add_gps):
            get_user_by_id.return_value = User(
                id='1',
                name='name',
                email='email',
                password='password',
                role='User',
                register_date=datetime.now())
            add_gps.return_value = GpsTrack(
                id='1',
                user_id='1',
                latitude='1',
                longitude='1',
                timestamp=datetime.now()
            )

            track = get_service().add_gps(user_id='1', latitude='1', longitude='1', timestamp=datetime.now())

            assert get_user_by_id.call_count == 1
            assert add_gps.call_count == 1
            assert track.user_id == '1'

    async def test_add_gps_user_none(self):
        with (patch('src.service.main_service.get_user_by_id') as get_user_by_id,
              patch('src.service.main_service.add_gps') as add_gps):
            get_user_by_id.return_value = None
            add_gps.return_value = GpsTrack(
                id='1',
                user_id='1',
                latitude='1',
                longitude='1',
                timestamp=datetime.now()
            )
            with pytest.raises(UserFindException):
                get_service().add_gps(user_id='1', latitude='1', longitude='1', timestamp=datetime.now())

            assert get_user_by_id.call_count == 1
            assert add_gps.call_count == 0

    async def test_get_tracks_by_date_call_from_user_successful(self):
        with (patch('src.service.main_service.get_all_tracks_by_date') as get_all_tracks_by_date,
              patch('src.service.main_service.get_tracks_by_date_userid') as get_tracks_by_date_userid):
            get_all_tracks_by_date.return_value = [
                GpsTrack(
                    id='1',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                ),
                GpsTrack(
                    id='2',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                )
            ]
            get_tracks_by_date_userid.return_value = [
                GpsTrack(
                    id='1',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                ),
                GpsTrack(
                    id='2',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                )
            ]

            one_day = timedelta(days=1)
            start_date = datetime.now() - one_day
            end_date = datetime.now() + one_day
            track = get_service().get_tracks_by_date(start_date, end_date,
                                                     TokenModel(user_id='1', email='email', role='User'))

            assert get_all_tracks_by_date.call_count == 0
            assert get_tracks_by_date_userid.call_count == 1
            assert len(track) == 2

    async def test_get_tracks_by_date_call_from_admin_successful(self):
        with (patch('src.service.main_service.get_all_tracks_by_date') as get_all_tracks_by_date,
              patch('src.service.main_service.get_tracks_by_date_userid') as get_tracks_by_date_userid):
            get_all_tracks_by_date.return_value = [
                GpsTrack(
                    id='1',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                ),
                GpsTrack(
                    id='2',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                )
            ]
            get_tracks_by_date_userid.return_value = [
                GpsTrack(
                    id='1',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                ),
                GpsTrack(
                    id='2',
                    user_id='1',
                    latitude='1',
                    longitude='1',
                    timestamp=datetime.now()
                )
            ]

            one_day = timedelta(days=1)
            start_date = datetime.now() - one_day
            end_date = datetime.now() + one_day
            track = get_service().get_tracks_by_date(start_date, end_date,
                                                     TokenModel(user_id='3', email='email', role='Administrator'))

            assert get_all_tracks_by_date.call_count == 1
            assert get_tracks_by_date_userid.call_count == 0
            assert len(track) == 2

    async def test_login_successful(self):
        with (patch('src.service.main_service.get_user_by_email') as get_user_by_email,
              patch('src.service.main_service.verify_password') as verify_password,
              patch('src.service.main_service.create_access_token') as create_access_token):
            get_user_by_email.return_value = User(
                id='1',
                name='name',
                email='email',
                password='password',
                role='User',
                register_date=datetime.now())
            verify_password.return_value = True
            create_access_token.return_value = "token"

            token = get_service().login(LoginIn(email='email', password='password'))

            assert get_user_by_email.call_count == 1
            assert verify_password.call_count == 1
            assert create_access_token.call_count == 1
            assert token == "token"

    async def test_login_user_none(self):
        with (patch('src.service.main_service.get_user_by_email') as get_user_by_email,
              patch('src.service.main_service.verify_password') as verify_password,
              patch('src.service.main_service.create_access_token') as create_access_token):
            get_user_by_email.return_value = None
            verify_password.return_value = True
            create_access_token.return_value = "token"

            with pytest.raises(UserLoginException):
                get_service().login(
                    LoginIn(email='email', password='password')
                )

            assert get_user_by_email.call_count == 1
            assert verify_password.call_count == 0
            assert create_access_token.call_count == 0

    async def test_login_wrong_password(self):
        with (patch('src.service.main_service.get_user_by_email') as get_user_by_email,
              patch('src.service.main_service.verify_password') as verify_password,
              patch('src.service.main_service.create_access_token') as create_access_token):
            get_user_by_email.return_value = User(
                id='1',
                name='name',
                email='email',
                password='password',
                role='User',
                register_date=datetime.now())
            verify_password.return_value = False
            create_access_token.return_value = "token"

            with pytest.raises(UserPasswordException):
                get_service().login(
                    LoginIn(email='email', password='password')
                )

            assert get_user_by_email.call_count == 1
            assert verify_password.call_count == 1
            assert create_access_token.call_count == 0

    async def test_register_successful(self):
        with (patch('src.service.main_service.get_user_by_email') as get_user_by_email,
              patch('src.service.main_service.get_password_hash') as get_password_hash,
              patch('src.service.main_service.create_user') as create_user,
              patch('src.service.main_service.get_user_by_id') as get_user_by_id):
            get_password_hash.return_value = 'hashedpassword'
            get_user_by_email.return_value = None
            create_user.return_value = "1"
            user = User(
                id='1',
                name='name',
                email='email',
                password='hashedpassword',
                role='User',
                register_date=datetime.now())
            get_user_by_id.return_value = user

            reg_out = get_service().register(
                RegisterIn(name='name', email='email', password='password')
            )

            assert reg_out.email == user.email
            assert get_user_by_email.call_count == 1
            assert get_password_hash.call_count == 1
            assert create_user.call_count == 1
            assert get_user_by_id.call_count == 1

    async def test_register_user_email_exist(self):
        with (patch('src.service.main_service.get_user_by_email') as get_user_by_email,
              patch('src.service.main_service.get_password_hash') as get_password_hash,
              patch('src.service.main_service.create_user') as create_user,
              patch('src.service.main_service.get_user_by_id') as get_user_by_id):
            get_password_hash.return_value = 'hashedpassword'
            user = User(
                id='1',
                name='name',
                email='email',
                password='hashedpassword',
                role='User',
                register_date=datetime.now())
            get_user_by_email.return_value = user
            create_user.return_value = "1"
            get_user_by_id.return_value = user

            with pytest.raises(UserRegisterException):
                get_service().register(
                    RegisterIn(name='name', email='email', password='password')
                )

            assert get_user_by_email.call_count == 1
            assert get_password_hash.call_count == 1
            assert create_user.call_count == 0
            assert get_user_by_id.call_count == 0
