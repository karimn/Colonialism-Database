"""
Forms and validation code for user registration.

"""


from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}

from constants import OCCUPATION_CHOICES, PURPOSE_OF_VISIT_CHOICES
from common.models import UserProfile

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value must contain only letters, numbers and underscores.")})
    first_name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                                    label=_("First Name"))
    last_name = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                                    label=_("Last Name"))

    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("E-mail"))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"))

    country_of_residence = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)))
    
    occupation = forms.CharField(widget=forms.Select(choices=OCCUPATION_CHOICES))
    purpose_of_visit = forms.CharField(widget=forms.Select(choices=PURPOSE_OF_VISIT_CHOICES), required=False)

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']


    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


    def save(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # this will only be done one time, so we need to create a user profile
        profile = UserProfile()
        profile.user = user
        profile.occupation = self.cleaned_data['occupation']
        profile.reason_of_visit = self.cleaned_data['purpose_of_visit']
        profile.country_of_residence = self.cleaned_data['country_of_residence']

        profile.save()

        user.save()

