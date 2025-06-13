from django.urls import path
from .views import user_login, user_logout, dashboard, user_signup, forgot_password, verify_otp, reset_password,upload_excel,download_file,delete_file,run_dmt_filtration_view,download_filtered_file,dmt_results_prompt_view,admin_access_view,html_merge_view,dmt_filter_view,get_progress_status,check_filter_ready,cancel_filtration
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
urlpatterns = [
    path('', user_login, name='login'),  # Default page
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('signup/', user_signup, name='signup'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    path("admin-access/", admin_access_view, name="admin_access"),
    path("no-access/", lambda request: render(request, "not_authorized.html"), name="no_access"),
    path('download/<int:file_id>/', download_file, name='download_file'),
    path('delete/<int:file_id>/', delete_file, name='delete_file'),
    path('run-dmt-filtration/<int:file_id>/', run_dmt_filtration_view, name='dmt_filtration_handler'),
    path('download-filtered-file/',download_filtered_file, name='download_filtered_excel'),
    path("dmt/prompt/<int:file_id>/", dmt_results_prompt_view, name="dmt_results_prompt"),
    path("merge-html/", html_merge_view, name="merge_html"),
    path("dmt/filter/<int:file_id>/", dmt_filter_view, name="dmt_filter"),
    path('progress/<int:file_id>/', get_progress_status, name='get_progress'),
    path("check-filter-ready/<int:file_id>/",check_filter_ready, name="check_filter_ready"),
    path("cancel-filtration/<int:file_id>/", cancel_filtration, name="cancel_filtration"),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)