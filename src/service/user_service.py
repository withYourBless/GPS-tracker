from typing import List

from src.Exceptions import UserRegisterException
from src.endpoints.security_api import get_password_hash
from src.repository.repository import get_user_by_email, update_user_info, user_change_role, delete_user, get_all_users, \
    get_user_by_id, get_tracks_by_id
from src.service.models.infoOut import InfoOut
from src.service.models.registerIn import RegisterIn
from src.service.models.trackOut import TrackOut
from src.service.models.userOut import UserOut
from src.service.models.role import Role


class UserService:
    def update_user_info(self, user_id: str, user_info: RegisterIn) -> UserOut:
        name = user_info.name
        email = user_info.email
        password = user_info.password
        hashed_password = get_password_hash(password)

        start_user = get_user_by_id(user_id)
        if not start_user:
            raise UserRegisterException


        user = update_user_info(user_id, name, email, hashed_password)

        return UserOut(name=user.name,
                       email=user.email,
                       role=start_user.role,
                       register_date=start_user.register_date)

    def user_change_role(self, user_id: str, role: Role) -> UserOut:
        user = user_change_role(user_id, role.value)
        return UserOut(name=user.name,
                       email=user.email,
                       role=user.role,
                       register_date=user.register_date)

    async def delete_user(self, user_id: str) -> str:
        return delete_user(user_id)

    def get_users(self) -> List[UserOut]:
        users = []
        for user in get_all_users():
            users.append(UserOut(name=user.name,
                                 email=user.email,
                                 role=user.role,
                                 register_date=user.register_date))
        return users

    def get_my_tracks(self, user_id: str) -> List[TrackOut]:
        gps_tracks = get_tracks_by_id(user_id)
        tracks_out = []
        for track in gps_tracks:
            tracks_out.append(
                TrackOut(id=track.id,
                         user_id=track.user_id,
                         latitude=track.latitude,
                         longitude=track.longitude,
                         timestamp=track.timestamp, )
            )

        return tracks_out

    def get_my_info(self, user_id: str) -> InfoOut:
        user_info = get_user_by_id(user_id)
        user = UserOut(
            name=user_info.name,
            email=user_info.email,
            role=user_info.role,
            register_date=user_info.register_date)
        return InfoOut(user=user, tracks=self.get_my_tracks(user_id))
