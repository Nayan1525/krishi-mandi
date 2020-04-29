from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from myapp.models import Farmer,User,Dealer,Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']
        help_texts = {
            'username': None,}

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['usern']

class FarmerSignUpForm(UserCreationForm):
    # interests = forms.ModelMultipleChoiceField(
    #     queryset=Subject.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=True
    # )
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1','email', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_farmer = True
        if commit:
            user.save()
        # farmer.interests.add(*self.cleaned_data.get('interests'))
        return user


class DealerSignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1','email', 'password2']:
            self.fields[fieldname].help_text = None
            
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_dealer = True
        if commit:
            user.save()
        return user