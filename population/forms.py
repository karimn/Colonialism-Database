from django import forms

import models

class MainPopulationQueryForm(forms.Form):
  location = forms.ModelMultipleChoiceField(queryset = models.Location.objects, required = False, label = 'Location')
