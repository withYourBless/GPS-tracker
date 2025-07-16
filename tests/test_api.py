import os
import datetime

import requests

from tests.conftest import test_logger
from pydantic import BaseModel


class TokenModel(BaseModel):
    user_id: str
    email: str
    role: str


BASE_URL = os.getenv("BASE_URL")
user_first = {"token": "", "id": "", "name": "", "email": "", "role": "", "register_date": ""}
user_second = {"token": "", "id": "", "name": "", "email": "", "role": "", "register_date": ""}
admin = {"token": "", "id": "", "name": "", "email": "", "role": "", "register_date": ""}


def create_admin():
    import uuid
    from src.endpoints.security_api import get_password_hash
    from src.repository.db_connect import get_cursor

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash("testpassword")
    query = """INSERT INTO "user" (id, name, email, password, role)
        VALUES (%s, %s, %s, %s, %s);"""
    with get_cursor() as cursor:
        cursor.execute(query, (user_id, "admin", "admin@example.com", hashed_password, "Administrator"))
        cursor.connection.commit()
    admin["id"] = user_id
    admin["name"] = "admin"
    admin["email"] = "admin@example.com"
    admin["password"] = hashed_password
    admin["role"] = "Administrator"


def login_admin():
    payload = {
        "email": admin["email"],
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)

    data = response.json()
    test_logger.info(data)
    admin["token"] = data["token"]


def all_user_delete():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.delete(
        f"{BASE_URL}/user/{user_first['id']}",
        headers=headers
    )


