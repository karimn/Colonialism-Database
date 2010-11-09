from django.db import models

from colonialismdb import common

class BaseTradeDataEntry(common.models.BaseDataEntry):
  class Meta(common.models.BaseDataEntry.Meta):
    abstract = True

  imports = models.DecimalField(max_digits = 20, decimal_places = 10, null = True, blank = True)
  exports = models.DecimalField(max_digits = 20, decimal_places = 10, null = True, blank = True)
  
  imports_value_unit = models.CharField("imports value unit", max_length = 20, choices = common.models.BaseDataEntry.UNIT_CHOICES, default = 'units')
  exports_value_unit = models.CharField("exports value unit", max_length = 20, choices = common.models.BaseDataEntry.UNIT_CHOICES, default = 'units')

  currency = models.ForeignKey(common.models.Currency, null = True, blank = True, related_name = '%(app_label)s_%(class)s_related')

class AggregateTradeDataEntry(BaseTradeDataEntry):
  class Meta(BaseTradeDataEntry.Meta):
    verbose_name = "aggregate trade data entry"
    verbose_name_plural = "aggregate trade data entries"
    permissions = ( ('activate_aggtradedataentry', 'Can activate submitted aggregate trade data entry'), )

class BilateralTradeDataEntry(BaseTradeDataEntry):
  class Meta(BaseTradeDataEntry.Meta):
    verbose_name = "bilateral trade data entry"
    verbose_name_plural = "bilateral trade data entries"
    permissions = ( ('activate_bilatradedataentry', 'Can activate submitted bilateral trade data entry'), )

  trade_partner = models.ForeignKey(common.models.PoliticalUnit, related_name = '%(app_label)s_%(class)s_trade_partner_related')

  imports_exchange_rate = models.DecimalField(max_digits = 13, decimal_places = 10, null = True, blank = True)
  exports_exchange_rate = models.DecimalField(max_digits = 13, decimal_places = 10, null = True, blank = True)
  gfd_exchange_rate = models.DecimalField(max_digits = 13, decimal_places = 10, null = True, blank = True)
  exchange_rate_scalar = models.DecimalField(max_digits = 6, decimal_places = 4, null = True, blank = True, help_text = "GFD Rate/Imputed Rate")

  imports_weight = models.DecimalField(max_digits = 18, decimal_places = 10, null = True, blank = True)
  exports_weight = models.DecimalField(max_digits = 18, decimal_places = 10, null = True, blank = True)
  imports_weight_unit = models.ForeignKey(common.models.WeightUnit, blank = True, null = True, related_name = '%(app_label)s_%(class)s_imports_related')
  exports_weight_unit = models.ForeignKey(common.models.WeightUnit, blank = True, null = True, related_name = '%(app_label)s_%(class)s_exports_related')

  ppi = models.DecimalField("producer price index", max_digits = 12, decimal_places = 10, null = True, blank = True)

  def __unicode__(self):
    return "%s + %s (%s - %s)" % (unicode(self.location), unicode(self.trade_partner), self.begin_date, self.end_date)
