from httpx import AsyncClient
from pytest_mock import MockerFixture

data: dict[str, dict] = {
    'menu': {
        'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'title': 'menu1',
        'description': 'string',
    },
    'submenu': {
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
}


async def test_create_menu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['menu']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post('/menus', json=data['menu'])

    assert response.status_code == 201
    assert response.json()['id'] == data['menu']['id']


async def test_create_submenu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['submenu']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu']['id']}/submenus", json=data['submenu']
    )

    assert response.status_code == 201
    assert response.json()['id'] == data['submenu']['id']


async def test_create_dish1(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['dish1']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu']['id']}/submenus/{data['submenu']['id']}/dishes",
        json=data['dish1'],
    )

    assert response.status_code == 201
    assert response.json()['id'] == data['dish1']['id']


async def test_create_dish2(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=data['dish2']['id'])
    mocker.patch('uuid.uuid4', mock)
    response = await async_client.post(
        f"/menus/{data['menu']['id']}/submenus/{data['submenu']['id']}/dishes",
        json=data['dish2'],
    )

    assert response.status_code == 201
    assert response.json()['id'] == data['dish2']['id']


async def test_menu_by_id(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['menu']['id']
    assert response.json()['submenus_count'] == 1
    assert response.json()['dishes_count'] == 2


async def test_submenu_by_id(async_client: AsyncClient):
    response = await async_client.get(
        f"/menus/{data['menu']['id']}/submenus/{data['submenu']['id']}"
    )

    assert response.status_code == 200
    assert response.json()['id'] == data['submenu']['id']
    assert response.json()['dishes_count'] == 2


async def test_delete_submenu(async_client: AsyncClient):
    response = await async_client.delete(
        f"/menus/{data['menu']['id']}/submenus/{data['submenu']['id']}"
    )

    assert response.status_code == 200


async def test_get_all_submenus(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu']['id']}/submenus")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_all_dishes(async_client: AsyncClient):
    response = await async_client.get(
        f"/menus/{data['menu']['id']}/submenus/{data['submenu']['id']}/dishes"
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_menu_by_id_2(async_client: AsyncClient):
    response = await async_client.get(f"/menus/{data['menu']['id']}")

    assert response.status_code == 200
    assert response.json()['id'] == data['menu']['id']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0


async def test_delete_menu(async_client: AsyncClient):
    response = await async_client.delete(f"/menus/{data['menu']['id']}")

    assert response.status_code == 200


async def test_get_all_menus(async_client: AsyncClient):
    response = await async_client.get('/menus')

    assert response.status_code == 200
    assert response.json() == []
