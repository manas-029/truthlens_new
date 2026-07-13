import os

from django import forms
from django.conf import settings
from .models import Scan


MEDIA_SIGNATURES = {
    'image': (
        b'\xff\xd8\xff',  # jpg
        b'\x89PNG\r\n\x1a\n',
        b'GIF87a',
        b'GIF89a',
        b'RIFF',  # webp starts RIFF....WEBP
    ),
    'audio': (
        b'ID3',
        b'\xff\xfb',
        b'\xff\xf3',
        b'\xff\xf2',
        b'RIFF',  # wav
        b'fLaC',
        b'OggS',
    ),
    'video': (
        b'\x00\x00\x00',  # mp4/mov boxes usually start with a size then ftyp
        b'ftyp',
        b'\x1aE\xdf\xa3',  # webm/mkv
        b'RIFF',  # avi
    ),
}

EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
    'audio': {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'},
    'video': {'.mp4', '.mov', '.avi', '.mkv', '.webm'},
}


class ScanUploadForm(forms.ModelForm):
    class Meta:
        model = Scan
        fields = ['file', 'media_type']
        widgets = {
            'media_type': forms.HiddenInput(),
        }

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        media_type = self.data.get('media_type') or self.cleaned_data.get('media_type')
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded.size > max_bytes:
            raise forms.ValidationError(f'File must be {settings.MAX_UPLOAD_SIZE_MB} MB or smaller.')

        ext = os.path.splitext(uploaded.name.lower())[1]
        if ext not in EXTENSIONS.get(media_type, set()):
            raise forms.ValidationError(f'Unsupported {media_type} file extension.')

        head = uploaded.read(32)
        uploaded.seek(0)
        signatures = MEDIA_SIGNATURES.get(media_type, ())
        if not any(head.startswith(sig) or sig in head[:16] for sig in signatures):
            raise forms.ValidationError('The file signature does not match the selected media type.')
        return uploaded


class URLScanForm(forms.Form):
    source_url = forms.URLField(label='Paste a video URL')
    media_type = forms.CharField(widget=forms.HiddenInput(), initial='video')
