#!/usr/bin/python

import datetime
import sys

from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location

coder_names = ("ahmedn", "chelsea", "mahsa", "nathalie", "tavish", )

first_day = datetime.date(2010, 10, 4) # starting on a Friday; assuming Fri-Thu work week
last_day = datetime.date.today()
len_workweek = datetime.timedelta(6)

work_gap = datetime.timedelta(minutes = 15)

model_tables = (('population', ), ('education', ), ('government', ), ('infrastructure', ), ) # ('economics', 'BilateralTradeDataEntry'), )

sep = ","

if __name__ == "__main__":
  if len(sys.argv) > 1:
    work_gap = datetime.timedelta(minutes = int(sys.argv[1])
  
  begin_week = first_day
  end_week = begin_week + len_workweek

  while end_week < datetime.date.today():
    today = begin_week

    while today <= end_week:
      sys.stdout.write("%s%s" % (sep, today.strftime("%a %m/%d")))
      today = today + datetime.timedelta(1)

    begin_week = end_week + datetime.timedelta(1)
    end_week = begin_week + len_workweek
  else:
    sys.stdout.write("\n")


  for coder_name in coder_names:
    try:
      coder = User.objects.get(username = coder_name)
    except User.DoesNotExist:
      continue

    sys.stdout.write("%s" % coder.username)

    begin_week = first_day
    end_week = begin_week + len_workweek

    while end_week < datetime.date.today():
      today = begin_week

      while today <= end_week:
        num_entries = 0
        work_hours = None

        for model_info in model_tables:
          app_name = model_info[0]
          class_name = model_info[1] if len(model_info) > 1 else "maindataentry"
          last_begin_range = None
          last_timestamp = None

          submitted_entries = getattr(coder, "submitted_%s_%s" % (app_name, class_name))

          #num_entries += submitted_entries.filter(datetime_created__year = today.year).filter(datetime_created__month = today.month).filter(datetime_created__day = today.day).count()

          filtered_submitted = submitted_entries.filter(datetime_created__year = today.year).filter(datetime_created__month = today.month).filter(datetime_created__day = today.day)

          if filtered_submitted.count() > 0:
            for entr in filtered_submitted.order_by('datetime_created'):
              if not last_timestamp:
                if work_hours == None:
                  work_hours = list()
                last_timestamp = last_begin_range = entr.datetime_created
                continue
              if last_timestamp and (entr.datetime_created - last_timestamp > work_gap):
                work_hours.append((last_begin_range, last_timestamp))
                last_begin_range = entr.datetime_created
              last_timestamp = entr.datetime_created
            else:
              if last_timestamp:
                work_hours.append((last_begin_range, last_timestamp))

        day_work_hours = datetime.timedelta() 
        if work_hours:
          for work_range in work_hours:
            day_work_hours = day_work_hours + (work_range[1] - work_range[0])
          sys.stdout.write("%s%f" % (sep, float(day_work_hours.seconds) / 60 / 60))
        else:
          sys.stdout.write("%s0" % (sep))


        #sys.stdout.write("%s%i" % (sep, num_entries))

        today = today + datetime.timedelta(1)

      begin_week = end_week + datetime.timedelta(1)
      end_week = begin_week + len_workweek

    sys.stdout.write("\n")



