#!/usr/bin/env python3
"""Bootstrap Metabase: setup, usuario de calificación, BD, dashboard y 12 KPIs SQL."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

from kpi_definitions import (
    DASHBOARD_NAME,
    GRADER_EMAIL,
    GRADER_PASSWORD,
    KPIS,
    TAB_DESEMPENO,
    TAB_EXPANSION,
)

METABASE_URL = "http://localhost:3000"
POSTGRES_HOST = "postgres"
POSTGRES_DB = "retailmax"
POSTGRES_USER = "retailmax"
POSTGRES_PASS = "retailmax"


class MetabaseClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def wait_until_ready(self, timeout: int = 600) -> None:
        deadline = time.time() + timeout
        last_progress = -1.0
        while time.time() < deadline:
            try:
                r = self.session.get(f"{self.base_url}/api/health", timeout=10)
                if r.status_code in (200, 503):
                    body = r.json()
                    status = body.get("status")
                    progress = body.get("progress")
                    if progress is not None and progress != last_progress:
                        print(f"  Metabase iniciando... {int(progress * 100)}%")
                        last_progress = progress
                    if status == "ok":
                        return
            except requests.RequestException:
                pass
            time.sleep(5)
        raise TimeoutError("Metabase no respondió a tiempo en /api/health")

    def setup_token(self) -> str | None:
        r = self.session.get(f"{self.base_url}/api/session/properties", timeout=30)
        r.raise_for_status()
        return r.json().get("setup-token")

    def run_setup(self, token: str) -> None:
        payload = {
            "token": token,
            "user": {
                "first_name": "Calificar",
                "last_name": "UVG",
                "email": GRADER_EMAIL,
                "password": GRADER_PASSWORD,
                "site_name": "RetailMax Analytics",
            },
            "database": None,
            "invite": None,
            "prefs": {
                "site_name": "RetailMax Analytics",
                "site_locale": "es",
            },
        }
        r = self.session.post(f"{self.base_url}/api/setup", json=payload, timeout=60)
        r.raise_for_status()

    def login(self) -> str:
        r = self.session.post(
            f"{self.base_url}/api/session",
            json={"username": GRADER_EMAIL, "password": GRADER_PASSWORD},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["id"]

    def list_databases(self) -> list[dict]:
        r = self.session.get(f"{self.base_url}/api/database", timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def add_database(self) -> int:
        payload = {
            "engine": "postgres",
            "name": "RetailMax",
            "details": {
                "host": POSTGRES_HOST,
                "port": 5432,
                "dbname": POSTGRES_DB,
                "user": POSTGRES_USER,
                "password": POSTGRES_PASS,
                "ssl": False,
            },
            "auto_run_queries": True,
            "is_full_sync": True,
            "schedules": {},
        }
        r = self.session.post(f"{self.base_url}/api/database", json=payload, timeout=60)
        r.raise_for_status()
        db_id = r.json()["id"]
        self.sync_database(db_id)
        return db_id

    def sync_database(self, db_id: int) -> None:
        self.session.post(f"{self.base_url}/api/database/{db_id}/sync_schema", timeout=60)
        for _ in range(60):
            r = self.session.get(f"{self.base_url}/api/database/{db_id}", timeout=30)
            r.raise_for_status()
            if r.json().get("initial_sync_status") == "complete":
                return
            time.sleep(2)

    def get_retailmax_db_id(self) -> int:
        for db in self.list_databases():
            if db.get("name") == "RetailMax" and db.get("engine") == "postgres":
                return db["id"]
        return self.add_database()

    def create_card(self, db_id: int, kpi: dict) -> int:
        payload = {
            "name": kpi["name"],
            "dataset_query": {
                "database": db_id,
                "type": "native",
                "native": {"query": kpi["sql"], "template-tags": {}},
            },
            "display": kpi["display"],
            "visualization_settings": {},
        }
        r = self.session.post(f"{self.base_url}/api/card", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["id"]

    def find_dashboard(self) -> dict | None:
        r = self.session.get(f"{self.base_url}/api/dashboard", timeout=30)
        r.raise_for_status()
        for dash in r.json():
            if dash.get("name") == DASHBOARD_NAME:
                return dash
        return None

    def create_dashboard_with_cards(self, tabs: dict[str, list[int]]) -> int:
        r = self.session.post(
            f"{self.base_url}/api/dashboard",
            json={
                "name": DASHBOARD_NAME,
                "description": "Dashboard de Estrategia y Expansión Comercial — RetailMax",
            },
            timeout=60,
        )
        r.raise_for_status()
        dash_id = r.json()["id"]

        tab_des = -1
        tab_exp = -2
        tab_key = {TAB_DESEMPENO: tab_des, TAB_EXPANSION: tab_exp}
        dashcards = []
        idx = 0
        row = 0
        col = 0

        for tab_name in (TAB_DESEMPENO, TAB_EXPANSION):
            for cid in tabs[tab_name]:
                dashcards.append(
                    {
                        "id": -(idx + 1),
                        "card_id": cid,
                        "dashboard_tab_id": tab_key[tab_name],
                        "row": row,
                        "col": col,
                        "size_x": 6,
                        "size_y": 6,
                        "parameter_mappings": [],
                        "visualization_settings": {},
                    }
                )
                idx += 1
                if col == 0:
                    col = 6
                else:
                    col = 0
                    row += 6

        body = {
            "name": DASHBOARD_NAME,
            "description": "Dashboard de Estrategia y Expansión Comercial — RetailMax",
            "tabs": [
                {"id": tab_des, "name": TAB_DESEMPENO},
                {"id": tab_exp, "name": TAB_EXPANSION},
            ],
            "dashcards": dashcards,
        }
        r = self.session.put(
            f"{self.base_url}/api/dashboard/{dash_id}",
            json=body,
            timeout=120,
        )
        r.raise_for_status()
        return dash_id


def is_already_bootstrapped(client: MetabaseClient) -> bool:
    try:
        client.login()
        dash = client.find_dashboard()
        return dash is not None
    except requests.HTTPError:
        return False


def main() -> int:
    client = MetabaseClient(METABASE_URL)
    print("Esperando Metabase...")
    client.wait_until_ready()

    token = client.setup_token()
    if token:
        print("Ejecutando setup inicial con usuario de calificación...")
        client.run_setup(token)
    else:
        print("Metabase ya configurado.")

    print("Iniciando sesión...")
    client.login()

    if client.find_dashboard():
        print("Dashboard ya existe. Bootstrap omitido.")
        return 0

    print("Conectando base de datos RetailMax...")
    db_id = client.get_retailmax_db_id()

    tabs: dict[str, list[int]] = {TAB_DESEMPENO: [], TAB_EXPANSION: []}
    all_card_ids: list[int] = []

    for kpi in KPIS:
        print(f"  Creando: {kpi['name']}")
        card_id = client.create_card(db_id, kpi)
        tabs[kpi["tab"]].append(card_id)
        all_card_ids.append(card_id)

    print("Creando dashboard con 2 tabs...")
    dash_id = client.create_dashboard_with_cards(tabs)
    print(f"Listo. Dashboard id={dash_id} en {METABASE_URL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
