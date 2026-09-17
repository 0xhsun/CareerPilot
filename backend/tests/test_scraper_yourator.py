"""Unit tests for scraper_yourator.py pure functions (no network calls)."""

import pytest

from app.scraper_yourator import _AREA_TO_YOURATOR_CODE, _build_url, _parse_salary


class TestBuildUrl:
    def test_contains_keyword(self):
        url = _build_url("Python", 1)
        assert "Python" in url

    def test_contains_page(self):
        url = _build_url("Python", 3)
        assert "page=3" in url

    def test_area_mapped_to_yourator_code(self):
        # 6001001000 → TPE
        url = _build_url("Python", 1, areas=["6001001000"])
        assert "TPE" in url
        assert "area" in url

    def test_unknown_area_skipped(self):
        url = _build_url("Python", 1, areas=["9999999999"])
        # area[] param should not appear at all
        assert "area%5B%5D" not in url

    def test_experience_mapped(self):
        url = _build_url("Python", 1, experience=["3"])
        assert "1_3_years" in url

    def test_unknown_experience_skipped(self):
        url = _build_url("Python", 1, experience=["999"])
        assert "years_of_exp" not in url

    def test_no_filters(self):
        url = _build_url("Python", 1)
        assert "area%5B%5D" not in url
        assert "years_of_exp" not in url

    def test_empty_areas_list(self):
        url = _build_url("Python", 1, areas=[])
        assert "area%5B%5D" not in url

    def test_empty_experience_list(self):
        url = _build_url("Python", 1, experience=[])
        assert "years_of_exp" not in url

    def test_multiple_areas(self):
        url = _build_url("Python", 1, areas=["6001001000", "6001002000"])
        assert "TPE" in url
        assert "NWT" in url
        assert url.count("area%5B%5D") == 2

    def test_multiple_experience(self):
        url = _build_url("Python", 1, experience=["1", "3"])
        assert "less_than_1" in url
        assert "1_3_years" in url

    # --- category[] tests ---

    def test_category_appears_in_url(self):
        url = _build_url("Python", 1, categories=["後端工程"])
        assert "category%5B%5D" in url
        assert "%E5%BE%8C%E7%AB%AF%E5%B7%A5%E7%A8%8B" in url  # URL-encoded 後端工程

    def test_multiple_categories(self):
        url = _build_url("Python", 1, categories=["後端工程", "AI 工程師"])
        assert url.count("category%5B%5D") == 2

    def test_empty_categories_no_param(self):
        url = _build_url("Python", 1, categories=[])
        assert "category" not in url

    def test_no_categories_by_default(self):
        url = _build_url("Python", 1)
        assert "category" not in url

    # --- monthly (salary range) tests ---

    def test_monthly_both_values(self):
        url = _build_url("Python", 1, salary_min=70000, salary_max=100000)
        assert "monthly=70000%2C100000" in url or "monthly=70000,100000" in url

    def test_monthly_only_min(self):
        url = _build_url("Python", 1, salary_min=50000)
        assert "monthly" in url
        assert "50000" in url

    def test_monthly_only_max(self):
        url = _build_url("Python", 1, salary_max=80000)
        assert "monthly" in url
        assert "80000" in url

    def test_monthly_zero_not_added(self):
        url = _build_url("Python", 1, salary_min=0, salary_max=0)
        assert "monthly" not in url

    def test_monthly_not_added_by_default(self):
        url = _build_url("Python", 1)
        assert "monthly" not in url


