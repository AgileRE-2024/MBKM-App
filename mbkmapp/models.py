from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Program(models.Model):
    nama_program = models.CharField(max_length=255)
    penyelenggara = models.CharField(max_length=255)
    durasi = models.CharField(max_length=64)
    kuota = models.PositiveIntegerField()
    deskripsi = models.TextField()
    rincian_kegiatan = models.TextField()
    kriteria_peserta = models.TextField()
    sks = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    mata_kuliah = models.ManyToManyField('MataKuliah', related_name='programs')

    def __str__(self):
        return self.nama_program
    
class MataKuliah(models.Model):
    kode_mk = models.CharField(max_length=20, unique=True, null = True)
    nama_mk = models.CharField(max_length=255)
    sks_mk = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_mk


class Dosen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=50, unique=True)
    universitas = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    office_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.nip}"

class TimKonversi(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    no_timkonversi = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
    
def validate_ipk(value):
    if value < 0.0 or value > 4.0:
        raise ValidationError('IPK harus antara 0.0 hingga 4.0.')

class Mahasiswa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True)
    universitas = models.CharField(max_length=100)
    nim = models.CharField(max_length=50)
    semester = models.IntegerField(null=True, blank=True)
    ipk_mhs = models.FloatField(validators=[validate_ipk], null=True)
    dosen = models.ForeignKey(Dosen, on_delete=models.SET_NULL, null=True, related_name="mahasiswa")

    def __str__(self):
        return self.user.username
    
class Konversi(models.Model):
    STATUS_CHOICES = [
        ('sedang_diverifikasi', 'Sedang Diverifikasi'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
    ]
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE, null=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sedang_diverifikasi')
    matkul_konversi = models.ManyToManyField(MataKuliah, related_name="konversi")
    document = models.FileField(upload_to='documents/', null=True, blank=True)
    dosen_wali = models.ForeignKey(Dosen, on_delete=models.SET_NULL, null=True, related_name="konversi_mahasiswa")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, related_name="konversi_program")
    verifikasi = models.ForeignKey('Verifikasi', on_delete=models.SET_NULL, null=True, related_name="konversi")

    @property
    def can_edit(self):
        """
        Mengecek apakah konversi bisa diedit:
        - Konversi harus sudah diterima dosen
        - LOA belum ada atau belum diterima
        """
        if self.status == 'diterima':
            try:
                loa = self.loa
                return loa.status in ['sedang_diverifikasi', 'ditolak']
            except Loa.DoesNotExist:
                return True
        return False
class Verifikasi(models.Model):
    dosen_wali = models.ForeignKey(Dosen, on_delete=models.CASCADE, related_name='dosen_verifikasi')
    tanggal_verifikasi = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Konversi.STATUS_CHOICES)
    catatan = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Verifikasi oleh {self.dosen_wali.user.username} pada {self.tanggal_verifikasi}"

class Loa(models.Model):
    STATUS_CHOICES = [
        ('sedang_diverifikasi', 'Sedang Diverifikasi'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
    ]
    konversi = models.OneToOneField(Konversi, on_delete=models.CASCADE, related_name="loa")
    loa_file = models.FileField(upload_to='loa_files/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sedang_diverifikasi')
    catatan_verifikasi = models.TextField(null=True, blank=True)
    tim_konversi = models.ForeignKey(TimKonversi, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LOA {self.id} - Konversi ID: {self.konversi.id} - Status: {self.status}"

