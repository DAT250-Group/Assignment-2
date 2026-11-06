from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app 

client = TestClient(app)

@patch("app.routes.auth_routes.run_query")
@patch("app.routes.auth_routes.verify_password")
def test_evitar_enumeracion_usuarios_login(mock_verify, mock_run_query):
    mensaje_seguro = "Invalid email or password."
    
    mock_run_query.return_value = None
    response_no_user = client.post("/login", data={"email": "falso@test.com", "password": "123"})
    
    mock_run_query.return_value = {"id": 1, "password_hash": "hash_real"} 
    mock_verify.return_value = False 
    response_wrong_pass = client.post("/login", data={"email": "real@test.com", "password": "123"})
    
    assert mensaje_seguro in response_no_user.text
    assert mensaje_seguro in response_wrong_pass.text