class TestParseSalary:
    def test_annual_salary_converted_to_monthly(self):
        low, high, display = _parse_salary("NT$ 600,000 - 900,000 (年薪)")
        assert low == 50000
        assert high == 75000

    def test_monthly_salary_unchanged(self):
        low, high, display = _parse_salary("NT$ 50,000 (月薪)")
        assert low == 50000
        assert high == 0

    def test_negotiable(self):
        low, high, display = _parse_salary("面議")
        assert low == 0
        assert high == 0
        assert display == "待遇面議"

    def test_none_returns_negotiable(self):
        low, high, display = _parse_salary(None)
        assert display == "待遇面議"

    def test_negotiable_alternate(self):
        low, high, display = _parse_salary("待遇面議")
        assert low == 0
        assert high == 0
        assert display == "待遇面議"

    def test_single_value_monthly(self):
        low, high, display = _parse_salary("NT$ 40,000 (月薪)")
        assert low == 40000
        assert high == 0
        assert "元以上" in display

    def test_annual_salary_display_string(self):
        low, high, display = _parse_salary("NT$ 600,000 - 900,000 (年薪)")
        assert "~" in display
        assert "50,000" in display
        assert "75,000" in display


class TestAreaMapping:
    def test_taoyuan_maps_to_tao(self):
        url = _build_url("Python", 1, areas=["6001005000"])
        assert "area%5B%5D=TAO" in url

    def test_hsinchu_expands_to_city_and_county(self):
        # 104's 6001006000 covers 新竹縣市; Yourator splits it into HSZ / HSQ
        url = _build_url("Python", 1, areas=["6001006000"])
        assert "area%5B%5D=HSZ" in url
        assert "area%5B%5D=HSQ" in url

    def test_keelung_maps_to_kee(self):
        assert "area%5B%5D=KEE" in _build_url("Python", 1, areas=["6001004000"])

    def test_yilan_maps_to_ila(self):
        assert "area%5B%5D=ILA" in _build_url("Python", 1, areas=["6001003000"])

    def test_miaoli_maps_to_mia(self):
        assert "area%5B%5D=MIA" in _build_url("Python", 1, areas=["6001007000"])

    def test_every_offered_area_is_mapped(self):
        from app.config import AREA_OPTIONS

        for area in AREA_OPTIONS:
            assert _AREA_TO_YOURATOR_CODE.get(area["value"]), area["label"]


class TestRemoteUrl:
    def test_absent_when_not_requested(self):
        assert "remote_work" not in _build_url("Python", 1)

    def test_full_remote(self):
        url = _build_url("Python", 1, remote=["full"])
        assert "remote_work%5B%5D=full" in url

    def test_partial_remote(self):
        url = _build_url("Python", 1, remote=["partial"])
        assert "remote_work%5B%5D=partial" in url

    def test_both_emit_two_params(self):
        url = _build_url("Python", 1, remote=["full", "partial"])
        assert url.count("remote_work%5B%5D=") == 2

    def test_unknown_key_skipped(self):
        assert "remote_work" not in _build_url("Python", 1, remote=["hybrid"])

    def test_combines_with_area(self):
        url = _build_url("Python", 1, areas=["6001005000"], remote=["full"])
        assert "area%5B%5D=TAO" in url
        assert "remote_work%5B%5D=full" in url


class TestRemoteTagging:
    """Yourator job payloads carry no remote field, so we tag from the filter."""

    @staticmethod
    async def _run(remote: list[str]) -> list[str]:
        from unittest.mock import patch

        from app.models import JobSearchRequest
        from app.scraper_yourator import scrape_jobs

        async def fake_fetch(session, url):
            return [{"path": "/companies/a/jobs/b", "name": "工程師", "company": {"brand": "A"}}]

        with patch("app.scraper_yourator._fetch_page", fake_fetch):
            jobs = await scrape_jobs(JobSearchRequest(keyword="Python", pages=1, remote=remote))
        return [j.remote_type for j in jobs]

    @pytest.mark.anyio
    async def test_single_filter_tags_every_job(self):
        assert await self._run(["full"]) == ["full"]

    @pytest.mark.anyio
    async def test_no_filter_leaves_type_unknown(self):
        assert await self._run([]) == [""]

    @pytest.mark.anyio
    async def test_ambiguous_filter_leaves_type_unknown(self):
        # With both values requested we cannot tell which one a job matched
        assert await self._run(["full", "partial"]) == [""]
