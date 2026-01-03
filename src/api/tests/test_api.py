from rest_framework import status
from rest_framework.test import APITestCase
from api.models import DeathRate


class TestDeathRateAPI(APITestCase):
    def setUp(self):
        # One sample record for GET/detail/update/delete tests
        self.sample = DeathRate.objects.create(
            country="Afghanistan",
            country_code="AFG",
            year=2017,
            death_rate_air_pollution=120.5,
            death_rate_household_solid_fuels=80.3,
            death_rate_ambient_pm=30.2,
            death_rate_ambient_ozone=10.1,
        )

    # 1) GET /api/deathrates/
    def test_list_endpoint(self):
        res = self.client.get("/api/deathrates/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

    # 2) GET /api/deathrates/?code=AFG
    def test_filter_by_country_code(self):
        res = self.client.get("/api/deathrates/?code=AFG")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)
        self.assertEqual(res.data[0]["country_code"], "AFG")

    # 3) GET /api/deathrates/?year=2017
    def test_filter_by_year(self):
        res = self.client.get("/api/deathrates/?year=2017")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)
        self.assertEqual(res.data[0]["year"], 2017)

    # 4) GET /api/deathrates/global-average/
    def test_global_average_endpoint(self):
        res = self.client.get("/api/deathrates/global-average/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)
        self.assertIn("year", res.data[0])
        self.assertIn("avg_air", res.data[0])

    # 5) POST /api/deathrates/create/
    def test_create_endpoint(self):
        payload = {
            "country": "India",
            "country_code": "IND",
            "year": 2018,
            "death_rate_air_pollution": 95.2,
            "death_rate_household_solid_fuels": 60.1,
            "death_rate_ambient_pm": 25.5,
            "death_rate_ambient_ozone": 8.3,
        }
        res = self.client.post("/api/deathrates/create/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DeathRate.objects.filter(country_code="IND", year=2018).exists())

    # 6) PUT /api/deathrates/<id>/update/
    def test_update_endpoint(self):
        payload = {
            "country": "Afghanistan",
            "country_code": "AFG",
            "year": 2017,
            "death_rate_air_pollution": 130.0,
            "death_rate_household_solid_fuels": 85.0,
            "death_rate_ambient_pm": 35.0,
            "death_rate_ambient_ozone": 12.0,
        }
        res = self.client.put(f"/api/deathrates/{self.sample.id}/update/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.sample.refresh_from_db()
        self.assertEqual(self.sample.death_rate_air_pollution, 130.0)

    # 7) DELETE /api/deathrates/<id>/delete/
    def test_delete_endpoint(self):
        res = self.client.delete(f"/api/deathrates/{self.sample.id}/delete/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DeathRate.objects.filter(id=self.sample.id).exists())
