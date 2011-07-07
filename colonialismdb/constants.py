from common.models import Location
from sources.models import SourceType

DAY_CHOICES = (
    ('--', '--'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', '31'),
)


MONTH_CHOICES = (
    ('', '--'),
    ('1', 'Jan'),
    ('2', 'Feb'),
    ('3', 'Mar'),
    ('4', 'Apr'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'Aug'),
    ('9', 'Sept'),
    ('10', 'Oct'),
    ('11', 'Nov'),
    ('12', 'Dec'),
)

CONTINENT_CHOICES = (
    ('', 'All'),
    ('Antartica', 'Antartica'),
    ('Asia', 'Asia'),
    ('Africa', 'Africa'),
    ('Australia', 'Australia'),
    ('Europe', 'Europe'),
    ('North America', 'North America'),
    ('Oceania', 'Oceania'),
    ('South America', 'South America'),
)

OCCUPATION_CHOICES = (
    ('', '-- Select One --'),
    ('Professor', 'Professor'),
    ('Teacher', 'Teacher'),
    ('Student', 'Student'),
    ('Government', 'Government'),
    ('Research Institute', 'Research Institute'),
    ('Business', 'Business'),
    ('Law', 'Law'),
    ('Other', 'Other'),
)

PURPOSE_OF_VISIT_CHOICES = (
    ('', '-- Select One --'),
    ('Research', 'Research'),
    ('Teaching', 'Teaching'),
    ('Personal Interest', 'Personal Interest'),
)

EMPIRE_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.name)) for l in Location.objects.filter(unit_type__name='Empire').distinct().order_by('name')]
NATION_STATE_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.name)) for l in Location.objects.filter(unit_type__name='Nation-state').distinct().order_by('name')]
CONFEDERATION_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.full_name)) for l in Location.objects.filter(unit_type__name='Confederation').distinct().order_by('name')]
SEMI_SOVEREIGN_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.full_name)) for l in Location.objects.filter(unit_type__name__in=['Semi-Sovereign', 'Protectorate', 'Colony', 'Territory']).distinct().order_by('name')]
NON_SOVEREIGN_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.full_name)) for l in Location.objects.filter(unit_type__name__in=['City','State', 'Village', 'District', 'County', 'Prefecture','Provinces', 'Province', 'Region', 'Municipality']).distinct().order_by('name')]

SOURCE_TYPE_CHOICES = [('', 'All')] + [(l.id, ("%s" % l.name)) for l in SourceType.objects.all().order_by('name')]