def test_register_post_successful_user():
    create_admin()
    payload = {
        "name": "test",
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/register", json=payload)
    data = response.json()
    test_logger.info(data)

    user_first["id"] = data["id"]
    user_first["name"] = data["name"]
    user_first["email"] = data["email"]
    user_first["role"] = data["role"]
    user_first["register_date"] = data["register_date"]

    assert response.status_code == 201
    assert "id" in data
    assert data["name"] == "test"
    assert data["email"] == "test@example.com"
    assert data["role"] == "User"
    assert "register_date" in data


def test_register_post_user_exist_email():
    payload = {
        "name": "test",
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/register", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == "Пользователь с таким email уже существует"


def test_login_success():
    login_admin()
    payload = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)

    data = response.json()
    test_logger.info(data)
    user_first["token"] = data["token"]

    assert response.status_code == 200
    assert "token" in data.keys()


def test_login_invalid_email():
    payload = {
        "email": "wrong@example.com",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 401
    assert data["detail"]["message"] == "Неверный email"


def test_login_invalid_password():
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 401
    assert data["detail"]["message"] == "Неверный пароль"


def test_gps_post_successful():
    payload = {
        "user_id": user_first["id"],
        "latitude": "59.939749",
        "longitude": "30.314182",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    }

    response = requests.post(f"{BASE_URL}/gps", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 201
    assert "id" in data.keys()


def test_gps_post_not_found_user_id():
    payload = {
        "user_id": "1",
        "latitude": "59.939749",
        "longitude": "30.314182",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    }

    response = requests.post(f"{BASE_URL}/gps", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 404
    assert data["detail"]["message"] == "Пользователь с id: 1 не найден"


def test_gps_post_coordinates_not_in_range():
    payload = {
        "user_id": user_first["id"],
        "latitude": "91.939749",
        "longitude": "30.314182",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    }

    response = requests.post(f"{BASE_URL}/gps", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == f"Координаты вне диапазона: 91.939749, 30.314182"


def test_gps_post_invalid_coordinates():
    payload = {
        "user_id": user_first["id"],
        "latitude": "lat.939749",
        "longitude": "30.314182",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    }

    response = requests.post(f"{BASE_URL}/gps", json=payload)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == f"Некорректный формат координат: ('lat.939749', '30.314182')"


def test_gps_post_invalid_timestamp():
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "user_id": user_first["id"],
        "latitude": "87.939749",
        "longitude": "30.314182",
        "timestamp": time,
    }

    response = requests.post(f"{BASE_URL}/gps", json=payload)

    data = response.json()
    test_logger.info(data)

    output = f"Некорректный формат времени: {time}. Необходимо формат YYYY-MM-DD HH:MM:SS.ffff"

    assert response.status_code == 400
    assert data["detail"]["message"] == output


def test_track_get_successful():
    one_day = datetime.timedelta(days=1)
    start_date = datetime.datetime.now() - one_day
    end_date = datetime.datetime.now() + one_day

    user_headers = {
        "Authorization": f"Bearer {user_first['token']}"
    }
    params = {
        "startDate": start_date,
        "endDate": end_date
    }

    response = requests.get(f"{BASE_URL}/tracks", headers=user_headers, params=params)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200


def test_track_get_not_found_in_range():
    one_day = datetime.timedelta(days=1)
    start_date = datetime.datetime.now() - one_day - one_day
    end_date = datetime.datetime.now()

    user_headers = {
        "Authorization": f"Bearer {user_first['token']}"
    }
    params = {
        "startDate": start_date,
        "endDate": end_date
    }

    response = requests.get(f"{BASE_URL}/tracks", params=params, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200


def test_user_post_successful():
    payload = {
        "name": "Test",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    admin_headers = {
        "Authorization": f"Bearer {admin['token']}"
    }

    response = requests.post(f"{BASE_URL}/user", json=payload, headers=admin_headers)

    data = response.json()
    test_logger.info(data)

    user_second["id"] = data["id"]
    user_second["name"] = data["name"]
    user_second["email"] = data["email"]
    user_second["role"] = data["role"]
    user_second["register_date"] = data["register_date"]

    assert response.status_code == 201
    assert "id" in data
    assert data["name"] == "Test"
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "User"
    assert "register_date" in data


def test_user_post_access_is_denied():
    payload = {
        "name": "Test",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    user_headers = {
        "Authorization": f"Bearer {user_first['token']}"
    }

    response = requests.post(f"{BASE_URL}/user", json=payload, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 403
    assert data["detail"]["message"] == "Доступ запрещен"


def test_user_post_user_exist_email():
    payload = {
        "name": "test",
        "email": "test@example.com",
        "password": "testpassword"
    }
    user_headers = {
        "Authorization": f"Bearer {admin['token']}"
    }

    response = requests.post(f"{BASE_URL}/user", json=payload, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == "Пользователь с таким email уже существует"


def test_user_update_as_admin_successful():
    payload = {
        "user_id": user_first["id"],
        "register_request": {
            "name": "testnew",
            "email": "test@example.com",
            "password": "testpassword"
        }
    }
    user_headers = {
        "Authorization": f"Bearer {admin['token']}"
    }

    response = requests.put(f"{BASE_URL}/user", json=payload, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200
    assert data["name"] == "testnew"


def test_user_update_as_user_successful():
    payload = {
        "user_id": "",
        "register_request": {
            "name": "testnew2",
            "email": "test@example.com",
            "password": "testpassword"
        }
    }
    user_headers = {
        "Authorization": f"Bearer {user_first['token']}"
    }

    response = requests.put(f"{BASE_URL}/user", json=payload, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200
    assert data["name"] == "testnew2"


def test_user_update_as_admin_bad_request():
    payload = {
        "user_id": "",
        "register_request": {
            "name": "testnew",
            "email": "test@example.com",
            "password": "testpassword"
        }
    }
    user_headers = {
        "Authorization": f"Bearer {admin['token']}"
    }

    response = requests.put(f"{BASE_URL}/user", json=payload, headers=user_headers)

    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == "Неверный запрос. Введите user_id"


def test_user_change_role_successful():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    role = "Administrator"
    response = requests.patch(
        f"{BASE_URL}/user/{user_first['id']}/",
        json=role,
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200
    assert data["role"] == "Administrator"
    assert "email" in data
    assert "name" in data


def test_user_change_role_access_is_denied():
    headers = {
        "Authorization": f"Bearer {user_second['token']}",
    }
    role = "User"
    response = requests.patch(
        f"{BASE_URL}/user/{admin['id']}/",
        json=role,
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 403


def test_user_get_successful():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.get(
        f"{BASE_URL}/users",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200
    assert "users" in data


def test_user_get_access_is_denied():
    headers = {
        "Authorization": f"Bearer {user_first['token']}",
    }
    response = requests.get(
        f"{BASE_URL}/users",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 403
    assert data["detail"]["message"] == "Доступ запрещен"


def test_info_get_successful():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.get(
        f"{BASE_URL}/info",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200


def test_track_get_successful():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.get(
        f"{BASE_URL}/track",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200


def test_user_delete_access_is_denied():
    headers = {
        "Authorization": f"Bearer {user_first['token']}",
    }
    response = requests.delete(
        f"{BASE_URL}/user/{user_second['id']}/",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 403
    assert data["detail"]["message"] == "Доступ запрещен"


def test_user_delete_successful():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.delete(
        f"{BASE_URL}/user/{user_second['id']}",
        headers=headers
    )

    test_logger.info(user_second)
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 200
    assert data == user_second["id"]


def test_user_delete_user_doesnot_exist():
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.delete(
        f"{BASE_URL}/user/{user_second['id']}/",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 400
    assert data["detail"]["message"] == f"Пользователя с таким id не существует {user_second['id']}"


def test_user_get_not_found_users():
    all_user_delete()
    headers = {
        "Authorization": f"Bearer {admin['token']}",
    }
    response = requests.get(
        f"{BASE_URL}/users",
        headers=headers
    )
    data = response.json()
    test_logger.info(data)

    assert response.status_code == 404
    assert data["detail"]["message"] == "Пользователи не найдены"
