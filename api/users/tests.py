import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

TEST_PASSWORD = 'test_pass'


@pytest.fixture
def user_with_password(user: 'User'):
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.mark.django_db
def test_auth_using_login_pass(anon_client: 'APIClient', user_with_password: 'User'):
    username = user_with_password.username
    response = anon_client.post(
        '/api/auth/login/',
        data={'username': username, 'password': 'incorrect_password'},
    )
    assert response.status_code == 403

    response = anon_client.post(
        '/api/auth/login/', data={'username': username, 'password': TEST_PASSWORD}
    )
    assert response.status_code == 200, response.content

    data = response.json()

    assert data['username'] == username


@pytest.mark.django_db
def test_user_flow(admin_client: 'APIClient', anon_client: 'APIClient'):
    """
    TODO Дополните тест.
     Требуется подготовить данные для создания нескольких рандомных пользователей используя клиент для admin
     (не забудьте вначале починить фикстуру admin) и выполнить следующие действия:
     1. Создать пользователя отправив POST-запрос на url '/api/v1/users/'
        response.status_code == 200
     2. Проверить количество созданных пользователей отправив GET-запрос на url '/api/v1/users/'
        response.status_code == 200
     3. Проверить авторизацию для каждого нового пользователя. Необходимо используя анонимный клиент
        отправить POST-запрос на url f'/api/v1/users/{created_users_id}/' response.status_code == 200
        (НАВЕРНО ИМЕЛОСЬ ВВИДУ НА /api/auth/login/)
     4. Удалить всех созданных пользователей, отправив DELETE-запрос на url f'/api/v1/users/{created_users_id}/',
        response.status_code == 204

    Пример создания данных для рандомных пользователей.

    users_count = 20
    users_data = [
        {
            'username': f'user_{i}',
            'password': f'password_{i}',
            'email': f'email_{i}@mail.ru',
        }
        for i in range(users_count)
    ]

    """

    users_count = 20
    users_data = [
        {
            'username': f'user_{i}',
            'password': f'password_{i}',
            'email': f'email_{i}@mail.ru',
        }
        for i in range(users_count)
    ]

    # Создание новых пользователей
    created_users_ids = []
    for user in users_data:
        response = admin_client.post('/api/v1/users/', data=user)
        assert response.status_code == 201, response.content

        data = response.json()
        assert data['username'] == user['username']

        created_users_ids.append(data['id'])

    # Проверка количества созданных пользователей
    response = admin_client.get('/api/v1/users/')
    assert response.status_code == 200, response.content
    data = response.json()
    assert data['count'] == users_count

    # Авторизация
    for i in range(users_count):
        response = anon_client.post(
            '/api/auth/login/',
            data={'username': f'user_{i}', 'password': f'password_{i}'}
        )
        assert response.status_code == 200

    # Удаление пользователей
    for created_user_id in created_users_ids:
        response = admin_client.delete(f'/api/v1/users/{created_user_id}/')
        assert response.status_code == 204
