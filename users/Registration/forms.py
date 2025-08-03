

from django import forms
from news.models import UserPreference, Category

class UserPreferenceForm(forms.ModelForm):
    preferred_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserPreference
        fields = ['preferred_categories']
