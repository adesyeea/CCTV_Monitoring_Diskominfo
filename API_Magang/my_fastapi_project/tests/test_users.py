"""
Tests for user endpoints — placeholder.
"""


def test_get_users(client):
    """Test that the users endpoint returns a response."""
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
