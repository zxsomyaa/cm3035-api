from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Avg

from .models import DeathRate
from .serializers import DeathRateSerializer


def home(request):
    ADMIN_USERNAME = "somya"
    ADMIN_PASSWORD = "admin123"

    rows = [
        ("Get all death rates", "/api/deathrates/", "Returns all death rate records in the database."),
        ("Filter by country code", "/api/deathrates/?code=AFG", "Returns records for a given ISO country code (example: AFG)."),
        ("Filter by year", "/api/deathrates/?year=2017", "Returns records for a given year (example: 2017)."),
        ("Filter by country + year", "/api/deathrates/?code=AFG&year=2017", "Returns records for a given country in a given year."),
        ("Global average death rates by year", "/api/deathrates/global-average/", "Returns global average death rates grouped by year."),
        ("Create a new record (POST)", "/api/deathrates/create/", "Creates a new record using a POST request."),
        ("View record by ID", "/api/deathrates/1/", "Retrieves one record by its ID (example: 1)."),
        ("Update record by ID (PUT/PATCH)", "/api/deathrates/1/update/", "Updates a record by ID using PUT or PATCH."),
        ("Delete record by ID (DELETE)", "/api/deathrates/1/delete/", "Deletes a record by ID."),
    ]

    table_rows_html = "\n".join(
        f"""
        <tr>
            <td>{title}</td>
            <td><a href="{url}" target="_blank"><code>{url}</code></a></td>
            <td>{desc}</td>
        </tr>
        """
        for title, url, desc in rows
    )

    return HttpResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CM3035 – Death Rates from Air Pollution API</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
      line-height: 1.4;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}
    th, td {{
      border: 1px solid #333;
      padding: 10px;
      vertical-align: top;
      text-align: left;
    }}
    th {{ background: #f2f2f2; }}
    tr:hover {{ background: #fafafa; }}
    code {{
      background: #eee;
      padding: 2px 4px;
      border-radius: 4px;
    }}
    pre {{
      background: #111;
      color: #f5f5f5;
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;
    }}
  </style>
</head>
<body>

  <h1>CM3035 Coursework – Death Rates from Air Pollution API</h1>

  <h2>API Endpoints</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 24%;">Title</th>
        <th style="width: 28%;">URL</th>
        <th>What it means</th>
      </tr>
    </thead>
    <tbody>
      {table_rows_html}
    </tbody>
  </table>

  <h2>Run Information</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 30%;">Item</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Python</td><td><code>3.12</code></td></tr>
      <tr><td>Django</td><td><code>6.0</code></td></tr>
      <tr><td>Framework</td><td>Django REST Framework</td></tr>
      <tr><td>Database</td><td>SQLite</td></tr>
    </tbody>
  </table>

  <h2>How to Run (Terminal)</h2>
  <pre>
# From project root (CM3035 Project Somya)
source myenv/bin/activate
cd src
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py load_deathrates --file ../dataset/death-rates-from-air-pollution.csv
python3 manage.py runserver
  </pre>

  <h2>Run Tests</h2>
  <pre>
python3 manage.py test -v 2
  </pre>

  <h2>Admin</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 30%;">Item</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Admin site</td><td><a href="/admin/" target="_blank"><code>/admin/</code></a></td></tr>
      <tr><td>Admin username</td><td><code>{ADMIN_USERNAME}</code></td></tr>
      <tr><td>Admin password</td><td><code>{ADMIN_PASSWORD}</code></td></tr>
    </tbody>
  </table>

</body>
</html>
        """,
        content_type="text/html",
    )


@api_view(["GET"])
def deathrates_list(request):
    qs = DeathRate.objects.all().order_by("id")

    code = request.query_params.get("code")
    year = request.query_params.get("year")

    if code:
        qs = qs.filter(country_code=code)

    if year:
        try:
            year_int = int(year)
            qs = qs.filter(year=year_int)
        except ValueError:
            return Response({"detail": "year must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = DeathRateSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def deathrates_detail(request, pk):
    obj = get_object_or_404(DeathRate, pk=pk)
    serializer = DeathRateSerializer(obj)
    return Response(serializer.data)


@api_view(["POST"])
def deathrates_create(request):
    serializer = DeathRateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "PUT"])
def deathrates_update(request, pk):
    obj = get_object_or_404(DeathRate, pk=pk)
    partial = request.method == "PATCH"
    serializer = DeathRateSerializer(obj, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def deathrates_delete(request, pk):
    obj = get_object_or_404(DeathRate, pk=pk)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def global_average_by_year(request):
    data = (
        DeathRate.objects.values("year")
        .annotate(
            avg_air=Avg("death_rate_air_pollution"),
            avg_household=Avg("death_rate_household_solid_fuels"),
            avg_pm=Avg("death_rate_ambient_pm"),
            avg_ozone=Avg("death_rate_ambient_ozone"),
        )
        .order_by("year")
    )
    return Response(list(data))