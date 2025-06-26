from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Query,
    Security,
    status,
    Path,
)

from src.Exceptions import UserLoginException, UserPasswordException, UserRegisterException, UserFindException
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
from ...service.service_models import TokenModel
from ...service.user_service import UserService
from ...service.models.role import Role

router = APIRouter()
mainService = MainService()
userService = UserService()


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
        login_request: LoginRequest = Body(None, description=""),
) -> LoginResponse:
    try:
        token = mainService.login(
            LoginIn(email=login_request.email,
                    password=login_request.password))
        return LoginResponse(token=token)
    except UserLoginException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Error(message="Неверные учетные данные").model_dump(),
        )
    except UserPasswordException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Error(message="Неверный пароль").model_dump(),
        )


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
        register_request: RegisterRequest = Body(None, description=""),
) -> RegisterResponse:
    try:
        register_response = mainService.register(
            RegisterIn(
                name=register_request.name,
                email=register_request.email,
                password=register_request.password,
            ))
        return RegisterResponse(
            id=register_response.id,
            name=register_response.name,
            email=register_response.email,
            role=register_response.role,
            register_date=register_response.register_date)
    except UserRegisterException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message="Пользователь с таким email уже существует").model_dump()
        )


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
        track_request: TrackRequest = Body(None, description="")
) -> TrackResponse:
    try:
        lat_str, lon_str = track_request.latitude, track_request.longitude
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Error(message=f"Координаты вне диапазона: {lat}, {lon}").model_dump()
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(
                message=f"Некорректный формат координат: {track_request.latitude, track_request.longitude}. Причина: {e}").model_dump())

    try:
        gps_track = mainService.add_gps(
            track_request.user_id,
            track_request.latitude,
            track_request.longitude,
            datetime.strptime(track_request.timestamp, "%Y-%m-%d %H:%M:%S.%f"))
        return TrackResponse(
            id=gps_track.id,
            user_id=gps_track.user_id,
            latitude=gps_track.latitude,
            longitude=gps_track.longitude,
            timestamp=gps_track.timestamp)
    except UserFindException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Error(message=f"Пользователь с id: {track_request.user_id} не найден").model_dump()
        )


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
async def track_get(
        start_date: Optional[datetime] = Query(None, alias="startDate", description="Начальная дата диапазона"),
        end_date: Optional[datetime] = Query(None, alias="endDate", description="Конечная дата диапазона"),
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> TrackFilteredResponse:
    try:
        tracks = mainService.get_tracks_by_date(start_date, end_date, token_bearerAuth)
        if not tracks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Error(message=f"Треки в этом диапазоне c {start_date} по {end_date} не найдены").model_dump()
            )
        filtered_tracks = []
        for track in tracks:
            filtered_tracks.append(TrackResponse(
                id=track.id,
                user_id=track.user_id,
                latitude=track.latitude,
                longitude=track.longitude,
                timestamp=track.timestamp
            ))
        return TrackFilteredResponse(tracks=filtered_tracks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Error(message=f"{e}").model_dump()
            )


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
        register_request: RegisterRequest = Body(None, description=""),
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> RegisterResponse:
    if token_bearerAuth.role != 'Administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    try:
        user = mainService.register(
            RegisterIn(
                name=register_request.name,
                email=register_request.email,
                password=register_request.password))
        return RegisterResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            register_date=user.register_date)
    except UserRegisterException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message="Пользователь с таким email уже существует").model_dump()
        )


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
        user_id: str = Body(None, description=""),
        register_request: RegisterRequest = Body(None, description=""),
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> UserResponse:
    if token_bearerAuth.role != 'Administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    if not user_id:
        user_id = token_bearerAuth.user_id
    try:
        user = userService.update_user_info(
            user_id,
            RegisterIn(
                name=register_request.name,
                email=register_request.email,
                password=register_request.password))
        return UserResponse(
            name=user.name,
            email=user.email,
            role=user.role,
            register_date=user.register_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Неверный запрос. {e}").model_dump()
        )


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
        user_id: str = Path(..., description=""),
        role: str = Body(None, description=""),
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> UserResponse:
    if token_bearerAuth.role != 'Administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    try:
        role = Role(role)
        user = userService.user_change_role(user_id, role)
        return UserResponse(name=user.name,
                            email=user.email,
                            role=role,
                            register_date=user.register_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Неверный запрос. {e}").model_dump()
        )


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
        user_id: str = Path(..., description=""),
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> str:
    if token_bearerAuth.role != 'Administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    try:
        return await userService.delete_user(user_id)
    except UserFindException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Пользователя с таким id не существует").model_dump()
        )


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
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> UsersResponse:
    if token_bearerAuth.role != 'Administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Error(message="Доступ запрещен").model_dump()
        )
    try:
        users = userService.get_users()
        user_response = []
        for user in users:
            user_response.append(
                UserResponse(
                    name=user.name,
                    email=user.email,
                    role=user.role,
                    register_date=user.register_date
                )
            )
        return UsersResponse(users=user_response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Неверный запрос. {e}").model_dump()
        )


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
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> InfoResponse:
    try:
        user_id = token_bearerAuth.user_id
        info = userService.get_my_info(user_id)
        user = UserResponse(
            name=info.user.name,
            email=info.user.email,
            role=info.user.role,
            register_date=info.user.register_date)
        tracks = []
        for track in info.tracks:
            tracks.append(
                TrackResponse(
                    id=track.id,
                    user_id=track.user_id,
                    latitude=track.latitude,
                    longitude=track.longitude,
                    timestamp=track.timestamp))
        filtered_track = TrackFilteredResponse(tracks=tracks)
        return InfoResponse(user=user, tracks=filtered_track)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Неверный запрос. {e}").model_dump()
        )


#TODO: ????добавить возможность просматривать ВСЕ треки с аккаунта администратора????
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
async def track_get(
        token_bearerAuth: TokenModel = Security(get_token_bearerAuth),
) -> AllTracksResponse:
    try:
        user_id = token_bearerAuth.user_id
        tracks = userService.get_my_tracks(user_id)
        track_response = []
        for track in tracks:
            track_response.append(
                TrackResponse(
                    id=track.id,
                    user_id=track.user_id,
                    latitude=track.latitude,
                    longitude=track.longitude,
                    timestamp=track.timestamp))
        return AllTracksResponse(tracks=track_response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Error(message=f"Неверный запрос. {e}").model_dump()
        )
