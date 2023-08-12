from typing import Any

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

data: dict[str, Any] = {
    'menu1': {
        'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'title': 'menu1',
        'description': 'string',
    },
    'submenu1': {
        'id': '1368e5f2-867b-4ec6-99e7-85eecdbc673e',
        'title': 'submenu1',
        'description': 'string',
    },
    'dish1': {
        'id': '1cd622ff-3070-4644-8711-e6f83ae1388b',
        'title': 'dish1',
        'description': 'string',
        'price': 25.20,
        'response_price': '25.20',
    },
    'dish2': {
        'id': '218d5f50-76a6-4a04-8e1c-77859160685b',
        'title': 'dish2',
        'description': 'string',
        'price': 5.5,
        'response_price': '5.50',
    },
    'patch_dish1': {
        'title': 'patch_dish1',
        'description': 'patch_string1',
        'price': 11.0,
        'response_price': '11.00',
    },
    'patch_dish2': {
        'title': 'patch_dish2',
        'description': 'patch_string2',
        'price': 10,
        'response_price': '10.00',
    },
    'invalid_id': '4d8b79de-e0cd-483e-9294-5425a5194492',
}

path = f"/menus/{data['menu1']['id']}/submenus/" f"{data['submenu1']['id']}/dishes"


async def test_post_menu_with_submenu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['menu1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu1'])

    assert response.status_code == 201
    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['menu1']['title']
    assert response.json()['description'] == data['menu1']['description']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0

    mock = mocker.MagicMock(return_value=data['submenu1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu1']['id']}/submenus", json=data['submenu1']
    )

    assert response.status_code == 201
    assert response.json()['id'] == data['submenu1']['id']
    assert response.json()['title'] == data['submenu1']['title']
    assert response.json()['description'] == data['submenu1']['description']
    assert response.json()['dishes_count'] == 0


