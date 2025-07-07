<<<<<<< HEAD
# Business Card Generator

A Flask web application for creating and managing digital business cards with PDF generation and QR code functionality.

## Features

- User registration and authentication
- Create and edit business cards
- Generate PDF business cards
- Generate QR codes with contact information
- Upload and display company logos
- Role-based access control (New User, Subscription, Admin)
- SQLite database for data storage

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. **Clone or download the project files**

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv312
   ```

3. **Activate virtual environment:**
   - Windows (PowerShell):
     ```powershell
     .\venv312\Scripts\Activate.ps1
     ```
   - Windows (Command Prompt):
     ```cmd
     venv312\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv312/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

   Or use the provided batch file (Windows):
   ```cmd
   run.bat
   ```

6. **Access the application:**
   Open your web browser and go to: `http://localhost:5000`

## Usage

1. **Register a new account** with your email and password
2. **Login** to your account
3. **Create a business card** by filling out the form
4. **View your cards** in the dashboard
5. **Edit cards** as needed
6. **Download PDF** and **scan QR codes** for contact information

## User Roles

- **New User**: Can create only one business card
- **Subscription**: Can create multiple business cards
- **Admin**: Full access to all features

## File Structure

```
├── app.py              # Main Flask application
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── run.bat            # Windows batch file to run app
├── README.md          # This file
├── static/
│   └── uploads/       # Uploaded files (logos, PDFs, QR codes)
└── templates/         # HTML templates
    ├── home.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── form.html
    └── card.html
```

## Database

The application uses SQLite database (`business_card_db.sqlite`) which is automatically created when you first run the application.

## Troubleshooting

### PowerShell Execution Policy Error
If you get an execution policy error when trying to activate the virtual environment in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module Not Found Errors
Make sure you have activated the virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use
If port 5000 is already in use, you can change it in `app.py`:
```python
app.run(debug=True, port=5001)
```

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Werkzeug**: Utilities for WSGI applications
- **reportlab**: PDF generation
- **qrcode**: QR code generation
- **Pillow**: Image processing (required by qrcode)

## License

This project is open source and available under the MIT License. 
=======
# businesscardapp
>>>>>>> 0101197d7518f8b6a6d5efabaa7fb13f3f6009b7
