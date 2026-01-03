import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from api.models import DeathRate


class Command(BaseCommand):
    help = "Load death rates from air pollution CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to CSV file"
        )

    def handle(self, *args, **options):
        csv_path = Path(options["file"]).resolve()

        if not csv_path.exists():
            self.stderr.write(f"File not found: {csv_path}")
            return

        COL_TOTAL = "Deaths - Air pollution - Sex: Both - Age: Age-standardized (Rate)"
        COL_HOUSE = "Deaths - Household air pollution from solid fuels - Sex: Both - Age: Age-standardized (Rate)"
        COL_PM = "Deaths - Ambient particulate matter pollution - Sex: Both - Age: Age-standardized (Rate)"
        COL_OZONE = "Deaths - Ambient ozone pollution - Sex: Both - Age: Age-standardized (Rate)"

        created = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                country = row.get("Entity")
                code = row.get("Code")
                year = row.get("Year")

                if not country or not code or not year:
                    continue

                def to_float(val):
                    return float(val) if val not in ("", None) else None

                DeathRate.objects.update_or_create(
                    country_code=code.strip(),
                    year=int(year),
                    defaults={
                        "country": country.strip(),
                        "death_rate_air_pollution": to_float(row.get(COL_TOTAL)),
                        "death_rate_household_solid_fuels": to_float(row.get(COL_HOUSE)),
                        "death_rate_ambient_pm": to_float(row.get(COL_PM)),
                        "death_rate_ambient_ozone": to_float(row.get(COL_OZONE)),
                    }
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {created} records"))