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


### Step 2: Set Up the Virtual Environment(Optional)

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
- **or**:

```bash
pip3 install -r requirements.txt
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

## Steps to Download and Install XAMPP  

1. **Download XAMPP**  
   - Visit the official XAMPP website: [https://www.apachefriends.org](https://www.apachefriends.org).  
   - Choose the version suitable for your operating system.  

2. **Install XAMPP**  
   - Run the downloaded installer.  
   - Follow the installation wizard to set up XAMPP on your machine.  
   - Select the necessary components: typically Apache, MySQL, PHP, and phpMyAdmin.  

3. **Start XAMPP**  
   - Launch the XAMPP Control Panel.  
   - Start the **Apache** and **MySQL** modules.

---

## Database Setup  

Follow these steps to create the database and configure the user for this project:  

1. **Access phpMyAdmin**  
   - Open your browser and navigate to `http://localhost/phpmyadmin`.  
   - Log in with the default credentials (usually `root` with no password).  

2. **Create a Database**  
   - Click on the **Databases** tab at the top.  
   - In the "Create database" section:  
     - Enter `prims` as the database name.  
     - Choose the collation `utf8mb4_general_ci` (recommended for compatibility).  
     - Click **Create**.  

3. **Create a User**  
   - Navigate to the **User accounts** tab in phpMyAdmin.  
   - Click **Add user account**.  
   - Fill in the details:  
     - **Username**: `admin`  
     - **Host name**: enter `localhost`.  
     - **Password**: `admin`  
     - **Re-type Password**: `admin`  

4. **Grant Privileges**  
   - Under the "Database for user" section:  
     - Select **Grant all privileges on database 'prims'**.  
   - Alternatively, scroll down to the "Global privileges" section and click **Check all**.  

5. **Apply Changes**  
   - Click **Go** to save the user and their privileges.  

6. **Verify Configuration**  
   - Return to the **User accounts** tab to confirm that the `admin` user has been created and assigned to the `prims` database.  

---

## Folder Structure

```
predictive-restaurant-inventory/
├── app/
│   ├── app.py
│   ├── db_config.py
│   ├── csv/
│   ├── models/
│   ├── static/
│   ├── templates/
│   └── training_and_diagnostics/
├── documentation/
│   └── images/          # Folder for documentation images, can add for ppt
├── .venv/                # Virtual environment
├── requirements.txt      # Python dependencies
└── README.md             # This file

```

---

## Troubleshooting

- **Flask command not found**: Use `python app/app.py` instead of `flask run`.
- **Virtual environment not activating**: Ensure you use the correct command for your OS.
- **mysqld.exe: Table '.\mysql\db' is marked as crashed and should be repaired**: Copy the files `db.frm`, `db.MAD`, and `db.MAI` from `C:\xampp\mysql\backup\mysql` and replace them in `C:\xampp\mysql\data\mysql`. 

---

## Notes

- Always activate the virtual environment before running the app.
- Do not commit `.venv/` to Git; it’s ignored via `.gitignore`.