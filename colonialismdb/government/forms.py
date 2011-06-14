from django import forms

from common.models import Location, BaseDataEntry, Category, SpatialAreaUnit, Currency
from sources.models import BaseSourceObject

from constants import DAY_CHOICES, MONTH_CHOICES

CURRENCY_CHOICES = [(l.id, l.name) for l in Currency.objects.all().order_by('name')]
LOCATION_CHOICES = [(l.id, l.name) for l in Location.objects.all().order_by('name')]
SOURCE_CHOICES = [(l.id, l.name) for l in BaseSourceObject.objects.all().order_by('name')]



class GovernmentSearchForm(forms.Form):
    start_day = forms.CharField(label='Start Day', max_length=2,
                widget=forms.Select(choices=DAY_CHOICES), required=False)

    start_month = forms.CharField(label='Start Month', max_length=15,
                widget=forms.Select(choices=MONTH_CHOICES), required=False)

    start_year = forms.CharField(label="Start Year", max_length=4)
    end_day = forms.CharField(label='End Day', max_length=100,
                widget=forms.Select(choices=DAY_CHOICES), required=False)

    end_month = forms.CharField(label='End Month', max_length=100,

                widget=forms.Select(choices=MONTH_CHOICES), required=False)
    end_year = forms.CharField(label="End Year", max_length=4)

    currency = forms.CharField(label='Currency',
        widget=forms.SelectMultiple(choices=CURRENCY_CHOICES,
            attrs={'style':'height: 100px;width: 250px; overflow: auto;'},), required=False)

    location = forms.CharField(label='Location',
        widget=forms.SelectMultiple(choices=LOCATION_CHOICES,
            attrs={'style':'height: 100px;width: 250px; overflow: auto;'},), required=False)

    source = forms.CharField(label='Source',
        widget=forms.SelectMultiple(choices=SOURCE_CHOICES,
            attrs={'style':'height: 100px;width: 250px; overflow: auto;'},), required=False)

