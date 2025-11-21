import pytest
import requests
import allure


@allure.feature("Получение заказов пользователя")
class TestGetUserOrders:
    """Тесты для эндпоинта получения заказов конкретного пользователя"""
    
    @allure.title("Получение заказов авторизованного пользователя")
    @allure.description("Проверка успешного получения заказов авторизованного пользователя")
    def test_get_orders_authorized_user(self, base_url, create_user, get_ingredients):
        """Тест получения заказов авторизованного пользователя"""
        user_data, tokens = create_user
        ingredients = get_ingredients
        
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
        
        # Создаём заказ для теста (опционально)
        if ingredients:
            order_data = {
                "ingredients": ingredients
            }
            requests.post(
                f"{base_url}/orders",
                json=order_data,
                headers={"Authorization": access_token}
            )
        
        # Получаем заказы пользователя
        response = requests.get(
            f"{base_url}/orders",
            headers={"Authorization": access_token}
        )
        
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is True, "Поле success должно быть True"
        assert "orders" in response_data, "В ответе должно быть поле orders"
        assert isinstance(response_data["orders"], list), "Поле orders должно быть списком"
        assert "total" in response_data, "В ответе должно быть поле total"
        assert "totalToday" in response_data, "В ответе должно быть поле totalToday"
    
    @allure.title("Получение заказов неавторизованного пользователя")
    @allure.description("Проверка ошибки при попытке получить заказы без авторизации")
    def test_get_orders_unauthorized_user(self, base_url):
        """Тест получения заказов неавторизованного пользователя"""
        response = requests.get(f"{base_url}/orders")
        
        assert response.status_code == 401, f"Ожидался код 401, получен {response.status_code}"
        response_data = response.json()
        assert response_data["success"] is False, "Поле success должно быть False"
        assert "message" in response_data, "В ответе должно быть поле message"
        assert "authorised" in response_data["message"].lower() or \
               "authorized" in response_data["message"].lower(), \
            "Сообщение должно содержать информацию о необходимости авторизации"

