from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from datetime import datetime
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os, random,json, xlrd, math
from .utils import process_hrl_files,is_file_locked
from django.core.files import File
from io import BytesIO
import pandas as pd
import shutil,os, re, traceback, ntpath
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from .models import UploadedExcel, StoredExcel
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .forms import ExcelUploadForm
from django.utils.timezone import now
from .html_merge import merge_files_in_batches
from .forms import HTMLMergeForm
from django.http import FileResponse, Http404, HttpResponse
from collections import defaultdict
User = get_user_model()
# Function to check if user is admin
def is_admin(user):
    return user.is_superuser  # Only allow superusers

# Admin access view
@login_required
def admin_access_view(request):
    users = User.objects.all()
    return render(request, 'admin_access.html', {
        'users': users,
        'user': request.user,
    })

# Make a user an admin
@login_required
@user_passes_test(is_admin)
def make_admin(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    messages.success(request, f"{user.username} is now an admin!")
    return redirect('admin_dash')

# Delete a user
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if not user.is_superuser:  # Prevent deletion of admins
        user.delete()
        messages.success(request, "User deleted successfully!")
    else:
        messages.error(request, "Cannot delete an admin user!")
    return redirect('admin_dash')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # 🔁 redirect to your custom dashboard
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')  # your custom login template

def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def dashboard(request):
    generated_files = UploadedExcel.objects.all()
    return render(request, "dashboard.html", {"generated_files": generated_files})


def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Signup successful! Please log in.")
        return redirect('login')  # Redirect to the login page

    return render(request, 'signup.html')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            try:
                otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
                
                # Store OTP in session
                request.session["otp"] = otp
                request.session["email"] = email
                print("Stored OTP:", otp)  # Debugging

                # Send OTP via email
                send_mail(
                    "Password Reset OTP",
                    f"Your OTP for password reset is {otp}",
                    "saransuresh01s@gmail.com",  
                    [email],
                    fail_silently=False,
                )

                return redirect("verify_otp")  # Check if URL exists in urls.py

            except Exception as e:
                print("Email sending error:", str(e))  # Debugging
                return render(request, "forgot_password.html", {"error": f"Error: {str(e)}"})

    return render(request, "forgot_password.html")

# def forgot_password(request):
#     if request.method == 'POST':
#         print("✅ POST request received.")  # Debug
#         email = request.POST['email']
#         print(f"✅ Email entered: {email}")  # Debug
        
#         try:
#             user = User.objects.get(email=email)
#             print("✅ User found in database.")  # Debug
            
#             otp = random.randint(100000, 999999)
#             request.session['otp'] = otp
#             request.session['email'] = email
#             print(f"✅ Generated OTP: {otp}")  # Debug

#             # Debug email sending
#             send_mail(
#                 'Your OTP Code',
#                 f'Your OTP code is {otp}',
#                 'saransuresh01s@gmail.com',
#                 [email],
#                 fail_silently=False,
#             )
#             print("✅ Email sent successfully.")  # Debug
            
#             return redirect('verify_otp')

#         except User.DoesNotExist:
#             print("❌ User not found.")  # Debug
#             return render(request, 'forgot_password.html', {'error': 'Email not found.'})
#     print("❌ Request was not POST")
#     return render(request, 'forgot_password.html')

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")

        if entered_otp == stored_otp:
            del request.session["otp"]  
            return redirect('reset_password')  # Redirect to reset password page
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "verify_otp.html")

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        print("OTP function called")
        email = request.POST.get("email")
        print("Email received:", email)

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store the OTP in session
        request.session["otp"] = otp
        request.session["email"] = email
        print("Stored OTP in session:", otp)  # Debugging

        # Send OTP via email
        try:
            send_mail(
                "Your OTP Code",
                f"Your OTP is {otp}. Do not share it with anyone.",
                "saransuresh01s@gmail.com",
                [email],
                fail_silently=False,
            )
            print("OTP sent successfully")  # Debugging
            return JsonResponse({"message": "OTP sent successfully"})
        except Exception as e:
            print("Error sending email:", str(e))  # Debugging
            return JsonResponse({"error": "Failed to send OTP"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'reset_password.html')

        # Get email from session
        email = request.session.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                
                # Reset the password
                user.set_password(password)
                user.save()

                # Clear the session to prevent unintended access to the reset flow
                del request.session['email'] 

                messages.success(request, "Password reset successful! You can now log in.")
                return redirect('login')  # Redirect to login page after successful reset
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
                return redirect('forgot_password')  # Redirect back to forgot password if no user found

    # If request method is not POST, render the reset password page
    return render(request, 'reset_password.html')

def is_excel_file(file):
    return file.name.endswith(".xlsx") or file.name.endswith(".xls")

@login_required
def upload_excel(request):
    form = ExcelUploadForm()
    preview_html = None
    message = None
    version_choice = "latest"
    folder_name = "default"

    if request.method == "POST" and request.FILES.get("file"):
        form = ExcelUploadForm(request.POST, request.FILES)
        uploaded_file = request.FILES["file"]
        folder_name = request.POST.get("folder_name", "default").strip()
        version_choice = request.POST.get("version", "latest").strip()

        user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id), folder_name)
        os.makedirs(user_folder, exist_ok=True)

        # Check for existing file in the same folder
        uploaded_files_qs = UploadedExcel.objects.filter(
            uploaded_by=request.user,
            folder_name=folder_name,
            file_name=uploaded_file.name
        )

        if uploaded_files_qs.exists():
            if version_choice == "latest":
                uploaded_files_qs.delete()
            elif version_choice == "oldest":
                messages.info(request, "Oldest version already exists. Skipping upload.")
                return redirect("upload_excel")

        if not is_excel_file(uploaded_file):
            messages.error(request, "Invalid file format. Please upload an Excel file (.xlsx or .xls).")
            return redirect("upload_excel")

        try:
            file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
            in_memory_file = BytesIO(uploaded_file.read())

            if file_ext == ".xlsx":
                excel_data = pd.read_excel(in_memory_file, sheet_name=None, engine="openpyxl")
            else:
                excel_data = pd.read_excel(in_memory_file, sheet_name=None, engine="xlrd")

            json_data = {}
            for sheet_name, df in excel_data.items():
                df_cleaned = df.loc[:, ~df.columns.str.contains("^Unnamed")]
                df_cleaned = df_cleaned.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
                json_data[sheet_name] = {
                    "columns": list(df_cleaned.columns),
                    "data": df_cleaned.to_dict(orient="records")
                }

            def clean_json(data):
                if isinstance(data, dict):
                    return {k: clean_json(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_json(v) for v in data]
                elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
                    return None
                else:
                    return data

            cleaned_data = clean_json(json_data)
            safe_json = json.dumps(cleaned_data, default=str)

            stored_excel, _ = StoredExcel.objects.get_or_create(
                user=request.user,
                folder_name=folder_name,
                data=safe_json
            )
            # Update existing stored_excel if newly uploaded
            stored_excel.data = safe_json
            stored_excel.save()

            UploadedExcel.objects.create(
                excel_file=uploaded_file,
                uploaded_by=request.user,
                folder_name=folder_name,
                file_name=uploaded_file.name,
                timestamp=now(),
                status="Processed",
                stored_excel=stored_excel
            )

            messages.success(request, "File uploaded and data saved successfully!")
            return redirect("upload_excel")

        except Exception as e:
            print("❌ Error processing Excel file:", e)
            messages.error(request, f"Error processing Excel file: {e}")
            return redirect("upload_excel")

    # === GET request ===

    uploaded_files = UploadedExcel.objects.filter(uploaded_by=request.user).order_by("-timestamp")
    stored_excels = StoredExcel.objects.filter(user=request.user).order_by("-uploaded_at")
    folder_names = UploadedExcel.objects.filter(uploaded_by=request.user).values_list('folder_name', flat=True).distinct()

    # Handle file dropdown selection
    selected_folder_name = request.GET.get("selected_folder_name")
    selected_file_id = request.GET.get("selected_file_id")

    selected_folder_uploads = None
    if selected_folder_name:
        selected_folder_uploads = UploadedExcel.objects.filter(
            uploaded_by=request.user,
            folder_name=selected_folder_name
        ).order_by("-timestamp")

    selected_file = None
    if selected_folder_name and selected_file_id:
        try:
            selected_file = UploadedExcel.objects.get(id=selected_file_id)
        except UploadedExcel.DoesNotExist:
            selected_file = None

    # Group uploads by folder
    uploads_grouped_by_folder = defaultdict(list)
    for upload in UploadedExcel.objects.filter(uploaded_by=request.user).order_by("-timestamp"):
        uploads_grouped_by_folder[upload.folder_name].append(upload)

    return render(request, "upload_excel.html", {
        "form": form,
        "folder_name": folder_name,
        "preview_html": preview_html,
        "message": message,
        "uploads_grouped_by_folder": dict(uploads_grouped_by_folder),
        "stored_excels": stored_excels,
        "version_choice": version_choice,
        "recent_uploads": uploaded_files,
        "folder_names": folder_names,
        "selected_folder_name": selected_folder_name,
        "selected_file_id": selected_file_id,
        "selected_file": selected_file,
        "selected_folder_uploads": selected_folder_uploads,
    })


@login_required
def view_excel_sheet(request, stored_excel_id):
    stored_excel = get_object_or_404(StoredExcel, id=stored_excel_id, user=request.user)

    # ✅ Safely parse JSON only if it's a string
    sheet_data = stored_excel.data
    if isinstance(sheet_data, str):
        try:
            sheet_data = json.loads(sheet_data)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in StoredExcel {stored_excel_id}")
            sheet_data = {}
    elif not isinstance(sheet_data, dict):
        print(f"❌ Unexpected type for sheet_data in StoredExcel {stored_excel_id}: {type(sheet_data)}")
        sheet_data = {}

    sheet_names = list(sheet_data.keys()) if isinstance(sheet_data, dict) else []
    selected_sheet = request.GET.get("sheet") or (sheet_names[0] if sheet_names else None)

    table_html = "<p class='text-danger'>No sheet selected.</p>"

    if selected_sheet and selected_sheet in sheet_data:
        sheet_content = sheet_data[selected_sheet]

        # Handle both old and new formats
        if isinstance(sheet_content, list):
            df = pd.DataFrame(sheet_content)
        else:
            columns = sheet_content.get("columns") or []
            data = sheet_content.get("data") or []
            df = pd.DataFrame(data, columns=columns)

        if df.empty and list(df.columns):
            table_html = df.head(0).to_html(classes="table table-bordered table-striped", index=False)
        elif not df.empty:
            table_html = df.to_html(classes="table table-bordered table-striped", index=False)
        else:
            table_html = "<p class='text-danger'>The selected sheet has no headers or data.</p>"

    # Debug info
    print("📄 Sheets available:", sheet_names)
    print("✅ Selected sheet:", selected_sheet)
    print("📦 Sheet data keys:", list(sheet_data.keys()) if isinstance(sheet_data, dict) else "N/A")

    return render(request, "view_excel_sheet.html", {
        "table_html": table_html,
        "stored_excel": stored_excel,
        "sheet_names": sheet_names,
        "selected_sheet": selected_sheet
    })

    
@login_required
def view_excel_sheet_redirect(request):
    excel_id = request.GET.get("excel_id")
    if excel_id:
        return redirect("view_excel_sheet", stored_excel_id=excel_id)
    else:
        # Optionally handle the case where no ID was selected
        return redirect("upload_excel")  # or render a warning message


@login_required
def run_dmt_filtration_view(request, file_id):
    session_file_id = request.session.get("file_id")
    if str(file_id) != str(session_file_id):
        messages.error(request, "Mismatch between selected file and session data.")
        return redirect("dmt_results_prompt", file_id=file_id)
    uploaded_file = get_object_or_404(UploadedExcel, pk=file_id, uploaded_by=request.user)

    if not uploaded_file.excel_file:
        messages.error(request, "This uploaded file has no associated Excel file.")
        return redirect('dmt_results_prompt', file_id=file_id)

    input_excel_path = uploaded_file.excel_file.path


    # ✅ Pull version_choice from session, not GET — session is set in dmt_results_prompt_view
    version_choice = request.session.get('version_choice', 'all')
    print(f"🔧 Starting HRL filtration | Version selected: {version_choice}")

    config_root = os.path.join(settings.MEDIA_ROOT, "uploads", str(request.user.id), uploaded_file.folder_name)

    try:
        # ✅ Perform filtration
        result_path = process_hrl_files(input_excel_path, config_root, version_choice)

        # ✅ Create user-specific folder if needed
        folder_name = uploaded_file.folder_name.strip()
        user_upload_dir = os.path.join('uploads', str(request.user.id), folder_name)
        full_user_upload_dir = os.path.join(settings.MEDIA_ROOT, user_upload_dir)
        os.makedirs(full_user_upload_dir, exist_ok=True)

        # ✅ Determine destination for filtered file
        filtered_filename = os.path.basename(result_path)
        relative_path = os.path.join(user_upload_dir, filtered_filename)

        # ✅ Save to Django-managed media
        with open(result_path, 'rb') as f:
            saved_path = default_storage.save(relative_path, File(f))

        # ✅ Log new UploadedExcel
        filtered_instance = UploadedExcel.objects.create(
            folder_name=folder_name,
            file_name=filtered_filename,
            excel_file=saved_path,
            uploaded_by=uploaded_file.uploaded_by,
            status='Filtered',
            stored_excel=uploaded_file.stored_excel
        )

        # ✅ Generate HTML preview of filtered Excel
        xls = pd.ExcelFile(result_path)
        tables_html = {}
        total_count = approved_count = pending_count = 0
        approved_percent = pending_percent = 0
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            tables_html[sheet_name] = df.to_html(classes="table table-bordered table-sm", index=False)
            
            if 'HRL Available?' in df.columns:
                hrl_series = df['HRL Available?'].astype(str).str.strip().str.lower()
                total_count += len(df)
                approved_count += (hrl_series == 'hrl found').sum()
                pending_count += (hrl_series != 'hrl found').sum()
                
        approved_percent = round((approved_count / total_count) * 100, 2) if total_count else 0
        pending_percent = round((pending_count / total_count) * 100, 2) if total_count else 0
        print("Approved Count:", approved_count)
        print("Approved Percent:", approved_percent)

        context = {
            "download_ready": True,
            "filtered_filename": filtered_filename,
            "tables_html": tables_html,
            "download_url": filtered_instance.excel_file.url,
            "total_count": total_count,
            "approved_count": approved_count,
            "pending_count": pending_count,
            "approved_percent": approved_percent,
            "pending_percent": pending_percent,
        }

        return render(request, "dmt_filter.html", context)

    except Exception as e:
        print("Traceback:", traceback.format_exc())
        messages.error(request, f"Error during HRL filtration: {str(e)}")
        return redirect("dmt_results_prompt", file_id=file_id)
    
    
def dmt_results_prompt_view(request, file_id):
    upload = get_object_or_404(UploadedExcel, id=file_id, uploaded_by=request.user)
    selected_folder = request.session.get("selected_folder_name")

    print(f"📦 File selected: {upload.file_name} from folder {upload.folder_name}")
    print(f"🌐 Session folder: {selected_folder}")

    # ❌ Block manual tampering (accessing file from other folder)
    if selected_folder and upload.folder_name != selected_folder:
        messages.error(request, "This file does not belong to the selected folder.")
        return redirect("upload_excel")

    if request.method == "POST":
        posted_file_id = request.POST.get("file_id")
        version_choice = request.POST.get("version_choice")

        if posted_file_id != str(upload.id):
            messages.error(request, "Mismatch in file ID. Please try again.")
            return redirect("upload_excel")

        if version_choice not in ["latest", "oldest", "all"]:
            messages.error(request, "Please select a valid version option.")
            return redirect("dmt_results_prompt", file_id=file_id)

        return redirect("dmt_filtration_handler", file_id=file_id)

    return render(request, "dmt_results_prompt.html", {"upload": upload})


@login_required
def download_filtered_file(request):
    filtered_file_path = request.session.get("filtered_file_path")
    print("Filtered file path from session:", filtered_file_path)

    if not filtered_file_path:
        return HttpResponse("Path not set in session.", status=400)

    if not os.path.exists(filtered_file_path):
        return HttpResponse(f"File does not exist at: {filtered_file_path}", status=404)

    return FileResponse(open(filtered_file_path, "rb"), as_attachment=True, filename=os.path.basename(filtered_file_path))


def download_file(request, file_id):
    upload = get_object_or_404(UploadedExcel, id=file_id, uploaded_by=request.user)
    file_path = upload.excel_file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=upload.file_name)
    except FileNotFoundError:
        raise Http404("File not found.")

