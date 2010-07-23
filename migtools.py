
def get_or_add_cat_item(item, mig_user, cat):
  if not item or len(item) == 0:
    return None

  item = item.title()

  try:
    return cat.objects.get(name = item)
  except cat.DoesNotExist:
    new_obj = cat(name = item, active = True, submitted_by = mig_user)
    new_obj.save()
    return new_obj

