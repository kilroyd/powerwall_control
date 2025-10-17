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
import json
import pathlib
import sys

import requests

API_URL = "https://api.netzero.energy/api/v1"


def print_http_request(req):
    """Nicely output an HTTP request with headers."""
    print(
        "{}\n{}\r\n{}\r\n\r\n{}".format(
            "-----------START-----------",
            req.method + " " + req.url,
            "\r\n".join(f"{k}: {v}" for k, v in req.headers.items()),
            req.body,
        )
    )


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
        choices=["ss", "tbc"],
        default=None,
        help="Set operational mode (self sufficiency or time based control)",
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
        choices=["never", "pv_only", "battery"],
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


def main():
    """Main script entry point."""
    args = parse_args()
    url = f"{API_URL}/{args.system_id}/config"
    headers = {
        "Authorization": f"Bearer {args.api_token}",
        "Content-Type": "application/json",
    }
    response = None
    request = {}

    if args.set_backup:
        print(f" Backup reserve {args.set_backup}")
        request["backup_reserve_percent"] = args.set_backup

    if args.set_mode:
        print(f" Operational mode {args.set_mode}")
        request["operational_mode"] = (
            "autonomous" if args.set_mode == "tbc" else "self_consumption"
        )

    if args.grid_charging is not None:
        print(f" Grid charging allowed {args.grid_charging}")
        request["grid_charging"] = bool(args.grid_charging)

    if args.export is not None:
        print(f" Energy export mode {args.export}")
        if args.export == "battery":
            export_mode = "battery_ok"
        else:
            export_mode = args.export
        request["energy_exports"] = export_mode

    if request:
        print("Changing Powerwall state")

        json_request = json.dumps(request, indent=4)
        response = requests.post(url, headers=headers, data=json_request)
    else:
        print("Reading Powerwall state:")
        response = requests.get(url, headers=headers)

    print(json.dumps(response.json(), indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(main())
