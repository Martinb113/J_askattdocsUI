"""Test script for the new fetch configurations endpoint."""
import asyncio
import httpx


async def test_fetch_configurations():
    """Test the configuration fetching endpoint."""
    # First, login as admin to get token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "attid": "admin",
        "password": "Admin123!"
    }

    async with httpx.AsyncClient() as client:
        # Login
        print("[1] Logging in as admin...")
        login_response = await client.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print(f"[ERROR] Login failed: {login_response.status_code}")
            print(login_response.text)
            return

        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"[OK] Login successful! Token: {access_token[:20]}...")

        # Fetch configurations for SD_International domain
        fetch_url = "http://localhost:8000/api/v1/admin/configurations/fetch-by-domain"
        headers = {"Authorization": f"Bearer {access_token}"}
        request_data = {
            "domain": "SD_International",
            "log_as_userid": "admin",
            "environment": "production"
        }

        print(f"\n[2] Fetching configurations for domain 'SD_International'...")
        fetch_response = await client.post(fetch_url, json=request_data, headers=headers)

        if fetch_response.status_code == 200:
            print("[OK] Configurations fetched successfully!")
            result = fetch_response.json()
            print(f"\n[DATA]:\n{result['data']}\n")
        else:
            print(f"[ERROR] Failed to fetch configurations: {fetch_response.status_code}")
            print(fetch_response.text)


if __name__ == "__main__":
    asyncio.run(test_fetch_configurations())
