"""
URL configuration for MBKM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MBKM import settings
from django.conf.urls.static import static
from mbkmapp.views import *
from mbkmapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name="landing"),
    path('programs/<int:id>/tambah-konversi/data-konversi', form_konversi, name="form_konversi"),
    path('programs/<int:id>/tambah-konversi/data-semester', form_semester, name="form_semester"),
    path('programs/<int:id>/tambah-konversi/download-form', download_form, name="download-form"),
    path('program-saya/<int:id>/tambah-konversi/status_daftar', status_daftar, name="status_daftar"),
    path('register-mahasiswa/', register_mahasiswa, name="register_mahasiswa"),
    path('register-dosen/', register_dosen, name="register_dosen"),
    path('register-timkonversi/', register_timkonversi, name="register_timkonversi"),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    path('programs/', daftar_program, name='daftar_program'),
    path('programs/<int:id>/', detail_program, name='detail_program'), 
    path('program-saya/', program_saya, name='program_saya'),
    path('verifikasi-loa/', verifikasi_loa, name='verifikasi_loa'),
    path('dosen/program/', views.dosen_program_mahasiswa, name='dosen_program_mahasiswa'),
    path('dosen/program/<int:konversi_id>/accept/', views.accept_konversi, name='accept_konversi'),
    path('dosen/program/<int:konversi_id>/reject/', views.reject_konversi, name='reject_konversi'),
    path('timkonversi/program/<int:loa_id>/accept/', views.accept_loa, name='accept_loa'),
    path('timkonversi/program/<int:loa_id>/reject/', views.reject_loa, name='reject_loa'),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)