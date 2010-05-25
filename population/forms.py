from django import forms

import models

class MainPopulationQueryForm(forms.Form):
  location = forms.ModelMultipleChoiceField(queryset = models.Location.objects, required = False, label = 'Location')
  begin_date = forms.DateField(required = False, label = "From Date")
  end_date = forms.DateField(required = False, label = "To Date")
