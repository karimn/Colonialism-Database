from django import forms
from django.forms.fields import MultipleChoiceField
from constants import EMPIRE_CHOICES, NATION_STATE_CHOICES, CONTINENT_CHOICES, \
                        SEMI_SOVEREIGN_CHOICES, NON_SOVEREIGN_CHOICES, SOURCE_TYPE_CHOICES, \
                        CONFEDERATION_CHOICES

class GeneralSearchForm(forms.Form):

    start_date_day = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:30px', 'disabled': 'true'}))
    start_date_month = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:30px', 'disabled': 'true'}))
    start_date_year = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:50px', 'disabled': 'true'}))

    end_date_day = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:30px', 'disabled': 'true'}))
    end_date_month = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:30px', 'disabled': 'true'}))
    end_date_year = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style': 'width:50px', 'disabled': 'true'}))
    all_time_frames = forms.BooleanField(initial=True)

    locations = forms.CharField(required=False, widget=forms.TextInput(attrs={'style': 'width:400px', 'disabled': 'true'}))
    all_locations = forms.BooleanField(initial=True)

    continent = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=CONTINENT_CHOICES, initial=('', 'All'))

    empire = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=EMPIRE_CHOICES, initial=('', 'All'))

    nation_state = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=NATION_STATE_CHOICES, initial=('', 'All'))

    semi_sovereign = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=SEMI_SOVEREIGN_CHOICES, initial=('', 'All'))

    non_sovereign = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=NON_SOVEREIGN_CHOICES, initial=('', 'All'))

    source_type = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=SOURCE_TYPE_CHOICES, initial=('', 'All'))

    
    confederation = forms.MultipleChoiceField(required=False,
                                       widget=forms.SelectMultiple(attrs={'size':'8', 'style':'width:200px;'}),
                                       choices=CONFEDERATION_CHOICES, initial=('', 'All'))


