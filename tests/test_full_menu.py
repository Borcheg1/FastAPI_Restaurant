from typing import Any

from httpx import AsyncClient
from pytest_mock import MockerFixture

data: dict[str, Any] = {
    'menu1': {
        'id': '4219b783-b3ac-49da-9095-8d19e150a065',
        'title': 'menu1',
        'description': 'menu desc1',
    },
    'menu2': {
        'id': 'f7d8e28f-01a5-4676-94c2-7a72e09bd7eb',
        'title': 'menu2',
        'description': 'menu desc2',
    },
    'submenu1': {
        'id': 'b5c4edf4-9fbf-4788-8ced-cd091d962e03',
        'title': 'vegetarian soups',
        'description': 'various vegetarian soups',
    },
    'submenu2': {
        'id': 'b3ec7100-f1c9-4fcb-b53c-69cdeed74245',
        'title': 'regular soups',
        'description': 'various regular soups',
    },
    'submenu3': {
        'id': 'fc4a4bcb-1c44-47a6-ad07-b45fb497783c',
        'title': 'I\'m on menu 1',
        'description': 'submenu desc 3',
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
    'dish3': {
        'id': '9821f28c-04d5-4aed-b1f1-051d8af38f70',
        'title': 'I\'m on submenu 2',
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
}

path = '/all_data/get'


async def test_get_empty(async_client: AsyncClient):
    response = await async_client.get(f'{path}')

    assert response.status_code == 200
    assert response.json() == []


async def test_get_with_menu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['menu1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu1'])

    assert response.status_code == 201

    response = await async_client.get(f'{path}')

    assert response.status_code == 200
    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']
    assert response.json()[0]['submenus_list'] == []


async def test_get_with_submenu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['submenu1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu1']['id']}/submenus", json=data['submenu1']
    )

    assert response.status_code == 201

    response = await async_client.get(f'{path}')

    submenu = response.json()[0]['submenus_list'][0]

    assert response.status_code == 200
    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']
    assert submenu['id'] == data['submenu1']['id']
    assert submenu['title'] == data['submenu1']['title']
    assert submenu['description'] == data['submenu1']['description']
    assert submenu['dishes_list'] == []


async def test_get_with_dish(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['dish1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu1']['id']}/submenus/{data['submenu1']['id']}/dishes",
        json=data['dish1']
    )

    assert response.status_code == 201

    response = await async_client.get(f'{path}')

    submenu = response.json()[0]['submenus_list'][0]
    dish = response.json()[0]['submenus_list'][0]['dishes_list'][0]

    assert response.status_code == 200

    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']

    assert submenu['id'] == data['submenu1']['id']
    assert submenu['title'] == data['submenu1']['title']
    assert submenu['description'] == data['submenu1']['description']

    assert dish['id'] == data['dish1']['id']
    assert dish['title'] == data['dish1']['title']
    assert dish['description'] == data['dish1']['description']
    assert dish['price'] == data['dish1']['response_price']


async def test_get_after_patch(async_client: AsyncClient):
    response = await async_client.patch(
        f"/menus/{data['menu1']['id']}/submenus/{data['submenu1']['id']}/dishes/{data['dish1']['id']}",
        json=data['patch_dish1']
    )

    assert response.status_code == 200

    response = await async_client.get(f'{path}')

    submenu = response.json()[0]['submenus_list'][0]
    dish = response.json()[0]['submenus_list'][0]['dishes_list'][0]

    assert response.status_code == 200

    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']

    assert submenu['id'] == data['submenu1']['id']
    assert submenu['title'] == data['submenu1']['title']
    assert submenu['description'] == data['submenu1']['description']

    assert dish['id'] == data['dish1']['id']
    assert dish['title'] == data['patch_dish1']['title']
    assert dish['description'] == data['patch_dish1']['description']
    assert dish['price'] == data['patch_dish1']['response_price']


async def test_get_with_many_items(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['menu2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu2'])

    assert response.status_code == 201

    mock = mocker.MagicMock(return_value=data['submenu2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f'/menus/{data["menu2"]["id"]}/submenus', json=data['submenu2']
    )

    assert response.status_code == 201

    mock = mocker.MagicMock(return_value=data['submenu3']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f'/menus/{data["menu1"]["id"]}/submenus', json=data['submenu3']
    )

    assert response.status_code == 201

    mock = mocker.MagicMock(return_value=data['dish2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f'/menus/{data["menu2"]["id"]}/submenus/{data["submenu2"]["id"]}/dishes',
        json=data['dish2']
    )

    assert response.status_code == 201

    mock = mocker.MagicMock(return_value=data['dish3']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f'/menus/{data["menu2"]["id"]}/submenus/{data["submenu2"]["id"]}/dishes',
        json=data['dish3']
    )

    assert response.status_code == 201

    response = await async_client.get(f'{path}')

    submenu1 = response.json()[0]['submenus_list'][0]
    submenu2 = response.json()[1]['submenus_list'][0]
    submenu3 = response.json()[0]['submenus_list'][1]

    dish1 = response.json()[0]['submenus_list'][0]['dishes_list'][0]
    dish2 = response.json()[1]['submenus_list'][0]['dishes_list'][0]
    dish3 = response.json()[1]['submenus_list'][0]['dishes_list'][1]

    assert response.status_code == 200

    assert response.json()[0]['id'] == data['menu1']['id']
    assert response.json()[0]['title'] == data['menu1']['title']
    assert response.json()[0]['description'] == data['menu1']['description']

    assert response.json()[1]['id'] == data['menu2']['id']
    assert response.json()[1]['title'] == data['menu2']['title']
    assert response.json()[1]['description'] == data['menu2']['description']

    assert submenu1['id'] == data['submenu1']['id']
    assert submenu1['title'] == data['submenu1']['title']
    assert submenu1['description'] == data['submenu1']['description']

    assert submenu2['id'] == data['submenu2']['id']
    assert submenu2['title'] == data['submenu2']['title']
    assert submenu2['description'] == data['submenu2']['description']

    assert submenu3['id'] == data['submenu3']['id']
    assert submenu3['title'] == data['submenu3']['title']
    assert submenu3['description'] == data['submenu3']['description']
    assert submenu3['dishes_list'] == []

    assert dish1['id'] == data['dish1']['id']
    assert dish1['title'] == data['patch_dish1']['title']
    assert dish1['description'] == data['patch_dish1']['description']
    assert dish1['price'] == data['patch_dish1']['response_price']

    assert dish2['id'] == data['dish2']['id']
    assert dish2['title'] == data['dish2']['title']
    assert dish2['description'] == data['dish2']['description']
    assert dish2['price'] == data['dish2']['response_price']

    assert dish3['id'] == data['dish3']['id']
    assert dish3['title'] == data['dish3']['title']
    assert dish3['description'] == data['dish3']['description']
    assert dish3['price'] == data['dish3']['response_price']
