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
        fields = ['title', 'description', 'tags', 'preview', 'text']  # Include the 'description' field
        labels = {'title':       'Title of your guide',
                  'description': 'Short description',
                  'text':        'Briefly explain your guide here'}


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
