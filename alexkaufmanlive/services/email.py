"""Email subscription service."""

import requests


def subscribe_to_buttondown(email, tags=None):
    """
    Subscribe an email to Buttondown newsletter.

    Args:
        email: Email address to subscribe
        tags: Optional list of tags to apply

    Returns:
        tuple: (success: bool, message: str, status_code: int)
    """
    if not email:
        return False, "Email is required", 400

    # Prepare data for Buttondown API
    data = {"email_address": email, "type": "regular"}
    if tags:
        for tag in tags:
            data["tag"] = tag

    # Make request to Buttondown API
    url = "https://api.buttondown.com/v1/subscribers"
    headers = {
        "Authorization": "Token daa462da-c883-4efa-a9e3-9e080bc204b9",
        "X-Buttondown-Collision-Behavior": "add",
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 201:
            return True, "Successfully subscribed!", 201
        else:
            return False, "Failed to subscribe", 400

    except requests.RequestException:
        return False, "Network error occurred", 500
    except Exception:
        return False, "An error occurred", 500
