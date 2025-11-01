"""Test netzero API."""

import datetime

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


async def test_energy_site_get_config():
    """Test EnergySite async_get_config()."""
    token = "abcdef"
    system_id = 12345
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
    }

    with aioresponses() as mock:
        mock.get(
            f"https://api.netzero.energy/api/v1/{system_id}/config",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, token)
            site = netzero.EnergySite(auth, system_id)
            config = await site.async_get_config()

            assert config.backup_reserve_percent == 80
            assert config.operational_mode == netzero.OperationalMode.AUTONOMOUS
            assert config.energy_exports == netzero.EnergyExportMode.PV_ONLY
            assert config.grid_charging

            mock.assert_called_once_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                headers={
                    "authorization": f"Bearer {token}",
                },
                allow_redirects=True,
            )


def test_energy_site_config_values():
    """Test EnergySiteConfig with different values."""
    json_cfg = [
        {
            "backup_reserve_percent": 80,
            "operational_mode": "autonomous",
            "energy_exports": "pv_only",
            "grid_charging": True,
        },
        {
            "backup_reserve_percent": 55,
            "operational_mode": "self_consumption",
            "energy_exports": "never",
            "grid_charging": False,
        },
        {
            "backup_reserve_percent": 11,
            "operational_mode": "backup",
            "energy_exports": "battery_ok",
            "grid_charging": True,
        },
    ]
    backup = [80, 55, 11]
    mode = [
        netzero.OperationalMode.AUTONOMOUS,
        netzero.OperationalMode.SELF_CONSUMPTION,
        netzero.OperationalMode.BACKUP,
    ]
    export = [
        netzero.EnergyExportMode.PV_ONLY,
        netzero.EnergyExportMode.NEVER,
        netzero.EnergyExportMode.BATTERY_OK,
    ]
    charging = [True, False, True]

    for i, c in enumerate(json_cfg):
        config = netzero.EnergySiteConfig(None, None, c)

        assert config.backup_reserve_percent == backup[i]
        assert config.operational_mode == mode[i]
        assert config.energy_exports == export[i]
        assert config.grid_charging == charging[i]


async def test_energy_site_config_update():
    """Test EnergySiteConfig async_update."""
    token = "abcdef"
    system_id = 12345
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
    }

    with aioresponses() as mock:
        mock.get(
            f"https://api.netzero.energy/api/v1/{system_id}/config",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, token)
            config = netzero.EnergySiteConfig(auth, system_id)
            await config.async_update()

            assert config.backup_reserve_percent == 80
            assert config.operational_mode == netzero.OperationalMode.AUTONOMOUS
            assert config.energy_exports == netzero.EnergyExportMode.PV_ONLY
            assert config.grid_charging

            mock.assert_called_once_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                headers={
                    "authorization": f"Bearer {token}",
                },
                allow_redirects=True,
            )


async def test_energy_site_config_control():
    """Test EnergySiteConfig async_control."""
    token = "abcdef"
    system_id = 12345
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
    }

    with aioresponses() as mock:
        mock.post(
            f"https://api.netzero.energy/api/v1/{system_id}/config",
            status=200,
            payload=expected_response,
            repeat=4,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, token)
            config = netzero.EnergySiteConfig(auth, system_id)

            await config.async_control(backup_reserve_percent=100)
            mock.assert_called_once_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                method="POST",
                headers={
                    "authorization": f"Bearer {token}",
                },
                json={"backup_reserve_percent": 100},
                allow_redirects=True,
            )

            await config.async_control(
                operational_mode=netzero.OperationalMode.SELF_CONSUMPTION
            )
            mock.assert_called_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                method="POST",
                headers={
                    "authorization": f"Bearer {token}",
                },
                json={"operational_mode": "self_consumption"},
                allow_redirects=True,
            )

            await config.async_control(energy_exports=netzero.EnergyExportMode.NEVER)
            mock.assert_called_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                method="POST",
                headers={
                    "authorization": f"Bearer {token}",
                },
                json={"energy_exports": "never"},
                allow_redirects=True,
            )

            await config.async_control(grid_charging=False)
            mock.assert_called_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                method="POST",
                headers={
                    "authorization": f"Bearer {token}",
                },
                json={"grid_charging": False},
                allow_redirects=True,
            )


async def test_energy_site_live_status():
    """Test EnergySiteConfig live_status."""
    token = "abcdef"
    system_id = 12345
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
        "live_status": {
            "percentage_charged": 100.0,
            "solar_power": 4140,
            "battery_power": -2520,
            "load_power": 1620,
            "grid_power": 110,
            "generator_power": 40,
            "grid_status": "Active",
            "island_status": "on_grid",
            "storm_mode_active": False,
            "timestamp": "2020-12-31T23:59:59.900Z",
        },
    }

    with aioresponses() as mock:
        mock.get(
            f"https://api.netzero.energy/api/v1/{system_id}/config",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, token)
            config = netzero.EnergySiteConfig(auth, system_id)
            await config.async_update()

            status = config.live_status
            assert status.percentage_charged == 100.0
            assert status.solar_power == 4140
            assert status.battery_power == -2520
            assert status.load_power == 1620
            assert status.grid_power == 110
            assert status.generator_power == 40
            assert status.grid_status == netzero.GridStatus.ACTIVE
            assert status.island_status == netzero.IslandStatus.ON_GRID
            assert not status.storm_mode_active
            assert status.timestamp == datetime.datetime(
                2020, 12, 31, 23, 59, 59, 900000, tzinfo=datetime.UTC
            )

            mock.assert_called_once_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                headers={
                    "authorization": f"Bearer {token}",
                },
                allow_redirects=True,
            )


