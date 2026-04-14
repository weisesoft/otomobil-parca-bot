import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, render_template_string

# 1) Google Sheet bağlantısı
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_key.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("otomobil_parca_listesi").sheet1  # Sheet adın farklıysa değiştir
    return sheet

# 2) Filtreleme fonksiyonu
def get_parts(brand=None, model=None, category=None):
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    results = []

    for row in rows:
        if brand and str(row["brand"]).lower() != str(brand).lower():
            continue
        if model and str(row["model"]).lower() != str(model).lower():
            continue
        if category and str(row["category"]).lower() != str(category).lower():
            continue
        results.append(row)

    return results


# 3) HTML Arayüz
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Otomobil Parça Arama</title>
</head>
<body>
    <h1>Otomobil Parça Arama</h1>
    <form method="GET" action="/search">
        <label>Marka:</label>
        <input type="text" name="brand" placeholder="Örn: Opel"><br><br>

        <label>Model:</label>
        <input type="text" name="model" placeholder="Örn: 2015"><br><br>

        <label>Kategori:</label>
        <input type="text" name="category" placeholder="Örn: Fren Sistemi"><br><br>

        <button type="submit">Ara</button>
    </form>

    {% if parts is not none %}
        <h2>Sonuçlar:</h2>
        {% if parts %}
            <ul>
            {% for p in parts %}
                <li>{{ p.brand }} {{ p.model }} | {{ p.category }} | {{ p.part_name }} → {{ p.price }} TL</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>Bu filtrelere uygun parça bulunamadı.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, parts=None)

@app.route("/search", methods=["GET"])
def search():
    brand = request.args.get("brand") or None
    model = request.args.get("model") or None
    category = request.args.get("category") or None

    parts = get_parts(brand=brand, model=model, category=category)

    # dict → attribute erişimi için küçük bir hack
    class Obj: 
        def __init__(self, d): self.__dict__ = d

    parts_obj = [Obj(p) for p in parts]

    return render_template_string(HTML_TEMPLATE, parts=parts_obj)

if __name__ == "__main__":
    app.run(debug=True)
