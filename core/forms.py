from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': '.pdf',
            'style': 'display: none;',
            'id': 'pdf-input'
        })
    )