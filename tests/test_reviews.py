import pytest

def review_payload(user_id=1, tmdb_movie_id=123, rating=8, review_text="Solid movie."):
    return {
        "user_id": user_id,
        "tmdb_movie_id": tmdb_movie_id,
        "rating": rating,
        "review_text": review_text,
    }

def test_create_review_ok(client):
    r = client.post("/api/reviews", json=review_payload())
    assert r.status_code == 201

    data = r.json()
    assert data["id"] >= 1
    assert data["user_id"] == 1
    assert data["tmdb_movie_id"] == 123
    assert data["rating"] == 8
    assert data["review_text"] == "Solid movie."

def test_list_reviews_returns_list(client):
    client.post("/api/reviews", json=review_payload(user_id=2, tmdb_movie_id=200, rating=7, review_text="Nice"))
    client.post("/api/reviews", json=review_payload(user_id=3, tmdb_movie_id=201, rating=9, review_text="Class"))

    r = client.get("/api/reviews")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_review_404(client):
    r = client.get("/api/reviews/999999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()

def test_get_review_by_id_ok(client):
    created = client.post("/api/reviews", json=review_payload(user_id=10, tmdb_movie_id=500, rating=6, review_text="ok"))
    review_id = created.json()["id"]

    r = client.get(f"/api/reviews/{review_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == review_id
    assert data["user_id"] == 10
    assert data["tmdb_movie_id"] == 500


@pytest.mark.parametrize("bad_rating", [0, 11, -1, 100])
def test_bad_rating_422(client, bad_rating):
    r = client.post("/api/reviews", json=review_payload(rating=bad_rating))
    assert r.status_code == 422
