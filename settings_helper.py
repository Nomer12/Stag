from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict

from config import get_db_connection


DEFAULT_LOW_STOCK_ALERT = 50
DEFAULT_NEAR_EXPIRY_ALERT = 90
DEFAULT_CRITICAL_EXPIRY_ALERT = 30
DEFAULT_NEWLY_RECEIVED_DAYS = 7
DEFAULT_RHU_NAME = "Rural Health Unit"
DEFAULT_RHU_LOCATION = "Bustos, Bulacan"


def get_system_settings() -> Dict[str, Any]:
    """
    Shared settings source for Inventory, Expiry/Wastage,
    Receiving, Reports, and other MediTrack modules.

    The old low_stock_alert value remains available for compatibility.
    """
    db = None
    cursor = None

    defaults = {
        "low_stock_alert": DEFAULT_LOW_STOCK_ALERT,
        "near_expiry_alert": DEFAULT_NEAR_EXPIRY_ALERT,
        "critical_expiry_alert": DEFAULT_CRITICAL_EXPIRY_ALERT,
        "newly_received_days": DEFAULT_NEWLY_RECEIVED_DAYS,
        "rhu_name": DEFAULT_RHU_NAME,
        "rhu_location": DEFAULT_RHU_LOCATION,
        "contact_number": "",
        "email_address": "",
    }

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                low_stock_alert,
                near_expiry_alert,
                critical_expiry_alert,
                newly_received_days,
                rhu_name,
                rhu_location,
                contact_number,
                email_address
            FROM settings
            WHERE setting_id = 1
            LIMIT 1
            """
        )

        settings = cursor.fetchone()

        if not settings:
            return defaults

        return {
            "low_stock_alert": int(
                settings.get("low_stock_alert")
                or DEFAULT_LOW_STOCK_ALERT
            ),
            "near_expiry_alert": int(
                settings.get("near_expiry_alert")
                or DEFAULT_NEAR_EXPIRY_ALERT
            ),
            "critical_expiry_alert": int(
                settings.get("critical_expiry_alert")
                or DEFAULT_CRITICAL_EXPIRY_ALERT
            ),
            "newly_received_days": int(
                settings.get("newly_received_days")
                or DEFAULT_NEWLY_RECEIVED_DAYS
            ),
            "rhu_name": (
                settings.get("rhu_name")
                or DEFAULT_RHU_NAME
            ),
            "rhu_location": (
                settings.get("rhu_location")
                or DEFAULT_RHU_LOCATION
            ),
            "contact_number": (
                settings.get("contact_number") or ""
            ),
            "email_address": (
                settings.get("email_address") or ""
            ),
        }

    except Exception as exc:
        print("Settings helper error:", exc)
        return defaults

    finally:
        if cursor is not None:
            cursor.close()

        if db is not None:
            db.close()


def days_until(expiry_date: Any) -> int:
    try:
        if isinstance(expiry_date, datetime):
            expiry = expiry_date.date()
        elif isinstance(expiry_date, date):
            expiry = expiry_date
        else:
            expiry = datetime.strptime(
                str(expiry_date),
                "%Y-%m-%d",
            ).date()

        return (expiry - date.today()).days

    except Exception:
        return 999999


def get_expiry_status(
    days_remaining: int,
    *,
    critical_days: int | None = None,
    near_expiry_days: int | None = None,
) -> str:
    settings = None

    if critical_days is None or near_expiry_days is None:
        settings = get_system_settings()

    if critical_days is None:
        critical_days = settings["critical_expiry_alert"]

    if near_expiry_days is None:
        near_expiry_days = settings["near_expiry_alert"]

    days_remaining = int(days_remaining)

    if days_remaining < 0:
        return "Expired"

    if days_remaining <= int(critical_days):
        return "Critical"

    if days_remaining <= int(near_expiry_days):
        return "Near Expiry"

    return "Good"


def get_inventory_status(
    days_remaining: int,
    stock: int,
    low_stock_alert: int | None = None,
    near_expiry_alert: int | None = None,
) -> str:
    """
    Backward-compatible helper for modules that still use one combined
    stock and expiry status.
    """
    settings = None

    if low_stock_alert is None or near_expiry_alert is None:
        settings = get_system_settings()

    if low_stock_alert is None:
        low_stock_alert = settings["low_stock_alert"]

    if near_expiry_alert is None:
        near_expiry_alert = settings["near_expiry_alert"]

    stock = int(stock or 0)
    days_remaining = int(days_remaining)

    if stock <= 0:
        return "Out of Stock"

    if days_remaining < 0:
        return "Expired"

    if days_remaining <= int(near_expiry_alert):
        return "Near Expiry"

    if stock <= int(low_stock_alert):
        return "Low Stock"

    return "Active"


def get_status_color(status: str) -> str:
    colors = {
        "Active": "green",
        "Good": "green",
        "Low Stock": "orange",
        "Near Expiry": "yellow",
        "Critical": "red",
        "Expired": "red",
        "Out of Stock": "gray",
    }

    return colors.get(status, "gray")