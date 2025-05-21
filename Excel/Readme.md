# **Git Bash and Git LFS Setup for Large File Handling in GitHub**

## **Introduction**
This guide provides a comprehensive step-by-step process to set up **Git Bash** and **Git LFS** for handling large files in a Git repository and pushing them to GitHub. It includes installation instructions, LFS setup, and pushing large files to your GitHub repository.


### **Step 1: Download Git Bash**
- Visit the official [Git website](https://git-scm.com/downloads).
- Download the **Git Bash** installer for your operating system (Windows, macOS, or Linux).
- Right click on the folder that you want you to push to the git then you can see the option like **Open Git Bash here**

### **Step 2: Install Git Bash**
- Run the downloaded installer.
- Follow the installation steps, keeping the default settings recommended.
- Make sure to select the option to use Git from the command line.

### **Step 3: Verify the Installation**
After installation, verify that Git Bash is correctly installed by running the following command:
```bash
git --version
```

### **Step 4: Download and Install Git LFS**
- Visit the [Git LFS Downloads page](https://git-lfs.github.com/).
- Download the installer for your operating system.
- Run the installer and follow the instructions to complete the installation.
- Once Git LFS is installed, you need to initialize it within Git. Run the following commands

## Step 5: Initialize Git Repository  
If you haven't already initialized a Git repository, run:  

```bash
git init
```

## Step 6: Install Git LFS  
If you haven't installed Git LFS yet, do so with the following command:  

```bash
git lfs install
```

## Step 7: Track the Large Folder  
To track the `synthetic_data_generator` folder using Git LFS, use:  

```bash
git lfs track "synthetic_data_generator/*"
```

## Step 8: Add and Commit the Changes  
Now, add the `.gitattributes` file and the `synthetic_data_generator` folder to your repository:  

```bash
git add .gitattributes
git add synthetic_data_generator/
```

## Step 9: Commit the Changes  
Commit these changes to Git:  

```bash
git commit -m "Track synthetic_data_generator folder with Git LFS"
```

## Step 10: Push the Repository (if using remote)  
If you plan to push this repository to a remote (e.g., GitHub, GitLab), you'll first need to set up the remote:  

```bash
git remote add origin <remote-repository-url>
git push -u origin master
```

### Key Explanations of Commands:
1. **`git lfs install`**: Initializes Git LFS in your repository, setting up the necessary hooks for managing large files.
2. **`git lfs version`**: Displays the installed version of Git LFS to confirm the installation.
3. **`git lfs track "*.mp4"`**: Tracks `.mp4` files (or any file type you specify) and adds them to `.gitattributes` for LFS management.
4. **`git add .gitattributes`**: Stages the `.gitattributes` file to be committed.
5. **`git add <your-large-file>`**: Stages the large files that have been tracked by Git LFS.
6. **`git commit -m "message"`**: Commits the staged changes (both the `.gitattributes` file and large files).
7. **`git push origin master`**: Pushes the local commits (including large files) to GitHub.
8. **`git lfs status`**: Checks and shows the status of files managed by Git LFS.


----------------------------------------------

# DJANGO ADMIN DATABASE SYSTEM

## TO CREATE A NEW USER IN THE DATABASE

### Register an Email in the Database
```sh
python manage.py shell
```

### Import the User Model
```python
from django.contrib.auth.models import User
```

### Create a Username with Email ID and Password
```python
User.objects.create_user(username='Saran', email='saransuresh01s@gmail.com', password='Starky@900')
```

### Verify That the Created User Exists in the Database
```python
User.objects.filter(email='your_email@example.com').exists()
```

### Generate a Random Username in the Database
```python
import uuid
new_username = f"user_{uuid.uuid4().hex[:8]}"
User.objects.create_user(username=new_username, email="your_email@example.com", password="your_password")
print(f"New user created successfully with username: {new_username}")
```

### Exit the Shell
```sh
exit()
```

---

## TO SHOW THE REGISTERED USERS IN THE DATABASE

### Open Django Shell
```sh
python manage.py shell
```

### Import the User Model
```python
from django.contrib.auth.models import User
```

### Show All Registered Usernames
```python
usernames = User.objects.values_list('username', flat=True)
print(list(usernames))
```

### Show All Usernames Along with Emails
```python
users = User.objects.values('username', 'email')
for user in users:
    print(user)
```

### Exit the Shell
```sh
exit()
```

---

## TO DELETE ALL THE REGISTERED USERS IN THE DATABASE

### Open Django Shell
```sh
python manage.py shell
```

### Import the User Model
```python
from django.contrib.auth.models import User
```

### Delete an Existing User
```python
username = "your_existing_username"

try:
    user = User.objects.get(username=username)
    user.delete()
    print(f"User '{username}' deleted successfully!")
except User.DoesNotExist:
    print("User does not exist.")
```

### Exit the Shell
```sh
exit()
```

---

## CREATING A SUPERUSER

### Create a Superuser (Admin)
```sh
python manage.py createsuperuser
```

### Assign Admin Privileges to a User
```python
from django.contrib.auth.models import User

# Get the user you want to make an admin
user = User.objects.get(username="Admin")

# Grant admin privileges
user.is_staff = True  # Allows access to the admin panel
user.is_superuser = True  # Gives full control like a superuser
user.save()

print(f"User {user.username} is now an admin!")
```

---

## Requisites
```sh
pip install django openpyxl
```

### Create `forms.py` in Your `Macro` App
