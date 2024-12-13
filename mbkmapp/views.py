from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from mbkmapp.forms import *

# Create your views here.

import logging

# Configure a logger for debugging
logger = logging.getLogger(__name__)


def landing(request):
    return render(request,"landing.html")

def daftar_program(request):
    # Mengurutkan programs berdasarkan created_at terbaru
    programs = Program.objects.all().order_by('-created_at')
    return render(request, 'programs.html', {'programs': programs})

def register_mahasiswa(request):
    if request.method == 'POST':
        form = MahasiswaRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = MahasiswaRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def register_dosen(request):
    if request.method == 'POST':
        form = DosenRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = DosenRegistrationForm()
    
    return render(request, 'register-dosen.html', {'form': form})

def register_timkonversi(request):
    if request.method == 'POST':
        form = TimKonversiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = TimKonversiForm()
    
    return render(request, 'register-timkonversi.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing')  
            else:
                form.add_error(None, 'Username atau password salah.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    request.session.flush() 
    messages.success(request, 'Successfully logged out!')
    return redirect('landing') 

# Di views.py
def detail_program(request, id):
    program = get_object_or_404(Program, id=id)
    
    rincian_kegiatan_list = program.rincian_kegiatan.split(";")
    kriteria_peserta_list = program.kriteria_peserta.split(";")
    mata_kuliah_list = program.mata_kuliah.all().order_by('nama_mk')
    
    # Inisialisasi variabel untuk status pendaftaran
    konversi_mahasiswa = None
    if request.user.is_authenticated and hasattr(request.user, 'mahasiswa'):
        konversi_mahasiswa = Konversi.objects.filter(
            mahasiswa=request.user.mahasiswa,
            program=program
        ).first()

    context = {
        'program': program,
        'rincian_kegiatan': rincian_kegiatan_list,
        'kriteria_peserta': kriteria_peserta_list,
        'mata_kuliah_list': mata_kuliah_list,
        'konversi_mahasiswa': konversi_mahasiswa,
    }
    return render(request, 'detail-program.html', context)


def form_semester(request, id):
    program = get_object_or_404(Program, id=id)
    
    mahasiswa = get_object_or_404(Mahasiswa, user=request.user)

    if request.method == "POST":
        form = FormSemester(request.POST, instance=mahasiswa)  
        if form.is_valid():
            form.save()  
            return redirect('download-form', id=program.id)  
    else:
        form = FormSemester(instance=mahasiswa)

    context = {
        'form': form,
        'program': program,  
    }

    return render(request, 'form-semester.html', context)

def download_form(request, id):
    program = get_object_or_404(Program, id=id)

    context = {
        'program': program,  
    }

    return render(request,"form-download.html", context)

import logging
logger = logging.getLogger(__name__)

@login_required
def form_konversi(request, id):
    try:
        program = get_object_or_404(Program, id=id)
        mahasiswa = get_object_or_404(Mahasiswa, user=request.user)
        dosen_wali = mahasiswa.dosen

        # Cek existing konversi
        existing_konversi = Konversi.objects.filter(
            mahasiswa=mahasiswa,
            program=program
        ).first()

        # Cek apakah bisa edit
        can_edit = True
        if existing_konversi:
            # Jika konversi sudah diterima, cek status LOA
            if existing_konversi.status == 'diterima':
                try:
                    loa = existing_konversi.loa
                    # Hanya bisa edit jika LOA belum ada, sedang diverifikasi, atau ditolak
                    can_edit = not loa or loa.status in ['sedang_diverifikasi', 'ditolak']
                except Loa.DoesNotExist:
                    # Jika LOA belum ada, masih bisa edit
                    can_edit = True
            else:
                # Jika konversi belum diterima, tidak bisa edit
                can_edit = False

        if not can_edit:
            messages.error(request, "Tidak dapat mengedit data konversi pada status ini.")
            return redirect('status_daftar', id=existing_konversi.id)

        if request.method == "POST":
            form = FormKonversi(
                request.POST, 
                request.FILES,
                instance=existing_konversi if existing_konversi else None,
                program=program,
                mahasiswa=mahasiswa
            )
            
            if form.is_valid():
                konversi = form.save(commit=False)
                konversi.program = program
                konversi.dosen_wali = dosen_wali
                konversi.mahasiswa = mahasiswa
                
                # Jika ini konversi baru
                if not existing_konversi:
                    konversi.status = 'sedang_diverifikasi'
                
                konversi.save()
                form.save_m2m()

                # Buat verifikasi baru jika belum ada
                if not existing_konversi:
                    verifikasi = Verifikasi.objects.create(
                        dosen_wali=dosen_wali,
                        status='sedang_diverifikasi'
                    )
                    konversi.verifikasi = verifikasi
                    konversi.save()

                messages.success(request, "Data konversi berhasil diperbarui!")
                return redirect('status_daftar', id=konversi.id)
            else:
                messages.error(request, "Gagal menyimpan data. Periksa kembali form anda.")
        else:
            form = FormKonversi(
                instance=existing_konversi if existing_konversi else None,
                program=program,
                mahasiswa=mahasiswa
            )

        context = {
            'form': form,
            'program': program,
            'mahasiswa': mahasiswa,
            'is_edit': existing_konversi is not None,
            'can_edit': can_edit
        }

        return render(request, 'form-konversi.html', context)

    except Exception as e:
        logger.error(f"Error in form_konversi: {str(e)}")
        messages.error(request, "Terjadi kesalahan saat memproses form.")
        return redirect('daftar_program')




def status_daftar(request, id):
    konversi = get_object_or_404(Konversi, id=id)
    loa = konversi.loa if hasattr(konversi, 'loa') else None
    can_edit = konversi.status != 'diterima'  # Tambahkan flag untuk mengecek apakah bisa diedit

    if request.method == "POST" and konversi.status == "diterima":
        # Create a new Loa instance only if it doesn't exist
        if not loa:
            loa = Loa(konversi=konversi)

        # Initialize the form with the instance (which may be new or existing)
        form = LoaForm(request.POST, request.FILES, instance=loa)

        if form.is_valid():
            # Save the form to the database
            loa = form.save(commit=False)  # Get the instance without saving yet
            loa.konversi = konversi  # Set the konversi ForeignKey
            loa.save()  # Now save the instance to the database
            messages.success(request, "LOA berhasil diunggah.")
            return redirect('status_daftar', id=konversi.id)
    else:
        form = LoaForm(instance=loa)

    context = {
        'konversi': konversi,
        'loa': loa,
        'form': form,
        'can_edit': can_edit,  # Tambahkan ke context
    }
    return render(request, "status.html", context)



def program_saya(request):
    try:
        mahasiswa = get_object_or_404(Mahasiswa, user=request.user)
        konversi_list = Konversi.objects.filter(mahasiswa=mahasiswa).order_by('-created_at')

        context = {
            'konversi_list': konversi_list,
        }
        
        return render(request, 'program_saya.html', context)
    except Mahasiswa.DoesNotExist:
        messages.error(request, "Akun Anda tidak terkait dengan data mahasiswa.")
        return redirect('landing')
    except Exception as e:
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect('landing')


@login_required
def dosen_program_mahasiswa(request):
    try:
        dosen = request.user.dosen  # Get the logged-in dosen
        konversi_list = Konversi.objects.filter(dosen_wali=dosen)
    except Dosen.DoesNotExist:
        messages.error(request, "Anda bukan dosen.")
        return redirect('landing')

    return render(request, 'dosen_program_mahasiswa.html', {'konversi_list': konversi_list})


@login_required
def accept_konversi(request, konversi_id):
    konversi = get_object_or_404(Konversi, id=konversi_id, dosen_wali=request.user.dosen)
    konversi.status = 'diterima'
    konversi.save()
    messages.success(request, "Konversi berhasil diterima.")
    return redirect('dosen_program_mahasiswa')

@login_required
def reject_konversi(request, konversi_id):
    konversi = get_object_or_404(Konversi, id=konversi_id, dosen_wali=request.user.dosen)
    konversi.status = 'ditolak'
    konversi.save()
    messages.success(request, "Konversi berhasil ditolak.")
    return redirect('dosen_program_mahasiswa')

@login_required
def verifikasi_loa(request):
    try:
        tim_konversi = request.user.timkonversi
        
        loa_list = Loa.objects.select_related('konversi').all()
        
        context = {
            'loa_list': loa_list,
            'STATUS_CHOICES': dict(Loa.STATUS_CHOICES)
        }
        
        return render(request, 'verifikasi-loa.html', context)
        
    except TimKonversi.DoesNotExist:
        messages.error(request, "Anda bukan Tim Konversi.")
        return redirect('landing')

@login_required
def accept_loa(request, loa_id):
    loa = get_object_or_404(Loa, id=loa_id)
    loa.status = 'diterima'
    loa.save()
    messages.success(request, "loa berhasil diterima.")
    return redirect('verifikasi_loa')

@login_required
def reject_loa(request, loa_id):
    loa = get_object_or_404(Loa, id=loa_id)
    loa.status = 'ditolak'
    loa.save()
    messages.success(request, "loa berhasil ditolak.")
    return redirect('verifikasi_loa')