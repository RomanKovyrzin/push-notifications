import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from pushes.models import Push, Option


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def clean_remember_me(self):
        data = self.cleaned_data['remember_me']
        if not data:
            self.request.session.set_expiry(0)
        return data


class CreatePushForm(forms.Form):
    title = forms.CharField(label='Заголовок уведомления', label_suffix='', max_length=50)
    text = forms.CharField(
        label='Текст уведомления', 
        label_suffix='', 
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'oninput': 'displayText(this.value)',
            }))
    send_date = forms.DateTimeField(label='Дата отправки', disabled=True, required=False, label_suffix='',)

    # Handle form input tag to access field attributes from template
    title.widget.attrs.update({
        'class': 'form-control form-control-lg',
        'oninput': 'displayTitle(this.value)'
        })
    send_date.widget.attrs.update({'class': 'form-control form-control-lg'})

    def clean_renewal_date(self):
        data = self.cleaned_data['push_title']
        
        # Check if a title less then or equal 50 chars. 
        if len(data) > 50:
            raise ValidationError(_('Invalid field length - over 50 chars'))

        # Remember to always return the cleaned data.
        return data


class SendPushForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'oninput': 'displayTitle(this.value)'
            })
        self.fields['text'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'oninput': 'displayText(this.value)'
            })

    title = forms.CharField(label='Заголовок уведомления', label_suffix='', max_length=50)
    text = forms.CharField(label='Текст уведомления', label_suffix='', widget=forms.Textarea)
    send_date = forms.DateTimeField(disabled=True, required=False, label_suffix='',)
    is_sent = forms.BooleanField(disabled=True, required=False)

    class Meta:
        model = Push
        fields = ['title', 'text', 'send_date', 'is_sent',]
        
    