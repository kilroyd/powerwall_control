"""Test netzero API."""

import aiohttp
from aioresponses import aioresponses

import netzero


async def test_auth_request_get():
    """Test Auth.request get.

    Check the request is sent to the appropriate URL with the
    appropriate authorization header.
    """
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
    }
    with aioresponses() as mock:
        mock.get(
            "https://api.netzero.energy/api/v1/sub/path1",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, "TESTTOKENABCDEF12345")

            custom_headers = {"KEY1": "VALUE1"}
            response = await auth.request("GET", "sub/path1", headers=custom_headers)

            assert response.status == 200
            assert await response.json() == expected_response
            mock.assert_called_once_with(
                "https://api.netzero.energy/api/v1/sub/path1",
                headers={
                    "authorization": "Bearer TESTTOKENABCDEF12345",
                    "KEY1": "VALUE1",
                },
                allow_redirects=True,
            )


async def test_auth_request_post():
    """Test Auth.request post.

    Check the request is sent to the appropriate URL with the
    appropriate authorization header.
    """
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
    }
    with aioresponses() as mock:
        mock.post(
            "https://api.netzero.energy/api/v1/sub/path2",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, "TESTTOKENABCDEF54321")

            custom_headers = {"KEY2": "VALUE2"}
            response = await auth.request("POST", "sub/path2", headers=custom_headers)

            assert response.status == 200
            assert await response.json() == expected_response
            mock.assert_called_once_with(
                "https://api.netzero.energy/api/v1/sub/path2",
                method="POST",
                headers={
                    "authorization": "Bearer TESTTOKENABCDEF54321",
                    "KEY2": "VALUE2",
                },
                allow_redirects=True,
            )
