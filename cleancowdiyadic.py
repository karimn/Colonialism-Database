#!/usr/bin/python

import migtools

from django.db.models import Q

from colonialismdb.economics.models import BilateralTradeDataEntry

if __name__ == "__main__":
  for bidata in BilateralTradeDataEntry.objects.filter(Q(exports = -9) | Q(imports = -9), Q(source = 3393)):
    if bidata.imports == -9:
      if bidata.exports == -9:
        bidata.delete()
      else:
        bidata.imports = None
        bidata.save()
    else:
      bidata.exports = None
      bidata.save()