@pytest.mark.parametrize('test_id', [data['submenu1']['id'], data['invalid_id']])
async def test_get_all_dishes_empty(async_client: AsyncClient, test_id):
    response = await async_client.get(
        f"/menus/{data['menu1']['id']}/submenus/{test_id}/dishes"
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_get_submenu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{data['invalid_id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'


async def test_post_dish(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['dish1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(f'{path}', json=data['dish1'])

    assert response.status_code == 201
    assert response.json()['id'] == data['dish1']['id']
    assert response.json()['title'] == data['dish1']['title']
    assert response.json()['description'] == data['dish1']['description']
    assert response.json()['price'] == data['dish1']['response_price']


async def test_get_submenu_by_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{data['dish1']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['dish1']['id']
    assert response.json()['title'] == data['dish1']['title']
    assert response.json()['description'] == data['dish1']['description']
    assert response.json()['price'] == data['dish1']['response_price']


async def test_post_submenu_same_title(async_client: AsyncClient):
    response = await async_client.post(f'{path}', json=data['dish1'])

    assert response.status_code == 409
    assert response.json()['detail'] == 'This title already exists'


async def test_get_all_dishes_not_empty(
    async_client: AsyncClient, mocker: MockerFixture
):
    mock = mocker.MagicMock(return_value=data['dish2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(f'{path}', json=data['dish2'])

    assert response.status_code == 201
    assert response.json()['id'] == data['dish2']['id']
    assert response.json()['title'] == data['dish2']['title']
    assert response.json()['description'] == data['dish2']['description']
    assert response.json()['price'] == data['dish2']['response_price']

    response2 = await async_client.get(f'{path}')

    assert response2.status_code == 200
    assert len(response2.json()) == 2
    assert response2.json()[0]['id'] == data['dish1']['id']
    assert response2.json()[0]['title'] == data['dish1']['title']
    assert response2.json()[0]['description'] == data['dish1']['description']
    assert response2.json()[0]['price'] == data['dish1']['response_price']

    assert response2.json()[1]['id'] == data['dish2']['id']
    assert response2.json()[1]['title'] == data['dish2']['title']
    assert response2.json()[1]['description'] == data['dish2']['description']
    assert response2.json()[1]['price'] == data['dish2']['response_price']


async def test_get_menu_by_id_with_dishes(async_client: AsyncClient):
    response = await async_client.get(f"menus/{data['menu1']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['menu1']['id']
    assert response.json()['title'] == data['menu1']['title']
    assert response.json()['description'] == data['menu1']['description']
    assert response.json()['submenus_count'] == 1
    assert response.json()['dishes_count'] == 2


async def test_get_submenu_by_id_with_dishes(async_client: AsyncClient):
    response = await async_client.get(
        f"menus/{data['menu1']['id']}/submenus/{data['submenu1']['id']}"
    )

    assert response.status_code == 200
    assert response.json()['id'] == data['submenu1']['id']
    assert response.json()['title'] == data['submenu1']['title']
    assert response.json()['description'] == data['submenu1']['description']
    assert response.json()['dishes_count'] == 2


async def test_patch_dish(async_client: AsyncClient):
    response = await async_client.patch(
        f"{path}/{data['dish1']['id']}", json=data['patch_dish1']
    )

    assert response.status_code == 200
    assert response.json()['id'] == data['dish1']['id']
    assert response.json()['title'] == data['patch_dish1']['title']
    assert response.json()['description'] == data['patch_dish1']['description']
    assert response.json()['price'] == data['patch_dish1']['response_price']

    response2 = await async_client.patch(
        f"{path}/{data['dish2']['id']}", json=data['patch_dish2']
    )

    assert response.status_code == 200
    assert response2.json()['id'] == data['dish2']['id']
    assert response2.json()['title'] == data['patch_dish2']['title']
    assert response2.json()['description'] == data['patch_dish2']['description']
    assert response2.json()['price'] == data['patch_dish2']['response_price']


async def test_patch_submenu_same_title(async_client: AsyncClient):
    response = await async_client.patch(
        f"{path}/{data['dish1']['id']}", json=data['patch_dish2']
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'This title already exists'


async def test_patch_submenu_invalid_id(async_client: AsyncClient):
    response = await async_client.patch(
        f"{path}/{data['invalid_id']}", json=data['patch_dish1']
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'


async def test_get_all_submenus_after_patch(async_client: AsyncClient):
    response = await async_client.get(f'{path}')

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['id'] == data['dish1']['id']
    assert response.json()[0]['title'] == data['patch_dish1']['title']
    assert response.json()[0]['description'] == data['patch_dish1']['description']
    assert response.json()[0]['price'] == data['patch_dish1']['response_price']

    assert response.json()[1]['id'] == data['dish2']['id']
    assert response.json()[1]['title'] == data['patch_dish2']['title']
    assert response.json()[1]['description'] == data['patch_dish2']['description']
    assert response.json()[1]['price'] == data['patch_dish2']['response_price']


async def test_get_submenu_by_id_after_patch(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{data['dish1']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['dish1']['id']
    assert response.json()['title'] == data['patch_dish1']['title']
    assert response.json()['description'] == data['patch_dish1']['description']
    assert response.json()['price'] == data['patch_dish1']['response_price']


async def test_delete_menu(async_client: AsyncClient):
    response = await async_client.delete(f"{path}/{data['dish1']['id']}")

    assert response.status_code == 200
    assert response.json()['status'] is True
    assert response.json()['message'] == 'The dish has been deleted'


async def test_get_all_submenus_after_delete_dish(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu1']['id']}/submenus")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == data['submenu1']['id']
    assert response.json()[0]['title'] == data['submenu1']['title']
    assert response.json()[0]['description'] == data['submenu1']['description']
    assert response.json()[0]['dishes_count'] == 1


async def test_get_all_menus_after_delete_dish(async_client: AsyncClient):
    response = await async_client.get('/menus')

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']
    assert response.json()[0]['submenus_count'] == 1
    assert response.json()[0]['dishes_count'] == 1


async def test_get_menu_by_deleted_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{data['dish1']['id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'


async def test_delete_menu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{data['invalid_id']}")

    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'
