import pytest
import requests
import uuid


BASE_URL = "https://stellarburgers.education-services.ru/api"


@pytest.fixture
def base_url():
    """Базовый URL API"""
    return BASE_URL


@pytest.fixture
def generate_unique_email():
    """Генерация уникального email для тестов"""
    def _generate():
        return f"test_{uuid.uuid4().hex[:8]}@test.com"
    return _generate


@pytest.fixture
def generate_unique_name():
    """Генерация уникального имени для тестов"""
    def _generate():
        return f"TestUser_{uuid.uuid4().hex[:8]}"
    return _generate


@pytest.fixture
def test_user_data(generate_unique_email, generate_unique_name):
    """Тестовые данные пользователя"""
    return {
        "email": generate_unique_email(),
        "password": "TestPassword123",
        "name": generate_unique_name()
    }


@pytest.fixture
def create_user(base_url, test_user_data):
    """Создание пользователя для тестов и удаление после"""
    # Создаём пользователя
    response = requests.post(
        f"{base_url}/auth/register",
        json=test_user_data
    )
    
    user_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
        "name": test_user_data["name"]
    }
    
    # Если пользователь успешно создан, сохраняем токены для удаления
    tokens = None
    if response.status_code == 200 and response.json().get("success"):
        tokens = {
            "accessToken": response.json().get("accessToken", "").replace("Bearer ", ""),
            "refreshToken": response.json().get("refreshToken", "")
        }
    
    yield user_data, tokens
    
    # Удаление пользователя после теста (если был создан)
    if tokens and tokens.get("refreshToken"):
        try:
            requests.post(
                f"{base_url}/auth/logout",
                json={"token": tokens["refreshToken"]}
            )
        except:
            pass


@pytest.fixture
def get_ingredients(base_url):
    """Получение списка ингредиентов для тестов"""
    response = requests.get(f"{base_url}/ingredients")
    if response.status_code == 200:
        response_data = response.json()
        # API может вернуть данные в разных форматах
        ingredients = response_data.get("data", [])
        if not ingredients and isinstance(response_data, list):
            ingredients = response_data
        if ingredients:
            return [ingredient["_id"] for ingredient in ingredients[:2]]
    return []


@pytest.fixture
def cleanup_users(base_url):
    """Удаление созданных в тестах пользователей"""
    tokens = []
    yield tokens
    for token in tokens:
        if token:
            try:
                requests.post(
                    f"{base_url}/auth/logout",
                    json={"token": token}
                )
            except:
                pass

