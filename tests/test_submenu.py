import pytest
from pytest_mock import MockerFixture
from httpx import AsyncClient

test_data = {
    "menu1": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "menu1",
        "description": "string"
    },
    "submenu1": {
        "id": "1368e5f2-867b-4ec6-99e7-85eecdbc673e",
        "title": "submenu1",
        "description": "string"
    },
    "submenu2": {
        "id": "25e016f4-1c2d-44a4-b567-57833821baf4",
        "title": "submenu2",
        "description": "string"
    },
    "patch_submenu1": {
        "title": "patch_submenu1",
        "description": "patch_string1"
    },
    "patch_submenu2": {
        "title": "patch_submenu2",
        "description": "patch_string2"
    },
    "invalid_id": "4d8b79de-e0cd-483e-9294-5425a5194492"
}

path = f"/menus/{test_data['menu1']['id']}/submenus"


async def test_post_menu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=test_data["menu1"]["id"])
    mocker.patch("uuid.uuid4", mock)
    response = await async_client.post("/menus", json=test_data["menu1"])

    assert response.status_code == 201
    assert response.json()["id"] == test_data["menu1"]["id"]
    assert response.json()["title"] == test_data["menu1"]["title"]
    assert response.json()["description"] == test_data["menu1"]["description"]
    assert response.json()["submenus_count"] == 0
    assert response.json()["dishes_count"] == 0


