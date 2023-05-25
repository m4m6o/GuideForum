from django import forms
from django_select2.forms import Select2TagWidget
from . import models


class TopicForm(forms.ModelForm):
    tags = forms.CharField(
        widget=Select2TagWidget(attrs={
            'data-placeholder': 'Choose tags',
            'data-tags': 'true',
            'data-token-separators': "[',', ' ']",
        }),
        required=False,
    )

    preview = forms.ImageField(widget=forms.ClearableFileInput, required=False)

    class Meta:
        model = models.Topic
        fields = ['title', 'description', 'tags', 'preview', 'text']
        labels = {
            'title': 'Title of your guide',
            'description': 'Short description',
            'text': 'Briefly explain your guide here'
        }

    def clean(self):
        cleaned_data = super().clean()
        clear_preview = self.cleaned_data.get('clear_preview')

        if clear_preview:
            cleaned_data['preview'] = None

        return cleaned_data


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
