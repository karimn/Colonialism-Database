#!/usr/bin/python

import datetime

from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location

coder_names = ("ahmedn", "chelsea", "mahsa", "nathalie", "tavish", )

first_day = datetime.date(2010, 9, 24) # starting on a Friday; assuming Fri-Thu work week
last_day = datetime.date.today()
len_workweek = datetime.timedelta(6)

model_tables = (('population', ), ('education', ), ('government', ), ('infrastructure', ), ) # ('economics', 'BilateralTradeDataEntry'), )

if __name__ == "__main__":
  begin_week = first_day
  end_week = begin_week + len_workweek

  while end_week < datetime.date.today():
    today = begin_week

    while today <= end_week:
      for coder_name in coder_names:
        try:
          coder = User.objects.get(username = coder_name)
        except User.DoesNotExist:
          continue

        num_entries = 0

        for model_info in model_tables:
          app_name = model_info[0]
          class_name = model_info[1] if len(model_info) > 1 else "maindataentry"

          submitted_entries = getattr(coder, "submitted_%s_%s" % (app_name, class_name))
          num_entries =+ submitted_entries.filter(datetime_created = today).count()

        print("%(coder)s, %(day)s, %(num_entries)i" % { 'coder' : coder.username, 'day' : today.strftime("%y-%m-%d"), 'num_entries' : num_entries })

      today = today + datetime.timedelta(1)

    begin_week = end_week + datetime.timedelta(1)
    end_week = begin_week + len_workweek



