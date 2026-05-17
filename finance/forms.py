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
                'placeholder': 'e.g. CNT-TCKU1234567',
                'style': 'text-transform:uppercase;',
                'oninput': 'this.value=this.value.toUpperCase()',
            }),
        }

    def clean_crn_container_no(self):
        return self.cleaned_data.get('crn_container_no', '').upper()
