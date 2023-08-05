from typing import Any

from httpx import AsyncClient
from pytest_mock import MockerFixture

data: dict[str, Any] = {
    'menu1': {
        'id': '1fa85f64-5717-4562-b3fc-2c963f66afa6',
        'title': 'menu1',
        'description': 'string',
    },
    'menu2': {
        'id': '2c0534ce-2824-4407-9b80-8f52550bc5cf',
        'title': 'menu2',
        'description': 'string',
    },
    'patch_menu1': {'title': 'patch_menu1', 'description': 'patch_string1'},
    'patch_menu2': {'title': 'patch_menu2', 'description': 'patch_string2'},
    'invalid_id': '509ec0db-bcd5-4b9a-8a3a-e41996345676',
}


async def test_get_all_menus_empty(async_client: AsyncClient):
    response = await async_client.get('/menus')

    assert response.status_code == 200
    assert response.json() == []


async def test_get_menu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu1']['id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'


async def test_post_menu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['menu1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu1'])

    assert response.status_code == 201
    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['menu1']['title']
    assert response.json()['description'] == data['menu1']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0


async def test_get_menu_by_id(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu1']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['menu1']['title']
    assert response.json()['description'] == data['menu1']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0


async def test_post_menu_same_title(async_client: AsyncClient):
    response = await async_client.post('/menus', json=data['menu1'])

    assert response.status_code == 409
    assert response.json()['detail'] == 'This title already exists'


async def test_get_all_menus_not_empty(
    async_client: AsyncClient, mocker: MockerFixture
):
    mock = mocker.MagicMock(return_value=data['menu2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu2'])

    assert response.status_code == 201
    assert response.json()['id'] == data['menu2']['id']
    assert response.json()['title'] == data['menu2']['title']
    assert response.json()['description'] == data['menu2']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0

    response2 = await async_client.get('/menus')

    assert len(response2.json()) == 2
    assert response2.status_code == 200
    assert response2.json()[0]['id'] == data['menu1']['id']
    assert response2.json()[0]['title'] == data['menu1']['title']
    assert response2.json()[0]['description'] == data['menu1']['description']
    assert response2.json()[0]['submenus_count'] == 0
    assert response2.json()[0]['dishes_count'] == 0

    assert response2.json()[1]['id'] == data['menu2']['id']
    assert response2.json()[1]['title'] == data['menu2']['title']
    assert response2.json()[1]['description'] == data['menu2']['description']
    assert response2.json()[1]['submenus_count'] == 0
    assert response2.json()[1]['dishes_count'] == 0


async def test_patch_menu(async_client: AsyncClient):
    response = await async_client.patch(
        f"/menus/{data['menu1']['id']}", json=data['patch_menu1']
    )

    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['patch_menu1']['title']
    assert response.json()['description'] == data['patch_menu1']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0

    response2 = await async_client.patch(
        f"/menus/{data['menu2']['id']}", json=data['patch_menu2']
    )

    assert response2.json()['id'] == data['menu2']['id']
    assert response2.json()['title'] == data['patch_menu2']['title']
    assert response2.json()['description'] == data['patch_menu2']['description']
    assert response2.json()['submenus_count'] == 0
    assert response2.json()['dishes_count'] == 0


async def test_patch_menu_same_title(async_client: AsyncClient):
    response = await async_client.patch(
        f"/menus/{data['menu1']['id']}", json=data['patch_menu2']
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'This title already exists'


async def test_patch_menu_invalid_id(async_client: AsyncClient):
    response = await async_client.patch(
        f"/menus/{data['invalid_id']}", json=data['patch_menu1']
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'


async def test_get_all_menus_after_patch(async_client: AsyncClient):
    response = await async_client.get('/menus')

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['patch_menu1']['title']
    assert response.json()[0]['description'] == data['patch_menu1']['description']
    assert response.json()[0]['submenus_count'] == 0
    assert response.json()[0]['dishes_count'] == 0

    assert response.json()[1]['id'] == data['menu2']['id']
    assert response.json()[1]['title'] == data['patch_menu2']['title']
    assert response.json()[1]['description'] == data['patch_menu2']['description']
    assert response.json()[1]['submenus_count'] == 0
    assert response.json()[1]['dishes_count'] == 0


async def test_get_menu_by_id_after_patch(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu1']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['patch_menu1']['title']
    assert response.json()['description'] == data['patch_menu1']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0


async def test_delete_menu(async_client: AsyncClient):
    response = await async_client.delete(f"/menus/{data['menu1']['id']}")

    assert response.status_code == 200
    assert response.json()['status'] is True
    assert response.json()['message'] == 'The menu has been deleted'


async def test_get_all_menus_after_delete(async_client: AsyncClient):
    response = await async_client.get('/menus')

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == data['menu2']['id']
    assert response.json()[0]['title'] == data['patch_menu2']['title']
    assert response.json()[0]['description'] == data['patch_menu2']['description']
    assert response.json()[0]['submenus_count'] == 0
    assert response.json()[0]['dishes_count'] == 0


async def test_get_menu_by_deleted_id(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu1']['id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'


async def test_delete_menu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['invalid_id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'
