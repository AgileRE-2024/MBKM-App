from django.contrib import admin
from mbkmapp.models import *

# Register your models here.

class ProgramAdmin(admin.ModelAdmin):
    list_display = ['nama_program', 'penyelenggara', 'kuota']
    search_fields = ['nama_program', 'penyelenggara', 'kuota']  
    list_per_page = 8


class MataKuliahInline(admin.TabularInline):
    model = Program.mata_kuliah.through  
    extra = 1  

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('nama_program', 'penyelenggara', 'durasi', 'kuota', 'sks')
    search_fields = ('nama_program', 'penyelenggara')
    filter_horizontal = ('mata_kuliah',)  

class MataKuliahAdmin(admin.ModelAdmin):
    list_display = ('kode_mk','nama_mk', 'sks_mk')
    search_fields = ('nama_mk',)
    inlines = [MataKuliahInline] 


class KonversiAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'program', 'status', 'get_ipk', 'created_at')  # Ganti 'ipk' ke 'get_ipk'
    search_fields = ('mahasiswa__user__username', 'program__nama_program', 'status')  # Sesuaikan search fields
    list_filter = ('status', 'program')
    filter_horizontal = ('matkul_konversi',)
    readonly_fields = ('created_at', 'updated_at')

    def get_ipk(self, obj):
        if obj.mahasiswa and obj.mahasiswa.ipk_mhs is not None:
            return f"{obj.mahasiswa.ipk_mhs:.2f}"
        return '-'
    get_ipk.short_description = 'IPK Mahasiswa'  # Nama yang akan ditampilkan di kolom admin
    get_ipk.admin_order_field = 'mahasiswa__ipk_mhs'  # Untuk enable sorting

    def get_search_results(self, request, queryset, search_term):
        """Override metode ini untuk memperluas pencarian"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        try:
            # Mencoba mencari berdasarkan IPK jika search_term adalah angka
            if search_term.replace('.', '').isdigit():
                ipk_value = float(search_term)
                queryset |= self.model.objects.filter(mahasiswa__ipk_mhs=ipk_value)
        except ValueError:
            pass
        
        return queryset, use_distinct

# Mendaftarkan model di admin site
admin.site.register(Program, ProgramAdmin)
admin.site.register(MataKuliah, MataKuliahAdmin)

admin.site.register(Mahasiswa)
admin.site.register(Dosen)
admin.site.register(Konversi, KonversiAdmin)
admin.site.register(Loa)