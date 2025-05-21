TO CREATE A NEW USER IN THE DATABASE.

To register an email in the database===>python manage.py shell
Import the User Model into it ===> from django.contrib.auth.models import User
Create a username with the mail ID and password ===> User.objects.create_user(username='Saran', email='saransuresh01s@gmail.com', password='Starky@900')
Verify that the created username, mailId and password exists in database ===>User.objects.filter(email='your_email@example.com').exists()
to generate a random username in the database:
import uuid
new_username = f"user_{uuid.uuid4().hex[:8]}"
User.objects.create_user(username=new_username, email="your_email@example.com", password="your_password")
print(f"New user created successfully with username: {new_username}")
exit the shell ===> exit()

TO SHOW  THE REGISTERED USER IN THE DATABASE
To register an email in the database===>python manage.py shell
Import the User Model into it ===> from django.contrib.auth.models import User
Shows all the registered usernames in the database:
usernames = User.objects.values_list('username', flat=True)
print(list(usernames))
exit the shell ===> exit()

shows all the  usernames along with the mail in the database:
users = User.objects.values('username', 'email')
for user in users:
    print(user)

exit the shell ===> exit()

TO DELETE ALL THE REGISTERED USERS IN THE DATABASE
To register an email in the database===>python manage.py shell
Import the User Model into it ===> from django.contrib.auth.models import User
Deletes the existing user in the database:
username = "your_existing_username"

try:
    user = User.objects.get(username=username)
    user.delete()
    print(f"User '{username}' deleted successfully!")
except User.DoesNotExist:
    print("User does not exist.")
exit the shell ===> exit()


CREATING A SUPERUSER
Creating a superuser(admin) ===> python manage.py createsuperuser

Assign Admin Prvileges for the user:
from django.contrib.auth.models import User
# Get the user you want to make an admin
user = User.objects.get(username="Admin")
# Grant admin privileges
user.is_staff = True  # Allows access to the admin panel
user.is_superuser = True  # Gives full control like a superuser
user.save()
print(f"User {user.username} is now an admin!")



Requsites:
pip install django openpyxl
Create forms.py into your Macro app.
