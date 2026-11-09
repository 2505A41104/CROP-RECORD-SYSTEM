# Agriculture Crop Record System — Python + Flask

This version is based on the uploaded Agriculture Crop Record System HTML file, but adds a real Python backend.

## Technologies
- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Open-Meteo Weather API
- CSV import/export

## Project structure

```text
crop_record_system_flask/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

`crop_records.db` is created automatically when the Flask application starts. It stores crop records in SQLite.

## How to run in Visual Studio Code

1. Open the `crop_record_system_flask` folder in VS Code.
2. Open the VS Code terminal.
3. Create a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install Flask:

```bash
pip install -r requirements.txt
```

5. Run the project:

```bash
python app.py
```

6. Open:

```text
http://127.0.0.1:5000
```

## Important

This is now a Python/Flask web application. The browser interface is still HTML/CSS/JavaScript, but Python handles the server and SQLite database.

Do not open `index.html` directly with double-click. Run `app.py` and open the Flask address in the browser.
