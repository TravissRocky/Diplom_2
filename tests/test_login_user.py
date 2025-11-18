import pytest
import requests
import allure


@allure.feature("Логин пользователя")
class TestLoginUser:
    """Тесты для эндпоинта авторизации пользователя"""
    
    @allure.title("Логин под существующим пользователем")
    @allure.description("Проверка успешной авторизации существующего пользователя")
    def test_login_existing_user(self, base_url, create_user):
        """Тест логина под существующим пользователем"""
        user_data, _ = create_user
        
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data
        )
        
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is True, "Поле success должно быть True"
        assert "user" in response_data, "В ответе должно быть поле user"
        assert response_data["user"]["email"] == user_data["email"], "Email должен совпадать"
        assert response_data["user"]["name"] == user_data["name"], "Имя должно совпадать"
        assert "accessToken" in response_data, "В ответе должен быть accessToken"
        assert "refreshToken" in response_data, "В ответе должен быть refreshToken"
    
    @allure.title("Логин с неверным логином и паролем")
    @allure.description("Проверка ошибки при авторизации с неверными данными")
    def test_login_with_invalid_credentials(self, base_url):
        """Тест логина с неверным логином и паролем"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "WrongPassword123"
        }
        
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data
        )
        
        assert response.status_code == 401, f"Ожидался код 401, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is False, "Поле success должно быть False"
        assert "message" in response_data, "В ответе должно быть поле message"
        assert "incorrect" in response_data["message"].lower(), \
            "Сообщение должно содержать информацию о неверных данных"

