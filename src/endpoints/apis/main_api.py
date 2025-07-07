from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Security,
    status,
)

from src.Exceptions import (
    UserFindException,
    UserLoginException,
    UserPasswordException,
    UserRegisterException,
)
from src.endpoints.security_api import get_token_bearerAuth

from ..models.allTracksResponse import AllTracksResponse
from ..models.error import Error
from ..models.infoResponse import InfoResponse
from ..models.loginRequest import LoginRequest
from ..models.loginResponse import LoginResponse
from ..models.registerRequest import RegisterRequest
from ..models.registerResponse import RegisterResponse
from ..models.trackFilteredResponse import TrackFilteredResponse
from ..models.trackRequest import TrackRequest
from ..models.trackResponse import TrackResponse
from ..models.userResponse import UserResponse
from ..models.usersResponse import UsersResponse

from ...service.main_service import MainService
from ...service.models.loginIn import LoginIn
from ...service.models.registerIn import RegisterIn
from ...service.models.role import Role
from ...service.service_models import TokenModel
from ...service.user_service import UserService

router = APIRouter()
mainService = MainService()
userService = UserService()


def require_admin(token: TokenModel = Security(get_token_bearerAuth)) -> TokenModel:
    if token.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    return token


def raise_bad_request(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=Error(message=message).model_dump()
    )


def raise_unauthorized(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=Error(message=message).model_dump(),
    )


def raise_not_found(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=Error(message=message).model_dump(),
    )


@router.post(
    "/login",
    responses={
        200: {"model": str, "description": "Успешная авторизация"},
        401: {"model": Error, "description": "Неверные учетные данные"},
    },
    tags=["default"],
    summary="Авторизация пользователя",
    response_model_by_alias=True,
)
async def login_post(
        login_request: LoginRequest = Body(None, description="Данные для входа"),
) -> LoginResponse:
    try:
        token = mainService.login(
            LoginIn(
                **login_request.model_dump(),
            )
        )
        return LoginResponse(token=token)
    except UserLoginException:
        raise_unauthorized("Неверный email")
    except UserPasswordException:
        raise_unauthorized("Неверный пароль")


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": UsersResponse, "description": "Пользователь создан"},
        400: {"model": Error, "description": "Неверный запрос"},
    },
    tags=["default"],
    summary="Регистрация пользователя",
    response_model_by_alias=True,
)
async def register_post(
        register_request: RegisterRequest = Body(None, description="Форма регистрации"),
) -> RegisterResponse:
    try:
        register_response = mainService.register(
            RegisterIn(
                **register_request.model_dump()
            )
        )
        return RegisterResponse(
            **register_response.model_dump()
        )
    except UserRegisterException:
        raise_bad_request("Пользователь с таким email уже существует")


@router.post(
    "/gps",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": TrackResponse, "description": "Координаты добавлены"},
        400: {"model": Error, "description": "Неверный запрос"},
        404: {"model": Error, "description": "Пользователь не найден"},
    },
    tags=["default"],
    summary="Добавление GPS трека",
    response_model_by_alias=True,
)
async def gps_post(
        track_request: TrackRequest = Body(None, description="Данные трека")
) -> TrackResponse:
    if not mainService.user_exists(track_request.user_id):
        raise_not_found(f"Пользователь с id: {track_request.user_id} не найден")
    try:
        latitude_str, longitude_str = track_request.latitude, track_request.longitude
        latitude = float(latitude_str.strip())
        longitude = float(longitude_str.strip())
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise_bad_request(f"Координаты вне диапазона: {latitude}, {longitude}")
    except ValueError:
        raise_bad_request(f"Некорректный формат координат: {track_request.latitude, track_request.longitude}")

    try:
        gps_track = mainService.add_gps(
            track_request.user_id,
            track_request.latitude,
            track_request.longitude,
            track_request.timestamp)

        return TrackResponse(
            **gps_track.model_dump()
        )
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.get(
    "/tracks",
    responses={
        200: {"model": TrackFilteredResponse, "description": "Список GPS треков"},
        403: {"model": Error, "description": "Доступ запрещен"},
        404: {"model": Error, "description": "Треки в этом диапазоне не найдены"},
    },
    tags=["default"],
    summary="Получение списка GPS треков по дате",
    response_model_by_alias=True,
)
async def get_filtered_tracks(
        start_date: Optional[datetime] = Query(None, alias="startDate", description="Начальная дата диапазона"),
        end_date: Optional[datetime] = Query(None, alias="endDate", description="Конечная дата диапазона"),
        token: TokenModel = Security(get_token_bearerAuth),
) -> TrackFilteredResponse:
    try:
        tracks = mainService.get_tracks_by_date(start_date, end_date, token)
        if not tracks:
            raise_not_found(f"Треки в этом диапазоне c {start_date} по {end_date} не найдены")
        filtered_tracks = [
            TrackResponse(
                **track.model_dump()
            )
            for track in tracks
        ]
        return TrackFilteredResponse(tracks=filtered_tracks)
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": UsersResponse, "description": "Пользователь создан"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Добавление нового пользователя администратором",
    response_model_by_alias=True,
)
async def user_post(
        register_request: RegisterRequest = Body(None, description="Форма регистрации"),
        token: TokenModel = Depends(require_admin),
) -> RegisterResponse:
    try:
        user = mainService.register(
            RegisterIn(
                **register_request.model_dump()
            )
        )
        return RegisterResponse(
            **user.model_dump()
        )
    except UserRegisterException:
        raise_bad_request("Пользователь с таким email уже существует")


