# ShopEase — Django E-Commerce Demo

## Requirements
- Python 3.10+
- Internet connection for Bootstrap CDN
- Django and Pillow (installed from requirements.txt)

## Run on Windows PowerShell
1. Extract this ZIP into a folder.
2. Open PowerShell in that folder.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv myenv
   .\myenv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Create database tables:
   ```powershell
   python manage.py makemigrations store
   python manage.py migrate
   ```
6. Create an admin account:
   ```powershell
   python manage.py createsuperuser
   ```
7. Start the server:
   ```powershell
   python manage.py runserver
   ```
8. Visit http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/

## Add products
Log into `/admin/`, open Products, and add a name, description, category, price, stock, and optional image.

## Included
- Product listing, search, category filter, and details
- User registration/login/logout
- Session-based cart
- Checkout with cash on delivery
- Order history
- Django admin product/order management

## Before deployment
This is a learning/demo project. Set DEBUG=False, use a strong environment-based SECRET_KEY, configure ALLOWED_HOSTS, HTTPS/security settings, static/media hosting, backups, and a real payment gateway if needed. Test stock/order flows and validate production settings before accepting real customers.
