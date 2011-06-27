from django import forms

from common.forms import GeneralSearchForm

class GovernmentSearchForm(GeneralSearchForm):
    test_input = forms.IntegerField()