@router.put(
    "/user",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserResponse, "description": "Данные пользователя обновлены"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Обновление данных пользователя, если вы админ, "
            "введите id пользователя, которого хотите изменить",
    response_model_by_alias=True,
)
async def user_update(
        user_id: str = Body(None, description="ID пользователя"),
        register_request: RegisterRequest = Body(None, description="Форма регистрации"),
        token: TokenModel = Security(get_token_bearerAuth),
) -> UserResponse:
    if not user_id:
        if token.role != Role.ADMIN.value:
            user_id = token.user_id
        else:
            raise_bad_request("Неверный запрос. Введите user_id")
    try:
        user = userService.update_user_info(
            user_id,
            RegisterIn(
                **register_request.model_dump()
            )
        )
        return UserResponse(
            **user.model_dump()
        )
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.patch(
    "/user/{user_id}/",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UserResponse, "description": "Роль пользователя изменена"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Обновление роли пользователя",
    response_model_by_alias=True,
)
async def user_change_role(
        user_id: str = Path(..., description="ID пользователя"),
        role: str = Body(..., description="Новая роль пользователя"),
        token: TokenModel = Depends(require_admin),
) -> UserResponse:
    try:
        role = Role(role)
        user = userService.user_change_role(user_id, role)
        return UserResponse(
            **user.model_dump()
        )
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.delete(
    "/user/{user_id}/",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": str, "description": "Пользователь удален"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Удаление учетной записи пользователя",
    response_model_by_alias=True,
)
async def user_delete(
        user_id: str = Path(..., description="ID пользователя"),
        token: TokenModel = Depends(require_admin),
) -> str:
    try:
        return await userService.delete_user(user_id)
    except UserFindException:
        raise_bad_request(f"Пользователя с таким id не существует {user_id}")


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": UsersResponse, "description": "Список пользователей получен"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Получение списка пользователей",
    response_model_by_alias=True,
)
async def user_get(
        token: TokenModel = Depends(require_admin),
) -> UsersResponse:
    try:
        users = userService.get_users()
        if not users:
            raise_not_found("Пользователи не найдены")
        user_response = [
            UserResponse(
                **u.model_dump()
            )
            for u in users
        ]

        return UsersResponse(users=user_response)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": InfoResponse, "description": "Информация получена"},
        400: {"model": Error, "description": "Неверный запрос"},
    },
    tags=["default"],
    summary="Получение информации о профиле и треках пользователя",
    response_model_by_alias=True,
)
async def info_get(
        token: TokenModel = Security(get_token_bearerAuth),
) -> InfoResponse:
    try:
        user_id = token.user_id
        info = userService.get_my_info(user_id)
        user = UserResponse(
            **info.user.model_dump()
        )
        tracks = [
            TrackResponse(
                **track.model_dump()
            )
            for track in info.tracks
        ]

        filtered_track = TrackFilteredResponse(tracks=tracks)
        return InfoResponse(user=user, tracks=filtered_track)
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")


@router.get(
    "/track",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": AllTracksResponse, "description": "Информация получена"},
        400: {"model": Error, "description": "Неверный запрос"},
        403: {"model": Error, "description": "Доступ запрещен"},
    },
    tags=["default"],
    summary="Получение информации о треках пользователя",
    response_model_by_alias=True,
)
async def get_all_user_tracks(
        token: TokenModel = Security(get_token_bearerAuth),
) -> AllTracksResponse:
    try:
        if token.role == Role.ADMIN.value:
            tracks = userService.get_all_tracks()
        else:
            user_id = token.user_id
            tracks = userService.get_my_tracks(user_id)
        track_response = [
            TrackResponse(
                **track.model_dump()
            )
            for track in tracks
        ]
        return AllTracksResponse(tracks=track_response)
    except Exception as e:
        raise_bad_request(f"Неверный запрос. {e}")
