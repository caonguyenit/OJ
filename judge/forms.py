from operator import attrgetter

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm

from django_ace import AceWidget
from judge.comments import valid_comment_page
from judge.models import Organization
from .models import Profile, Submission, Comment, Problem

try:
    from pagedown.widgets import PagedownWidget
except ImportError:
    PagedownWidget = None


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'about', 'organization', 'timezone', 'language', 'ace_theme']


class ProblemSubmitForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProblemSubmitForm, self).__init__(*args, **kwargs)
        self.fields['problem'].empty_label = None
        self.fields['problem'].widget = forms.HiddenInput()
        self.fields['language'].empty_label = None
        self.fields['language'].label_from_instance = attrgetter('display_name')

    class Meta:
        model = Submission
        fields = ['problem', 'source', 'language']
        widgets = {
            'source': AceWidget(theme='twilight'),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'body', 'parent']
        widgets = {
            'parent': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'style': 'min-width:100%', 'placeholder': 'Comment title'})
        self.fields['body'].widget.attrs.update({'style': 'min-width:100%', 'placeholder': 'Comment body'})

    def clean_page(self):
        page = self.cleaned_data['page']
        if not valid_comment_page(page):
            raise ValidationError('Invalid page id: %(id)s', params={'id': page})


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'key', 'about']


class EditOrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'short_name', 'about', 'admins']
        widgets = {
            'admins': FilteredSelectMultiple('Admins', False)
        }
        if PagedownWidget is not None:
            widgets['about'] = PagedownWidget


class NewOrganizationForm(EditOrganizationForm):
    class Meta(EditOrganizationForm.Meta):
        fields = ['key'] + EditOrganizationForm.Meta.fields


class ProblemEditForm(ModelForm):
    class Meta:
        model = Problem
        fields = ['name', 'is_public', 'authors', 'types', 'group', 'description', 'time_limit',
                  'memory_limit', 'points', 'partial', 'allowed_languages']
        widgets = {
            'authors': FilteredSelectMultiple('Authors', False),
            'types': FilteredSelectMultiple('Problem types', False),
            'allowed_languages': FilteredSelectMultiple('Allowed languages', False),
        }
        if PagedownWidget is not None:
            widgets['description'] = PagedownWidget

    def __init__(self, *args, **kwargs):
        super(ProblemEditForm, self).__init__(*args, **kwargs)
        self.fields['authors'].queryset = Profile.objects.filter(Q(user__group__in=['ProblemSetter', 'Admin']) |
                                                                 Q(user__is_superuser=True))
