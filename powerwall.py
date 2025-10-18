#!/usr/bin/env python3
"""Tesla Powerwall Control.

Controls Powerwall by sending requests via the Developer API on the
Netzero app. Use of the Developer API on Netzero is currently free.

The Developer API is documented at https://docs.netzero.energy/docs/tesla/API

The JSON file for --system-json should look like:
    {
        "api_token": "abcedf",
        "system_id": "12345"
    }
"""

import argparse
import asyncio
import json
import pathlib
import sys

import aiohttp

import netzero


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tesla Powerwall Control via Netzero",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--api-token", "-a", default=None, help="API token to use")
    parser.add_argument("--system-id", "-s", default=None, help="System to control")
    parser.add_argument(
        "--system-json",
        "-j",
        default=None,
        help="JSON file containing API token and System ID",
    )

    parser.add_argument(
        "--set-backup",
        "-b",
        type=int,
        default=None,
        help="Set backup reserve percentage",
    )
    parser.add_argument(
        "--set-mode",
        "-m",
        choices=["auto", "self"],
        default=None,
        help="Set operational mode (autonomous or self sufficiency)",
    )
    parser.add_argument(
        "--grid-charging",
        "-g",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable grid charging",
    )
    parser.add_argument(
        "--export",
        "-x",
        choices=["never", "pv", "both"],
        default=None,
        help="Energy export mode",
    )

    args = parser.parse_args()
    if args.system_json:
        with pathlib.Path(args.system_json).open(encoding="utf-8") as f:
            data = json.load(f)
            if args.api_token is None:
                args.api_token = data["api_token"]
            if args.system_id is None:
                args.system_id = data["system_id"]

    if not (args.api_token and args.system_id):
        print(
            "error: API token and System ID must be specified, either by --system-json or --api-token and system-id"
        )
        sys.exit(1)

    return args


async def main():
    """Main script entry point."""
    args = parse_args()
    request = ""
    operational_mode = None
    export_mode = None
    if args.set_backup:
        request += f" Backup reserve {args.set_backup}\n"

    if args.set_mode:
        request += f" Operational mode {args.set_mode}\n"
        if args.set_mode == "auto":
            operational_mode = netzero.OperationalMode.AUTONOMOUS
        else:
            operational_mode = netzero.OperationalMode.SELF_CONSUMPTION

    if args.grid_charging is not None:
        request += f" Grid charging allowed {args.grid_charging}\n"

    if args.export is not None:
        request += f" Energy export mode {args.export}\n"
        if args.export == "both":
            export_mode = netzero.EnergyExportMode.BATTERY_OK
        elif args.export == "pv":
            export_mode = netzero.EnergyExportMode.PV_ONLY
        else:
            export_mode = netzero.EnergyExportMode.NEVER

    async with aiohttp.ClientSession() as session:
        auth = netzero.Auth(session, args.api_token)
        site = netzero.EnergySiteConfig(auth, args.system_id)

        if request:
            print(f"Changing Powerwall state\n{request}")
            await site.async_control(
                backup_reserve_percent=args.set_backup,
                grid_charging=args.grid_charging,
                energy_exports=export_mode,
                operational_mode=operational_mode,
            )

        else:
            print("Reading Powerwall state:")
            await site.async_update()

        print(json.dumps(site.raw_data, indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