@pytest.mark.parametrize("test_id", [test_data["menu1"]["id"], test_data['invalid_id']])
async def test_get_all_submenus_empty(async_client: AsyncClient, test_id):
    response = await async_client.get(f"/menus/{test_id}/submenus")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_submenu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{test_data['invalid_id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"


async def test_post_submenu(async_client: AsyncClient, mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=test_data["submenu1"]["id"])
    mocker.patch("uuid.uuid4", mock)
    response = await async_client.post(f"{path}", json=test_data["submenu1"])

    assert response.status_code == 201
    assert response.json()["id"] == test_data["submenu1"]["id"]
    assert response.json()["title"] == test_data["submenu1"]["title"]
    assert response.json()["description"] == test_data["submenu1"]["description"]
    assert response.json()["dishes_count"] == 0


async def test_get_submenu_by_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{test_data['submenu1']['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == test_data["submenu1"]["id"]
    assert response.json()["title"] == test_data["submenu1"]["title"]
    assert response.json()["description"] == test_data["submenu1"]["description"]
    assert response.json()["dishes_count"] == 0


async def test_post_submenu_same_title(async_client: AsyncClient):
    response = await async_client.post(f"{path}", json=test_data["submenu1"])

    assert response.status_code == 409
    assert response.json()["detail"] == "This title already exists"


async def test_get_all_submenus_not_empty(async_client: AsyncClient,
                                       mocker: MockerFixture):
    mock = mocker.MagicMock(return_value=test_data["submenu2"]["id"])
    mocker.patch("uuid.uuid4", mock)
    response = await async_client.post(f"{path}", json=test_data["submenu2"])

    assert response.status_code == 201
    assert response.json()["id"] == test_data["submenu2"]["id"]
    assert response.json()["title"] == test_data["submenu2"]["title"]
    assert response.json()["description"] == test_data["submenu2"]["description"]
    assert response.json()["dishes_count"] == 0

    response2 = await async_client.get(f"{path}")

    assert response2.status_code == 200
    assert len(response2.json()) == 2
    assert response2.json()[0]["id"] == test_data["submenu1"]["id"]
    assert response2.json()[0]["title"] == test_data["submenu1"]["title"]
    assert response2.json()[0]["description"] == test_data["submenu1"]["description"]
    assert response2.json()[0]["dishes_count"] == 0

    assert response2.json()[1]["id"] == test_data["submenu2"]["id"]
    assert response2.json()[1]["title"] == test_data["submenu2"]["title"]
    assert response2.json()[1]["description"] == test_data["submenu2"]["description"]
    assert response2.json()[1]["dishes_count"] == 0


async def test_get_menu_by_id_with_submenus(async_client: AsyncClient):
    response = await async_client.get(f"menus/{test_data['menu1']['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == test_data["menu1"]["id"]
    assert response.json()["title"] == test_data["menu1"]["title"]
    assert response.json()["description"] == test_data["menu1"]["description"]
    assert response.json()["submenus_count"] == 2
    assert response.json()["dishes_count"] == 0


async def test_patch_submenu(async_client: AsyncClient):
    response = await async_client.patch(f"{path}/{test_data['submenu1']['id']}",
                                        json=test_data["patch_submenu1"])

    assert response.json()["id"] == test_data["submenu1"]["id"]
    assert response.json()["title"] == test_data["patch_submenu1"]["title"]
    assert response.json()["description"] == test_data["patch_submenu1"]["description"]
    assert response.json()["dishes_count"] == 0

    response2 = await async_client.patch(f"{path}/{test_data['submenu2']['id']}",
                                        json=test_data["patch_submenu2"])

    assert response2.json()["id"] == test_data["submenu2"]["id"]
    assert response2.json()["title"] == test_data["patch_submenu2"]["title"]
    assert response2.json()["description"] == test_data["patch_submenu2"]["description"]
    assert response2.json()["dishes_count"] == 0


async def test_patch_submenu_same_title(async_client: AsyncClient):
    response = await async_client.patch(f"{path}/{test_data['submenu1']['id']}",
                                        json=test_data["patch_submenu1"])

    assert response.status_code == 409
    assert response.json()["detail"] == "This title already exists"


async def test_patch_submenu_invalid_id(async_client: AsyncClient):
    response = await async_client.patch(f"{path}/{test_data['invalid_id']}",
                                        json=test_data["patch_submenu1"])
    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"


async def test_get_all_submenus_after_patch(async_client: AsyncClient):
    response = await async_client.get(f"{path}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == test_data["submenu1"]["id"]
    assert response.json()[0]["title"] == test_data["patch_submenu1"]["title"]
    assert response.json()[0]["description"] == test_data["patch_submenu1"]["description"]
    assert response.json()[0]["dishes_count"] == 0

    assert response.json()[1]["id"] == test_data["submenu2"]["id"]
    assert response.json()[1]["title"] == test_data["patch_submenu2"]["title"]
    assert response.json()[1]["description"] == test_data["patch_submenu2"]["description"]
    assert response.json()[1]["dishes_count"] == 0


async def test_get_submenu_by_id_after_patch(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{test_data['submenu1']['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == test_data["submenu1"]["id"]
    assert response.json()["title"] == test_data["patch_submenu1"]["title"]
    assert response.json()["description"] == test_data["patch_submenu1"]["description"]
    assert response.json()["dishes_count"] == 0


async def test_delete_menu(async_client: AsyncClient):
    response = await async_client.delete(f"{path}/{test_data['submenu1']['id']}")

    assert response.status_code == 200
    assert response.json()['status'] is True
    assert response.json()['message'] == "The submenu has been deleted"


async def test_get_all_submenus_after_delete_submenu(async_client: AsyncClient):
    response = await async_client.get(f"{path}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == test_data["submenu2"]["id"]
    assert response.json()[0]["title"] == test_data["patch_submenu2"]["title"]
    assert response.json()[0]["description"] == test_data["patch_submenu2"]["description"]
    assert response.json()[0]["dishes_count"] == 0


async def test_get_all_menus_after_delete_submenu(async_client: AsyncClient):
    response = await async_client.get("/menus")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == test_data["menu1"]["id"]
    assert response.json()[0]["title"] == test_data["menu1"]["title"]
    assert response.json()[0]["description"] == test_data["menu1"]["description"]
    assert response.json()[0]["submenus_count"] == 1
    assert response.json()[0]["dishes_count"] == 0


async def test_get_menu_by_deleted_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{test_data['submenu1']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"


async def test_delete_menu_by_invalid_id(async_client: AsyncClient):
    response = await async_client.get(f"{path}/{test_data['invalid_id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "submenu not found"
