import pytest
import requests
import allure


@allure.feature("Создание пользователя")
class TestCreateUser:
    """Тесты для эндпоинта создания пользователя"""
    
    @allure.title("Создание уникального пользователя")
    @allure.description("Проверка успешного создания нового пользователя")
    def test_create_unique_user(self, base_url, generate_unique_email, generate_unique_name, cleanup_users):
        """Тест создания уникального пользователя"""
        user_data = {
            "email": generate_unique_email(),
            "password": "TestPassword123",
            "name": generate_unique_name()
        }
        
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data
        )
        
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is True, "Поле success должно быть True"
        assert "user" in response_data, "В ответе должно быть поле user"
        assert response_data["user"]["email"] == user_data["email"], "Email должен совпадать"
        assert response_data["user"]["name"] == user_data["name"], "Имя должно совпадать"
        assert "accessToken" in response_data, "В ответе должен быть accessToken"
        assert "refreshToken" in response_data, "В ответе должен быть refreshToken"
        
        refresh_token = response_data.get("refreshToken")
        if refresh_token:
            cleanup_users.append(refresh_token)
    
    @allure.title("Создание пользователя, который уже зарегистрирован")
    @allure.description("Проверка ошибки при попытке создать уже существующего пользователя")
    def test_create_existing_user(self, base_url, create_user):
        """Тест создания пользователя, который уже зарегистрирован"""
        user_data, _ = create_user
        
        # Попытка создать пользователя с теми же данными
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data
        )
        
        assert response.status_code == 403, f"Ожидался код 403, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is False, "Поле success должно быть False"
        assert "message" in response_data, "В ответе должно быть поле message"
        assert "already exists" in response_data["message"].lower(), \
            "Сообщение должно содержать информацию о существующем пользователе"
    
    @allure.title("Создание пользователя без обязательного поля")
    @allure.description("Проверка ошибки при создании пользователя без одного из обязательных полей")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_missing_field(self, base_url, generate_unique_email, 
                                       generate_unique_name, missing_field):
        """Тест создания пользователя без одного из обязательных полей"""
        user_data = {
            "email": generate_unique_email(),
            "password": "TestPassword123",
            "name": generate_unique_name()
        }
        
        # Удаляем одно из полей
        user_data.pop(missing_field)
        
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data
        )
        
        assert response.status_code == 403, f"Ожидался код 403, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is False, "Поле success должно быть False"
        assert "message" in response_data, "В ответе должно быть поле message"
        assert "required" in response_data["message"].lower(), \
            "Сообщение должно содержать информацию об обязательных полях"

