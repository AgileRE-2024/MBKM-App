from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from mbkmapp.models import *

class FormKonversi(ModelForm):
    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop('program', None)
        self.mahasiswa = kwargs.pop('mahasiswa', None)
        super(FormKonversi, self).__init__(*args, **kwargs)

        if self.program:
            self.fields['matkul_konversi'].queryset = self.program.mata_kuliah.all()
            
        # Jika ini edit form, document tidak required
        if self.instance.pk:
            self.fields['document'].required = False

    def clean(self):
        cleaned_data = super().clean()
        matkul_konversi = cleaned_data.get('matkul_konversi')
        document = cleaned_data.get('document')

        # Validasi IPK
        if self.mahasiswa and self.mahasiswa.ipk_mhs:
            if self.mahasiswa.ipk_mhs < 2.5:
                raise forms.ValidationError("IPK Anda harus minimal 2.5 untuk melanjutkan pendaftaran.")

        # Validasi total SKS
        if matkul_konversi:
            total_sks = sum(matkul.sks_mk for matkul in matkul_konversi)
            if total_sks > self.program.sks:
                raise forms.ValidationError(
                    f"Total SKS mata kuliah yang dipilih ({total_sks}) "
                    f"melebihi batas SKS program ({self.program.sks})."
                )

        # Validasi document hanya untuk konversi baru
        if not self.instance.pk and not document:
            raise forms.ValidationError("Dokumen pendukung harus diunggah untuk pendaftaran baru.")
        
        return cleaned_data

    class Meta:
        model = Konversi
        fields = ['matkul_konversi', 'document']
        labels = {
            'matkul_konversi': 'Mata Kuliah Konversi',
            'document': 'Dokumen Pendukung',
        }
        
class FormSemester(ModelForm):
    class Meta:
        model = Mahasiswa
        fields = ['semester']
        labels = {
            'semester' : 'Semester',
            }
        widgets = {
            'semester': forms.TextInput(attrs={'class': 'form-control'}),

        }
    def __init__(self, *args, **kwargs):
        super(FormSemester, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = self.Meta.labels[field_name]


class MahasiswaRegistrationForm(UserCreationForm):
    # Field tambahan untuk model Mahasiswa
    universitas = forms.CharField(max_length=100)
    nim = forms.CharField(max_length=50)
    semester = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Semester',
        'class': 'form-control'
    }))
    ipk_mhs = forms.FloatField(required=True, widget=forms.NumberInput(attrs={
        'placeholder': 'IPK',
        'class': 'form-control'
    }))
    dosen = forms.ModelChoiceField(queryset=Dosen.objects.all(), empty_label="Pilih Dosen Wali")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(MahasiswaRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['universitas'].widget.attrs.update({'placeholder': 'Universitas', 'class': 'form-control'})
        self.fields['nim'].widget.attrs.update({'placeholder': 'NIM', 'class': 'form-control'})
        self.fields['dosen'].widget.attrs.update({'class': 'form-control'})

    def clean_ipk_mhs(self):
        ipk = self.cleaned_data.get('ipk_mhs')
        if ipk < 2.5 or ipk > 4.0:
            raise ValidationError("IPK harus di antara 2.5 dan 4.0.")
        return ipk

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Mahasiswa.objects.create(
                user=user,
                universitas=self.cleaned_data.get('universitas'),
                nim=self.cleaned_data.get('nim'),
                dosen=self.cleaned_data.get('dosen'),
                semester=self.cleaned_data.get('semester'),
                ipk_mhs=self.cleaned_data.get('ipk_mhs'),
            )
        return user
    
class DosenRegistrationForm(UserCreationForm):
    universitas = forms.CharField(max_length=100)
    nip = forms.CharField(max_length=50)
    department = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(DosenRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['universitas'].widget.attrs.update({'placeholder': 'Universitas', 'class': 'form-control'})
        self.fields['nip'].widget.attrs.update({'placeholder': 'NIP', 'class': 'form-control'})
        self.fields['department'].widget.attrs.update({'placeholder':'Department', 'class':'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Dosen.objects.create(
                user=user,
                universitas=self.cleaned_data.get('universitas'),
                nip=self.cleaned_data.get('nip'),
                department=self.cleaned_data.get('department')
            )
        return user
    
class TimKonversiForm(UserCreationForm):
    no_timkonversi = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(TimKonversiForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['no_timkonversi'].widget.attrs.update({'placeholder': 'No Tim Konversi', 'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            TimKonversi.objects.create(
                user=user,
                no_timkonversi=self.cleaned_data.get('no_timkonversi'),
            )
        return user
    
class LoaForm(forms.ModelForm):
    class Meta:
        model = Loa
        fields = ['loa_file']
        widgets = {
            'loa_file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({  
            'placeholder': 'Password',
            'class': 'form-control'
        })