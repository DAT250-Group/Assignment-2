from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app 

client = TestClient(app)

@patch("app.routes.profile_routes.get_user_from_session")
@patch("app.routes.profile_routes.run_query")
def test_evitar_escalada_privilegios_form(mock_run_query, mock_get_user):
    mock_get_user.return_value = {"id": 1, "username": "alumnoprueba", "role": "student"}
    
    form_data = {
        "full_name": "Alvaro Hacker",
        "phone": "123456",
        "address": "Mi casa",
        "bio": "Estudiante",
        "role": "admin"  # El ataque
    }
    
    response = client.post("/profile/update", data=form_data, follow_redirects=False)    
    assert response.status_code == 302 
    
    mock_run_query.assert_called_once()
    args, kwargs = mock_run_query.call_args
    consulta_sql = args[0]
    parametros_sql = args[1]
    
    assert "role=%s" not in consulta_sql
    assert "admin" not in parametros_sql