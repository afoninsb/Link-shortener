import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio()
async def test_app(client: AsyncClient, create_db, user_data, urls_data):

    # Регистрация юзера
    response = await client.post(
        '/user/signup',
        json=user_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['username'] == user_data['username']
    assert data['id'] == 1

    # Регистрация юзера c тем же username - отказ
    response = await client.post(
        '/user/signup',
        json=user_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Авторизация пользователя
    response = await client.post(
        '/user/login',
        data=user_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data.keys()
    assert 'token_type' in data.keys()
    assert data['token_type'] == 'bearer'
    token = data['access_token']

    # Авторизованный пользователь добавляет url
    url_0 = urls_data[0]
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'short' in data.keys()
    assert 'is_deleted' in data.keys()
    assert data['original'] == url_0['original']
    assert data['description'] == url_0['description']
    assert data['is_private'] == url_0['is_private']
    assert data['is_deleted'] == False
    auth_user_url_id = data['id']

    # Добавляем тот же url - Отказ
    url_0 = urls_data[0]
    response = await client.post(
        '/',
        json=urls_data[0],
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Неавторизованный пользователь добавляет url
    url_1 = urls_data[1]
    url_1['is_private'] = True
    response = await client.post(
        '/',
        json=urls_data[1],
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'short' in data.keys()
    assert 'is_deleted' in data.keys()
    assert data['id'] == 2
    assert data['original'] == url_1['original']
    assert data['description'] == url_1['description']
    assert data['is_deleted'] == False
    assert data['is_private'] == False
    user_url_id = data['id']

    # Авторизованный юзер меняет статус своей ссылки
    # Про удаление делается аналогично
    is_private = not urls_data[0]['is_private']
    response = await client.post(
        f'/{auth_user_url_id}/is_private',
        json={'is_private': is_private},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['is_private'] == is_private

    # Авторизованный юзер меняет статус чужой ссылки - Отказ
    # Про удаление делается аналогично
    is_private = not urls_data[1]['is_private']
    response = await client.post(
        f'/{user_url_id}/is_private',
        json={'is_private': is_private},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Неавторизованный юзер меняет статус ссылки - Отказ
    # Про удаление делается аналогично
    is_private = not urls_data[1]['is_private']
    response = await client.post(
        f'/{user_url_id}/is_private',
        json={'is_private': is_private},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Статус авторизованного пользователя
    response = await client.get(
        '/user/status',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['total'] == 1
    assert data['items'][0]['id'] == auth_user_url_id

    # Статус неавторизованного пользователя - Отказ
    response = await client.get(
        '/user/status',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Инфо авторизованного пользователя
    response = await client.get(
        '/user/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == user_data['username']
    assert data['id'] == 1

    # Инфо неавторизованного пользователя - Отказ
    response = await client.get(
        '/user/me',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Переходы по ссылке
    response = await client.get(
        '/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    response = await client.get(
        '/1',
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    # Статус ссылки
    response = await client.get('/1/status?full_info=1&page=1&size=10')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == 1
    assert data['transitions']['total'] == 2
    assert data['transitions']['items'][0]['user_id'] == 1
    assert data['transitions']['items'][1]['user_id'] is None


@pytest.mark.asyncio()
async def test_dropdb(dropdb):
    pass
