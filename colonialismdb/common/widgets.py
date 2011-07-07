from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.contrib.admin import widgets

#class AutocompleteAdminWidget(forms.TextInput):
class AutocompleteAdminWidget(forms.HiddenInput):
    def __init__(self, rel, search_field, label_method=None, attrs=None):
        self.rel = rel
        self.search_field = search_field
        self.label_method = label_method
        super(AutocompleteAdminWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        output = [super(AutocompleteAdminWidget, self).render(name, value, attrs)]

        if value:
          label = self.label_for_value(value)
        else:
          label = u''

        output.append('''
        <input type="text" id="lookup_%(name)s" value="%(label)s" class="vTextField" maxlength="%(maxlength)s"/>
        <p class="help">Start typing to see available matches, and press "Enter" or "Tab" to select option</p>
        <link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>
        <script type="text/javascript">
          $(document).ready(function() { 
            $('#id_%(name)s').attr('readOnly', 1);
            $('#lookup_%(name)s').autocomplete({ source : function(request, response) 
                                                          {
                                                            $.ajax({ url : 'autocomplete/%(app_label)s/%(model)s/',
                                                                     datatype : 'json',
                                                                     data : { term : request.term,
                                                                              search_field : '%(search_field)s',
                                                                              label_method : '%(label_method)s',
                                                                            },
                                                                     success : function(data) 
                                                                     {
                                                                        response(data)
                                                                     }
                                                                   })
                                                          },
                                                 select : function(event, ui) 
                                                 {
                                                    $('#id_%(name)s').val(ui.item.pk);
                                                 },
                                                 delay : 0
                                               });
            $('#add_id_%(name)s').hide();
          });
        </script> ''' % { 'name' : name, 
                          'label' : label,
                          'maxlength' : 50,
                          'search_field' : self.search_field,
                          'label_method' : self.label_method if self.label_method else '',
                          'id' : attrs['id'], 
                          'app_label' : self.rel.to._meta.app_label, 
                          'model' : self.rel.to._meta.module_name })

        return mark_safe(u''.join(output))

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return truncate_words(obj, 14)

