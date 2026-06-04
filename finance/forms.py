from django import forms
from .models import ContainerNotification


class ContainerNotificationForm(forms.ModelForm):
    class Meta:
        model  = ContainerNotification
        fields = ['crn_container_no']
        labels = {'crn_container_no': 'Container No'}
        widgets = {
            'crn_container_no': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'CNT-TCKU1234567',
                'style': 'text-transform:uppercase;',
                'oninput': 'this.value=this.value.toUpperCase()',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If creating new record, prefill with CNT- prefix
        if not self.instance.pk:
            self.fields['crn_container_no'].initial = 'CNT-'

    def clean_crn_container_no(self):
        value = self.cleaned_data.get('crn_container_no', '').upper()
        # Ensure it starts with CNT-
        if value and not value.startswith('CNT-'):
            value = 'CNT-' + value
        return value
