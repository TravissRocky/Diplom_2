import pytest
import requests
import allure


@allure.feature("Изменение данных пользователя")
class TestUpdateUser:
    """Тесты для эндпоинта обновления данных пользователя"""
    
    @allure.title("Изменение данных пользователя с авторизацией")
    @allure.description("Проверка успешного обновления данных авторизованного пользователя")
    @pytest.mark.parametrize("field_to_update,new_value", [
        ("name", "NewName"),
        ("email", None)  # Будет сгенерирован в тесте
    ])
    def test_update_user_with_auth(self, base_url, create_user, generate_unique_email, 
                                    field_to_update, new_value):
        """Тест изменения данных пользователя с авторизацией"""
        user_data, tokens = create_user
        
        # Получаем токен авторизации
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        assert login_response.status_code == 200, "Не удалось авторизоваться"
        access_token = login_response.json()["accessToken"]
        
        # Подготавливаем данные для обновления
        update_data = {}
        if field_to_update == "email":
            update_data["email"] = generate_unique_email()
        else:
            update_data[field_to_update] = new_value
        
        # Обновляем данные пользователя
        response = requests.patch(
            f"{base_url}/auth/user",
            json=update_data,
            headers={"Authorization": access_token}
        )
        
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is True, "Поле success должно быть True"
        assert "user" in response_data, "В ответе должно быть поле user"
        
        # Проверяем, что поле действительно обновилось
        if field_to_update == "email":
            assert response_data["user"]["email"] == update_data["email"], \
                "Email должен быть обновлён"
        else:
            assert response_data["user"][field_to_update] == new_value, \
                f"{field_to_update} должен быть обновлён"
    
    @allure.title("Изменение данных пользователя без авторизации")
    @allure.description("Проверка ошибки при попытке обновить данные без авторизации")
    def test_update_user_without_auth(self, base_url, generate_unique_name):
        """Тест изменения данных пользователя без авторизации"""
        update_data = {
            "name": generate_unique_name()
        }
        
        response = requests.patch(
            f"{base_url}/auth/user",
            json=update_data
        )
        
        assert response.status_code == 401, f"Ожидался код 401, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is False, "Поле success должно быть False"
        assert "message" in response_data, "В ответе должно быть поле message"
        assert "authorised" in response_data["message"].lower() or \
               "authorized" in response_data["message"].lower(), \
            "Сообщение должно содержать информацию о необходимости авторизации"
    
    @allure.title("Проверка изменения любого поля пользователя")
    @allure.description("Проверка, что можно изменить любое поле пользователя")
    def test_update_any_user_field(self, base_url, create_user, generate_unique_email, 
                                    generate_unique_name):
        """Тест проверки изменения любого поля пользователя"""
        user_data, tokens = create_user
        
        # Авторизуемся
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        assert login_response.status_code == 200, "Не удалось авторизоваться"
        access_token = login_response.json()["accessToken"]
        
        # Тестируем изменение имени
        new_name = generate_unique_name()
        response_name = requests.patch(
            f"{base_url}/auth/user",
            json={"name": new_name},
            headers={"Authorization": access_token}
        )
        
        assert response_name.status_code == 200, "Не удалось обновить имя"
        assert response_name.json()["user"]["name"] == new_name, "Имя должно быть обновлено"
        
        # Тестируем изменение email
        new_email = generate_unique_email()
        response_email = requests.patch(
            f"{base_url}/auth/user",
            json={"email": new_email},
            headers={"Authorization": access_token}
        )
        
        assert response_email.status_code == 200, "Не удалось обновить email"
        assert response_email.json()["user"]["email"] == new_email, "Email должен быть обновлён"

