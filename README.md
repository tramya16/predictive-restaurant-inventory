# Predictive Restaurant Inventory Management System (PRIMS)

PRIMS is a Flask-based app that predicts ingredient demand for restaurants, reducing waste and preventing stockouts. It uses machine learning to automate inventory management and order placement.

## Getting Started

### Prerequisites

- **Python 3.x**: Install from [python.org](https://www.python.org/downloads/).
- **Git**: Install from [git-scm.com](https://git-scm.com/).

### Step 1: Clone the Repository

Clone the repo to your local machine:

```bash
git clone https://github.com/tramya16/predictive-restaurant-inventory.git
cd predictive-restaurant-inventory
```


### Step 2: Set Up the Virtual Environment

Create and activate the virtual environment:

- **On Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

- **On macOS/Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies

Install required dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask Application

Run the Flask app with:

- **On Windows**:
  ```bash
  python app/app.py
  ```

- **On macOS/Linux**:
  ```bash
  python3 app/app.py
  ```

Visit `http://127.0.0.1:5000/` in your browser to see the app.

---

## Folder Structure

```
predictive-restaurant-inventory/
├── app/
│   ├── app.py
│   ├── static/
│   └── templates/
├── documentation/
│   └── images/          # Folder for documentation images
├── .venv/                # Virtual environment
├── requirements.txt      # Python dependencies
└── README.md             # This file

```

---

## Troubleshooting

- **Flask command not found**: Use `python app/app.py` instead of `flask run`.
- **Virtual environment not activating**: Ensure you use the correct command for your OS.

---

## Notes

- Always activate the virtual environment before running the app.
- Do not commit `.venv/` to Git; it’s ignored via `.gitignore`.
```