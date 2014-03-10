from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand): 
    help = "Backup items into fixtures" 
    def handle_noargs(self, **options): 
        from django.core import serializers
        from django.db.models import get_models

        for item in get_models():
            if item.__name__ is not 'south':
                file_name = 'shoghlanah/fixtures/' + item.__name__ + '_backup.json'
                data = serializers.serialize('json', item.objects.all(), use_natural_keys=True, indent = 4)
                if len(list(data)) > 3:
                    f = open(file_name, 'w')
                    f.write(data)
                    f.close()