def test_energy_site_status_values():
    """Test EnergySiteStatus with different values."""
    json_status = [
        {
            "percentage_charged": 100.0,
            "solar_power": 4140,
            "battery_power": -2520,
            "load_power": 1620,
            "grid_power": 110,
            "generator_power": 40,
            "grid_status": "Active",
            "island_status": "on_grid",
            "storm_mode_active": False,
            "timestamp": "2020-12-31T23:59:59.900Z",
        },
        {
            "percentage_charged": 13.0,
            "solar_power": 3000,
            "battery_power": 0,
            "load_power": 1000,
            "grid_power": 2500,
            "generator_power": 100,
            "grid_status": "Inactive",
            "island_status": "on_grid",
            "storm_mode_active": True,
            "timestamp": "2021-01-01T01:00:00.000Z",
        },
        {
            "percentage_charged": 80.0,
            "solar_power": 44,
            "battery_power": 55,
            "load_power": 66,
            "grid_power": 77,
            "generator_power": 88,
            "grid_status": "Active",
            "island_status": "off_grid",
            "storm_mode_active": True,
            "timestamp": "2022-02-28T12:00:00.000Z",
        },
    ]
    charged = [100.0, 13.0, 80.0]
    solar = [4140, 3000, 44]
    battery = [-2520, 0, 55]
    load = [1620, 1000, 66]
    grid = [110, 2500, 77]
    gen = [40, 100, 88]
    grid_stat = [
        netzero.GridStatus.ACTIVE,
        netzero.GridStatus.INACTIVE,
        netzero.GridStatus.ACTIVE,
    ]
    island = [
        netzero.IslandStatus.ON_GRID,
        netzero.IslandStatus.ON_GRID,
        netzero.IslandStatus.OFF_GRID,
    ]
    storm = [False, True, True]
    time = [
        datetime.datetime(2020, 12, 31, 23, 59, 59, 900000, tzinfo=datetime.UTC),
        datetime.datetime(2021, 1, 1, 1, 0, 0, 0, tzinfo=datetime.UTC),
        datetime.datetime(2022, 2, 28, 12, 0, 0, 0, tzinfo=datetime.UTC),
    ]
    for i, s in enumerate(json_status):
        status = netzero.EnergySiteStatus(None, None, s)

        assert status.percentage_charged == charged[i]
        assert status.solar_power == solar[i]
        assert status.battery_power == battery[i]
        assert status.load_power == load[i]
        assert status.grid_power == grid[i]
        assert status.generator_power == gen[i]
        assert status.grid_status == grid_stat[i]
        assert status.island_status == island[i]
        assert status.storm_mode_active == storm[i]
        assert status.timestamp == time[i]


async def test_energy_site_status_update():
    """Test EnergySiteStatus async_update."""
    token = "abcdef"
    system_id = 12345
    expected_response = {
        "backup_reserve_percent": 80,
        "operational_mode": "autonomous",
        "energy_exports": "pv_only",
        "grid_charging": True,
        "live_status": {
            "percentage_charged": 100.0,
            "solar_power": 4140,
            "battery_power": -2520,
            "load_power": 1620,
            "grid_power": 110,
            "generator_power": 40,
            "grid_status": "Active",
            "island_status": "on_grid",
            "storm_mode_active": False,
            "timestamp": "2020-12-31T23:59:59.900Z",
        },
    }

    with aioresponses() as mock:
        mock.get(
            f"https://api.netzero.energy/api/v1/{system_id}/config",
            status=200,
            payload=expected_response,
        )
        async with aiohttp.ClientSession() as session:
            auth = netzero.Auth(session, token)
            status = netzero.EnergySiteStatus(auth, system_id)
            await status.async_update()

            assert status.percentage_charged == 100.0
            assert status.solar_power == 4140
            assert status.battery_power == -2520
            assert status.load_power == 1620
            assert status.grid_power == 110
            assert status.generator_power == 40
            assert status.grid_status == netzero.GridStatus.ACTIVE
            assert status.island_status == netzero.IslandStatus.ON_GRID
            assert not status.storm_mode_active
            assert status.timestamp == datetime.datetime(
                2020, 12, 31, 23, 59, 59, 900000, tzinfo=datetime.UTC
            )

            mock.assert_called_once_with(
                f"https://api.netzero.energy/api/v1/{system_id}/config",
                headers={
                    "authorization": f"Bearer {token}",
                },
                allow_redirects=True,
            )