def delete_file(request, file_id):
    upload = get_object_or_404(UploadedExcel, id=file_id, uploaded_by=request.user)
    file_path = upload.excel_file.path

    upload.delete()
    if os.path.exists(file_path):
        os.remove(file_path)

    messages.success(request, "File deleted successfully.")
    return redirect("upload_excel")


def html_merge_view(request):
    final_output_folder = None

    if request.method == "POST":
        batch_size = request.POST.get("batch_size")
        run_id = request.POST.get("output_name", "").strip()

        if not run_id:
            messages.error(request, "Output folder name cannot be empty.")
        elif not batch_size:
            messages.error(request, "Batch size is required.")
        else:
            try:
                batch_size = int(batch_size)
                uploaded_files = request.FILES.getlist("folder")

                if not uploaded_files:
                    messages.error(request, "No files received.")
                    return render(request, "merge_html.html", {})

                # Save uploaded files to temp folder
                input_folder = os.path.join(settings.MEDIA_ROOT, "temp_upload")
                os.makedirs(input_folder, exist_ok=True)

                for f in uploaded_files:
                    file_path = os.path.join(input_folder, f.name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb+") as dest:
                        for chunk in f.chunks():
                            dest.write(chunk)

                # Final output path using user-defined folder
                output_folder = os.path.join(settings.MEDIA_ROOT, run_id)
                os.makedirs(output_folder, exist_ok=True)

                # Merge logic
                merge_files_in_batches(
                    input_folder=input_folder,
                    base_output_folder=settings.MEDIA_ROOT,
                    num_files=len(uploaded_files),
                    batch_size=batch_size,
                    run_id=run_id
                )

                messages.success(request, f"Merge complete. Output saved in: {run_id}/")
                final_output_folder = run_id

            except Exception as e:
                messages.error(request, f"Merge failed: {str(e)}")

    return render(request, "merge_html.html", {
        "final_output_folder": final_output_folder
    })



