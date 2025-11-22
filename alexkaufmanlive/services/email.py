"""Email subscription service."""

import requests


def subscribe_to_buttondown(email, tags=None, api_token=None):
    """
    Subscribe an email to Buttondown newsletter.

    Args:
        email: Email address to subscribe
        tags: Optional list of tags to apply
        api_token: api token for buttondown

    Returns:
        tuple: (success: bool, message: str, status_code: int)
    """
    if not email:
        return False, "Email is required", 400

    if not api_token:
        return False, "Buttondown API Token not set.", 500

    # Prepare data for Buttondown API
    data = {"email_address": email, "type": "regular"}
    if tags:
        for tag in tags:
            data["tag"] = tag

    # Make request to Buttondown API
    url = "https://api.buttondown.com/v1/subscribers"
    headers = {
        "Authorization": f"Token {api_token}",
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
