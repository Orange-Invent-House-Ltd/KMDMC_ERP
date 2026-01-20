from typing import Any, Dict, Optional, Union
from uuid import UUID

import geocoder
from django.http import HttpRequest
from rest_framework.request import Request as DRFRequest

RequestType = Union[HttpRequest, DRFRequest]


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]  # Take the first IP in the list
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_user_agent(request: HttpRequest) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


def get_geo_location(ip: str) -> Dict[str, str]:
    if not ip:  # Check if IP is None or an empty string
        return {}

    # Use geocoder to get the city and country from the IP address.
    g = geocoder.ip(ip)
    if g.ok:
        return {
            "city": g.city,
            "country": g.country,
        }
    return {}


def extract_api_request_metadata(
    request: Optional[RequestType],
) -> Optional[Dict[str, Optional[str]]]:
    if not isinstance(request, (HttpRequest, DRFRequest)):
        return None

    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    geo_location = get_geo_location(ip_address) or {}

    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
        "city": geo_location.get("city"),
        "country": geo_location.get("country"),
    }