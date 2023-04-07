import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_reg_user(client, dbsession, user_data):
    # Регистрация юзера
    response = await client.post(
        '/user/signup',
        json=user_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['username'] == user_data['username']

    # Регистрация юзера c тем же username - отказ
    response = await client.post(
        '/user/signup',
        json=user_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_auth_user(client, dbsession, user_data):
    user = user_data
    response = await client.post('/user/signup', json=user)
    # Авторизация пользователя
    response = await client.post('/user/login', data=user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data.keys()
    assert 'token_type' in data.keys()
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_auth_user_add_url(client, dbsession, user_data, urls_data):
    user = user_data
    response = await client.post('/user/signup', json=user)
    response = await client.post('/user/login', data=user)
    data = response.json()
    token = data['access_token']
    # Авторизованный пользователь добавляет url
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'short' in data.keys()
    assert 'is_deleted' in data.keys()
    assert data['original'] == urls_data[0]['original']
    assert data['description'] == urls_data[0]['description']
    assert data['is_private'] == urls_data[0]['is_private']
    assert data['is_deleted'] == False
    # Добавляем тот же url - Отказ
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_notauth_user_add_url(client, dbsession, urls_data):
    # Неавторизованный пользователь добавляет url
    url_1 = urls_data[1]
    url_1['is_private'] = True
    response = await client.post(
        '/',
        json=url_1,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'short' in data.keys()
    assert 'is_deleted' in data.keys()
    assert data['original'] == url_1['original']
    assert data['description'] == url_1['description']
    assert data['is_deleted'] == False
    assert data['is_private'] == False


@pytest.mark.asyncio
async def test_auth_user_change_url(client, dbsession, user_data, urls_data):
    user = user_data
    response = await client.post('/user/signup', json=user)
    response = await client.post('/user/login', data=user)
    data = response.json()
    token = data['access_token']
    # Авторизованный юзер меняет статус своей ссылки
    # Про удаление делается аналогично
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    is_private = not urls_data[0]['is_private']
    response = await client.post(
        f'/{data["id"]}/is_private',
        json={'is_private': is_private},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['is_private'] == is_private


@pytest.mark.asyncio
async def test_auth_user_change_alien_url(client, dbsession, user_data, urls_data):
    # Авторизованный юзер меняет статус чужой ссылки - Отказ
    # Про удаление делается аналогично
    response = await client.post(
        '/',
        json=urls_data[0],
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    url_id = data['id']
    is_private = not urls_data[1]['is_private']
    user = user_data
    response = await client.post('/user/signup', json=user)
    response = await client.post('/user/login', data=user)
    data = response.json()
    token = data['access_token']
    response = await client.post(
        f'/{url_id}/is_private',
        json={'is_private': is_private},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_unauth_user_change_url(client, dbsession, user_data, urls_data):
    # Невторизованный юзер меняет статус ссылки - Отказ
    # Про удаление делается аналогично
    response = await client.post(
        '/',
        json=urls_data[0],
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    url_id = data['id']
    is_private = not urls_data[1]['is_private']
    response = await client.post(
        f'/{url_id}/is_private',
        json={'is_private': is_private},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_status_auth_user(client, dbsession, user_data, urls_data):
    # Статус авторизованного пользователя
    user = user_data
    response = await client.post('/user/signup', json=user)
    response = await client.post('/user/login', data=user)
    data = response.json()
    token = data['access_token']
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    url_id = data['id']
    response = await client.get(
        '/user/status',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['total'] == 1
    assert data['items'][0]['id'] == url_id
