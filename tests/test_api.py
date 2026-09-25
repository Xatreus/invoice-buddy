from fastapi.testclient import TestClient

from invoice_buddy.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "invoice-buddy",
    }


def test_get_invoices():
    response = client.get("/invoices")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_anomalies():
    response = client.get("/anomalies")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ask(monkeypatch):
    def fake_run_agent(session, question):
        assert question == "How much did we spend?"
        return "You spent ₹10,000."

    monkeypatch.setattr(
        "invoice_buddy.api.run_agent",
        fake_run_agent,
    )

    response = client.post(
        "/ask",
        json={
            "question": "How much did we spend?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "How much did we spend?"
    assert data["answer"] == "You spent ₹10,000."
