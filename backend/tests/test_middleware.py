import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from api.middleware import get_current_user, get_current_admin
from api.auth import create_access_token

app = FastAPI()

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"], "email": current_user["email"]}

@app.get("/admin")
async def admin_route(current_user: dict = Depends(get_current_admin)):
    return {"message": "admin access granted"}

client = TestClient(app)

def test_protected_route_without_token():
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_protected_route_with_valid_token():
    token = create_access_token({"user_id": "123", "email": "test@example.com", "role": "user"})
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["user_id"] == "123"
    assert response.json()["email"] == "test@example.com"

def test_protected_route_with_invalid_token():
    response = client.get("/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_admin_route_requires_admin_role():
    # Regular user token
    user_token = create_access_token({"user_id": "123", "email": "user@test.com", "role": "user"})
    response = client.get("/admin", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]
    
    # Admin token
    admin_token = create_access_token({"user_id": "456", "email": "admin@test.com", "role": "admin"})
    response = client.get("/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
