import uuid
from datetime import datetime
from typing import List

from src.repository.db_connect import get_cursor
from src.repository.db_models import GpsTrack, User


def get_user_by_email(email) -> User | None:
    query = """ SELECT * FROM "user" WHERE email=%s"""
    with get_cursor() as cursor:
        cursor.execute(query, (email,))
        user_info = cursor.fetchone()
    if not user_info:
        return None
    user = User(
        id=user_info[0],
        name=user_info[1],
        email=user_info[2],
        password=user_info[3],
        role=user_info[4],
        register_date=user_info[5])
    return user


def get_user_by_id(user_id: str) -> User | None:
    query = """ SELECT * FROM "user" WHERE id=%s"""
    with get_cursor() as cursor:
        cursor.execute(query, (user_id,))
        user_info = cursor.fetchone()
    if not user_info:
        return None
    user = User(
        id=user_info[0],
        name=user_info[1],
        email=user_info[2],
        password=user_info[3],
        role=user_info[4],
        register_date=user_info[5])
    return user


def create_user(name, email, hashed_password) -> str:
    user_id = str(uuid.uuid4())
    query = """INSERT INTO "user" (id, name, email, password)
    VALUES (%s, %s, %s, %s);"""
    with get_cursor() as cursor:
        cursor.execute(query, (user_id, name, email, hashed_password))
        cursor.connection.commit()
    return user_id


def add_gps(user_id: str, latitude: str, longitude: str, timestamp: datetime) -> GpsTrack:
    gps_id = str(uuid.uuid4())
    query = """INSERT INTO gps_track (id, user_id, latitude, longitude, timestamp)
    VALUES (%s, %s, %s, %s, %s);"""
    with get_cursor() as cursor:
        cursor.execute(query, (gps_id, user_id, latitude, longitude, timestamp))
        cursor.connection.commit()
    return GpsTrack(
        id=gps_id,
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp
    )


def get_all_tracks_by_date(start_date: datetime, end_date: datetime) -> List[GpsTrack | None]:
    query = """SELECT * FROM gps_track
        WHERE  gps_track.timestamp >= %(start_date)s
                AND gps_track.timestamp <= %(end_date)s
                ORDER BY timestamp;"""
    with get_cursor() as cursor:
        cursor.execute(query, {"start_date": start_date,
                               "end_date": end_date})

        rows = cursor.fetchall()

    tracks = []
    for row in rows:
        tracks.append(GpsTrack(id=row[0], user_id=row[1], latitude=row[2], longitude=row[3], timestamp=row[4]))
    return tracks


def get_tracks_by_date_userid(start_date: datetime, end_date: datetime, user_id: str) -> List[GpsTrack | None]:
    query = """SELECT * FROM gps_track
            WHERE  gps_track.timestamp >= %(start_date)s
                    AND gps_track.timestamp <= %(end_date)s
                    AND gps_track.user_id = %(user_id)s
                    ORDER BY timestamp;"""
    with get_cursor() as cursor:
        cursor.execute(query, {"start_date": start_date,
                               "end_date": end_date,
                               "user_id": user_id})

        rows = cursor.fetchall()

    tracks = []
    for row in rows:
        tracks.append(GpsTrack(id=row[0], user_id=row[1], latitude=row[2], longitude=row[3], timestamp=row[4]))
    return tracks


def update_user_info(user_id: str, name: str, email: str, hashed_password: str,) -> User:
    query = """UPDATE "user" 
    SET name = %s, email = %s, password = %s
    WHERE id = %s;"""
    with get_cursor() as cursor:
        cursor.execute(query, (name, email, hashed_password, user_id))
        cursor.connection.commit()
    return User(id=user_id,
                name=name,
                email=email,
                password=hashed_password)


def user_change_role(user_id: str, role: str) -> User:
    query = """UPDATE "user" 
    SET role = %s
    WHERE id=%s;"""
    with get_cursor() as cursor:
        cursor.execute(query, (role, user_id))
        cursor.connection.commit()
    user = get_user_by_id(user_id)
    return User(id=user_id,
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                register_date=user.register_date)


def delete_user(user_id: str) -> str:
    query = """DELETE FROM "user"
    WHERE id=%s;"""
    with get_cursor() as cursor:
        cursor.execute(query, (user_id,))
        cursor.connection.commit()

    return user_id


def get_all_users() -> List[User]:
    query = """ SELECT * FROM public.user"""
    with get_cursor() as cursor:
        cursor.execute(query)
        users_info = cursor.fetchall()

    users = []
    for user in users_info:
        users.append(User(
            id=user[0],
            name=user[1],
            email=user[2],
            password=user[3],
            role=user[4],
            register_date=user[5]))
    return users


def get_tracks_by_id(user_id: str) -> List[GpsTrack | None]:
    query = """SELECT * FROM gps_track
                WHERE user_id = %(user_id)s
                ORDER BY timestamp;"""
    with get_cursor() as cursor:
        cursor.execute(query, {"user_id": user_id})

        rows = cursor.fetchall()

    tracks = []
    for row in rows:
        tracks.append(GpsTrack(id=row[0], user_id=row[1], latitude=row[2], longitude=row[3], timestamp=row[4]))
    return tracks
