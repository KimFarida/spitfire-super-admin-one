import os, logging, json
from typing import Callable

import requests
import psycopg2


DB_URL = os.getenv("SQLALCHEMY_DATABASE_URI")
# OK_CODES = [200, 201, 204, 404, 403, 401]
FAIL_CODES = [500, 501, 502, 503, 504, 505]


def clean_up(table: str, id: str):
    """
    deletes hanging records from a table

    :param table: table to delete from
    :param id: id of record to delete
    """
    if not table or not id:
        return

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id={id}")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error occurred while cleaning up {id} in {table}: {e}")


def check_endpoint(
        url: str,
        endpoint: tuple[str, str, Callable],
        data: dict = None,
        to_clean_ids: list[str] = None
) -> tuple[bool, tuple]:
    """
    checks if an endpoint is working

    :param url: base url
    :param endpoint: endpoint to check
    :param method: http method
    :param data: data to send
    :param config: contains id to clean up if endpoint is a delete endpoint
                    and it fails

    :return: True if endpoint is working, False otherwise
    """
    method, endpoint_url, extractor = endpoint
    full_url = f"{url}{endpoint_url}"
    try:
        if data:
            data = json.dumps(data)
    
        if method == "GET":
            response = requests.get(full_url, json=data)
        elif method == "PUT":
            response = requests.put(full_url, json=data)
        elif method == "POST":
            response = requests.post(full_url, json=data)
        elif method == "DELETE":
            if to_clean_ids[-1] is None:
                raise Exception("No id to clean")
            full_url = full_url.format(to_clean_ids[-1])
            response = requests.delete(full_url, json=data)
        elif method == "PATCH":
            response = requests.patch(full_url, json=data)
        else:
            raise Exception(f"Invalid method: {method}")

        response_data = response.json()
        print(response_data, response.status_code)
        logging.error(f"Response from {full_url}: {response_data}")

        if response.status_code in FAIL_CODES:
            logging.error(f"Error occurred while checking {full_url}. Status Code: {response.status_code}")
            return False, (None, None)

        if method == 'POST' and extractor:
            table, to_clean_id = extractor(response_data)
            return True, (table, to_clean_id)
        return True, (None, None)
    except Exception as e:
        logging.error(f"Error occurred while checking {full_url}: {e}")
        return False, (None, None)