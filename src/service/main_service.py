from datetime import datetime
from typing import List

from src.Exceptions import UserLoginException, UserRegisterException, UserFindException
from src.endpoints.apis.main_api import UserPasswordException
from src.endpoints.security_api import verify_password, create_access_token, get_password_hash
from src.repository.db_models import User
from src.repository.repository import get_user_by_email, create_user, add_gps, get_all_tracks_by_date, \
    get_tracks_by_date_userid, get_user_by_id
from src.service.models.loginIn import LoginIn
from src.service.models.registerIn import RegisterIn
from src.service.models.registerOut import RegisterOut
from src.service.models.role import Role
from src.service.models.trackOut import TrackOut
from src.service.service_models import TokenModel


class MainService:
    def add_gps(self, user_id: str, latitude: str, longitude: str, timestamp: datetime) -> TrackOut:
        if get_user_by_id(user_id) is None:
            raise UserFindException
        track = add_gps(user_id, latitude, longitude, timestamp)
        return TrackOut(
            id=track.id,
            user_id=track.user_id,
            latitude=track.latitude,
            longitude=track.longitude,
            timestamp=track.timestamp,
        )

    def get_tracks_by_date(self, start_date: datetime, end_date: datetime, token_bearerAuth: TokenModel) -> List[
        TrackOut]:
        if token_bearerAuth.role == Role.ADMIN.value:
            tracks = get_all_tracks_by_date(start_date, end_date)
        else:
            tracks = get_tracks_by_date_userid(start_date, end_date, token_bearerAuth.user_id)
        filtered_tracks = []
        for track in tracks:
            filtered_tracks.append(
                TrackOut(
                    id=track.user_id,
                    user_id=track.user_id,
                    latitude=track.latitude,
                    longitude=track.longitude,
                    timestamp=track.timestamp))
        return filtered_tracks

    def login(self, login_in: LoginIn) -> str:
        email = login_in.email
        password = login_in.password

        user = get_user_by_email(email)
        if user:
            hashed_password = user.password
        else:
            raise UserLoginException

        if not verify_password(password, hashed_password):
            raise UserPasswordException

        token = create_access_token(
            data={"email": email, "user_id": user.id, "role": user.role}
        )

        return token

    def register(self, register_in: RegisterIn) -> RegisterOut:
        name = register_in.name
        email = register_in.email
        password = register_in.password
        hashed_password = get_password_hash(password)

        if get_user_by_email(email):
            raise UserRegisterException

        user_id = create_user(name, email, hashed_password)
        user = get_user_by_id(user_id)

        return RegisterOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            register_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), )

    def user_exists(self, user_id: str) -> bool:
        return get_user_by_id(user_id) is not None
