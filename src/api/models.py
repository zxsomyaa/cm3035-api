from django.db import models

class DeathRate(models.Model):
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    year = models.IntegerField()

    # Age-standardized death rates
    death_rate_air_pollution = models.FloatField(null=True, blank=True)
    death_rate_household_solid_fuels = models.FloatField(null=True, blank=True)
    death_rate_ambient_pm = models.FloatField(null=True, blank=True)
    death_rate_ambient_ozone = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("country_code", "year")
        indexes = [
            models.Index(fields=["country_code", "year"]),
            models.Index(fields=["year"]),
        ]

    def __str__(self):
        return f"{self.country_code} {self.year}"