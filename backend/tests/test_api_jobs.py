"""Integration tests for the /api/jobs router."""

from unittest.mock import AsyncMock, patch

from app.config import AREA_OPTIONS, EXPERIENCE_OPTIONS, REMOTE_OPTIONS
from app.models import JobListing


def _make_job(**kwargs) -> JobListing:
    defaults = {
        "job": "後端工程師",
        "date": "2026/02/23",
        "link": "https://www.104.com.tw/job/abc",
        "company": "測試公司",
        "city": "台北市",
        "experience": "1-3年",
        "education": "大學",
        "salary": "50,000 ~ 70,000 元",
        "salary_low": 50000,
        "salary_high": 70000,
        "is_featured": False,
    }
    defaults.update(kwargs)
    return JobListing(**defaults)


class TestOptions:
    def test_returns_area_and_experience_lists(self, client):
        resp = client.get("/api/jobs/options")
        assert resp.status_code == 200
        body = resp.json()
        assert body["areas"] == AREA_OPTIONS
        assert body["experience"] == EXPERIENCE_OPTIONS
        assert body["remote"] == REMOTE_OPTIONS

    def test_taoyuan_is_selectable(self, client):
        values = [a["value"] for a in client.get("/api/jobs/options").json()["areas"]]
        assert "6001005000" in values

    def test_northern_areas_are_selectable(self, client):
        areas = client.get("/api/jobs/options").json()["areas"]
        labels = {a["value"]: a["label"] for a in areas}
        # 宜蘭 / 基隆 / 苗栗 round out the north alongside 台北/新北/桃園/新竹
        assert labels["6001003000"] == "宜蘭縣"
        assert labels["6001004000"] == "基隆市"
        assert labels["6001007000"] == "苗栗縣"
        # 104 serves both 新竹市 and 新竹縣 jobs under this single code
        assert labels["6001006000"] == "新竹縣市"

    def test_area_values_are_unique(self, client):
        values = [a["value"] for a in client.get("/api/jobs/options").json()["areas"]]
        assert len(values) == len(set(values))

    def test_areas_have_value_and_label(self, client):
        resp = client.get("/api/jobs/options")
        for area in resp.json()["areas"]:
            assert "value" in area
            assert "label" in area


class TestSearchJobs:
    def test_returns_results_and_count(self, client):
        jobs = [_make_job(), _make_job(link="https://www.104.com.tw/job/xyz")]
        with patch("app.routers.jobs.scrape_104", new=AsyncMock(return_value=jobs)):
            resp = client.post("/api/jobs/search", json={"keyword": "Python", "pages": 1})
        assert resp.status_code == 200
        body = resp.json()
        assert body["count"] == 2
        assert len(body["results"]) == 2

    def test_elapsed_time_is_non_negative(self, client):
        with patch("app.routers.jobs.scrape_104", new=AsyncMock(return_value=[])):
            resp = client.post("/api/jobs/search", json={"keyword": "Python", "pages": 1})
        assert resp.json()["elapsed_time"] >= 0

    def test_empty_results(self, client):
        with patch("app.routers.jobs.scrape_104", new=AsyncMock(return_value=[])):
            resp = client.post("/api/jobs/search", json={"keyword": "nonexistent_xyz", "pages": 1})
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    def test_missing_keyword_returns_422(self, client):
        resp = client.post("/api/jobs/search", json={"pages": 1})
        assert resp.status_code == 422

    def test_empty_keyword_returns_422(self, client):
        resp = client.post("/api/jobs/search", json={"keyword": "", "pages": 1})
        assert resp.status_code == 422

    def test_pages_out_of_range_returns_422(self, client):
        resp = client.post("/api/jobs/search", json={"keyword": "Python", "pages": 0})
        assert resp.status_code == 422
        resp = client.post("/api/jobs/search", json={"keyword": "Python", "pages": 21})
        assert resp.status_code == 422

    def test_result_fields_match_job_listing_schema(self, client):
        job = _make_job()
        with patch("app.routers.jobs.scrape_104", new=AsyncMock(return_value=[job])):
            resp = client.post("/api/jobs/search", json={"keyword": "Python", "pages": 1})
        result = resp.json()["results"][0]
        assert result["job"] == job.job
        assert result["company"] == job.company
        assert result["salary_low"] == job.salary_low
