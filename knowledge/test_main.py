from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

new_user_guid: str = '99999999-9999-9999-9999-999999999911'
new_user_id: int = 35


def test_activity_statistics_200():
    response = client.get("/user/activity_statistics?nbd_filter=scopus")
    assert response.status_code == 200
    assert all(bool(x in response.json().keys() and type(response.json()[x]) in [int, float]) for x in
               ["sum_documents", "sum_citations", "h_average"])


def test_activity_statistics_404_not_nbd():
    response = client.get(
        "/user/activity_statistics?nbd_filter=scopus1"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "scopus1 is not NBD."
    }


def test_create_user_201():
    response = client.post(
        "/user/",
        json={
            "Уникальный UUID идентификатор научного сотрудника": f"{new_user_guid}",
            "ФИО научного сотрудника": "Аванов Василий Андреевич",
            "Источник данных (Scopus, WOS, RISC)": "scopus",
            "Количество публикаций автора, проиндексированных источником": 303,
            "Количество цитирований автора": 1140,
            "Индекс Хирша, рассчитанный НБД": 14,
            "Ссылка на профиль автора в НБД": "https://www.scopus.com/authid/detail.uri?authorId=7404809618"
        }
    )
    assert response.status_code == 201
    assert response.json()['new user id'] and type(response.json()['new user id']) == int


def test_create_user_403_first():
    response = client.post(
        "/user/",
        json={
            "Уникальный UUID идентификатор научного сотрудника": f"{new_user_guid}",
            "ФИО научного сотрудника": "Аванов Василий Андреевич",
            "Источник данных (Scopus, WOS, RISC)": "scopus",
            "Количество публикаций автора, проиндексированных источником": 303,
            "Количество цитирований автора": 1140,
            "Индекс Хирша, рассчитанный НБД": 14,
            "Ссылка на профиль автора в НБД": "https://www.scopus.com/authid/detail.uri?authorId=7404809618"
        }
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are already exists in the system."
    }


def test_create_user_403_second():
    response = client.post(
        "/user/",
        json={
            "Уникальный UUID идентификатор научного сотрудника": f"{new_user_guid}",
            "ФИО научного сотрудника": "Рванов Василий Андреевич",
            "Источник данных (Scopus, WOS, RISC)": "scopus",
            "Количество публикаций автора, проиндексированных источником": 303,
            "Количество цитирований автора": 1140,
            "Индекс Хирша, рассчитанный НБД": 14,
            "Ссылка на профиль автора в НБД": "https://www.scopus.com/authid/detail.uri?authorId=7404809618"
        }
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": f"The user with guid {new_user_guid} already exists in the system."
    }


def test_get_user_200_none_fields():
    response = client.get(
        f"/user/{new_user_guid}/{new_user_id}"
    )
    assert response.status_code == 200
    assert response.json()['fullname'] and type(response.json()['fullname']) == str
    assert response.json()['h_index'] and type(response.json()['h_index']) == int
    assert response.json()['url'] and type(response.json()['url']) == str


def test_get_user_200_false_fields():
    response = client.get(
        f"/user/{new_user_guid}/{new_user_id}?fields=false"
    )
    assert response.status_code == 200
    assert response.json()['fullname'] and type(response.json()['fullname']) == str
    assert response.json()['h_index'] and type(response.json()['h_index']) == int
    assert response.json()['url'] and type(response.json()['url']) == str


def test_get_user_200_true_fields():
    response = client.get(
        f"/user/{new_user_guid}/{new_user_id}?fields=true"
    )
    assert response.status_code == 200
    assert response.json()['fullname'] and type(response.json()['fullname']) == str
    assert response.json()['h_index'] and type(response.json()['h_index']) == int
    assert response.json()['url'] and type(response.json()['url']) == str
    assert response.json()['document_count'] and type(response.json()['document_count']) == int
    assert response.json()['citation_count'] and type(response.json()['citation_count']) == int


def test_get_user_404():
    response = client.get(
        f"/user/{new_user_guid}/0"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f'User with id {0} and guid {new_user_guid} does not exist.'
    }


def test_get_all_users_422_not_filter():
    response = client.get(
        f"/user/"
    )
    assert response.status_code == 422
    assert response.json() == {
        'detail':
            [{'loc': ['query', 'nbd_filter'],
              'msg': 'field required',
              'type': 'value_error.missing'}]
    }


def test_get_all_users_200_filter_scopus_not_sort():
    response = client.get(
        f"/user/?nbd_filter=scopus"
    )
    assert response.status_code == 200
    assert response.json()['total'] and type(response.json()['items']) == list
    assert response.json()['total'] and type(response.json()['total']) == int
    assert response.json()['page'] and type(response.json()['page']) == int
    assert response.json()['size'] and type(response.json()['size']) == int


def test_get_all_users_404_use_two_true_sort():
    response = client.get(
        f"/user/?nbd_filter=scopus1"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "scopus1 is not NBD."
    }


def test_get_all_users_404_use_two_true_sort():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=false&sort_date=false"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f'You cannot sort by Hirsch and by date at the same time.'
    }


def test_get_all_users_404_use_two_false_sort():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=true&sort_date=true"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f'You cannot sort by Hirsch and by date at the same time.'
    }


def test_get_all_users_200_filter_scopus_h_sort_desc():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=true"
    )
    assert response.status_code == 200
    # add check sort
    assert response.json()['total'] and type(response.json()['items']) == list
    assert response.json()['total'] and type(response.json()['total']) == int
    assert response.json()['page'] and type(response.json()['page']) == int
    assert response.json()['size'] and type(response.json()['size']) == int


def test_get_all_users_200_filter_scopus_h_sort_asc():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=false"
    )
    assert response.status_code == 200
    # add check sort
    assert response.json()['total'] and type(response.json()['items']) == list
    assert response.json()['total'] and type(response.json()['total']) == int
    assert response.json()['page'] and type(response.json()['page']) == int
    assert response.json()['size'] and type(response.json()['size']) == int


def test_get_all_users_200_filter_scopus_data_sort_desc():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=true"
    )
    assert response.status_code == 200
    # add check sort
    assert response.json()['total'] and type(response.json()['items']) == list
    assert response.json()['total'] and type(response.json()['total']) == int
    assert response.json()['page'] and type(response.json()['page']) == int
    assert response.json()['size'] and type(response.json()['size']) == int


def test_get_all_users_200_filter_scopus_data_sort_asc():
    response = client.get(
        f"/user/?nbd_filter=scopus&sort_h=false"
    )
    assert response.status_code == 200
    # add check sort
    assert response.json()['total'] and type(response.json()['items']) == list
    assert response.json()['total'] and type(response.json()['total']) == int
    assert response.json()['page'] and type(response.json()['page']) == int
    assert response.json()['size'] and type(response.json()['size']) == int


def test_delete_user_200():
    response = client.delete(
        f"/user/{new_user_guid}/{new_user_id}"
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": f'User with user_guid {new_user_guid} is deleted'
    }


def test_delete_user_404():
    response = client.delete(
        f"/user/{new_user_guid}/{new_user_id}"
    )
    assert response.status_code == 404
    assert response.json() == {'detail': f'User with id {new_user_id} and guid {new_user_guid} does not exist.'}
