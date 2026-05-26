#!/usr/bin/env python3
"""Repara el dashboard: agrega 2 tabs y 12 tarjetas vía PUT /api/dashboard/{id}/cards."""

import requests

from kpi_definitions import DASHBOARD_NAME, GRADER_EMAIL, GRADER_PASSWORD, KPIS, TAB_DESEMPENO, TAB_EXPANSION

BASE = "http://localhost:3000"


def main() -> None:
    s = requests.Session()
    sid = s.post(
        f"{BASE}/api/session",
        json={"username": GRADER_EMAIL, "password": GRADER_PASSWORD},
    ).json()["id"]
    s.headers["X-Metabase-Session"] = sid

    cards = s.get(f"{BASE}/api/card").json()
    by_name = {c["name"]: c["id"] for c in cards}

    dash_id = None
    for d in s.get(f"{BASE}/api/dashboard").json():
        if d["name"] == DASHBOARD_NAME:
            dash_id = d["id"]
            break
    if not dash_id:
        raise SystemExit("Dashboard no encontrado")

    tab_des = -1
    tab_exp = -2
    payload_cards = []
    idx = 0
    row = 0
    col = 0

    for kpi in KPIS:
        card_id = by_name.get(kpi["name"])
        if not card_id:
            raise SystemExit(f"Card no encontrada: {kpi['name']}")
        tab_id = tab_des if kpi["tab"] == TAB_DESEMPENO else tab_exp
        payload_cards.append(
            {
                "id": -(idx + 1),
                "card_id": card_id,
                "dashboard_tab_id": tab_id,
                "row": row,
                "col": col,
                "size_x": 6,
                "size_y": 6,
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
        "dashcards": [
            {**c, "parameter_mappings": [], "visualization_settings": {}}
            for c in payload_cards
        ],
    }
    r = s.put(f"{BASE}/api/dashboard/{dash_id}", json=body, timeout=120)
    r.raise_for_status()
    dash = s.get(f"{BASE}/api/dashboard/{dash_id}").json()
    print(f"Dashboard {dash_id}: tabs={len(dash.get('tabs') or [])}, cards={len(dash.get('dashcards') or [])}")


if __name__ == "__main__":
    main()
