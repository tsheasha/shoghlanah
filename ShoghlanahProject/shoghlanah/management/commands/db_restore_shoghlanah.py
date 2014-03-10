from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand): 
    help = "Restore Items from fixtures to db" 
    def handle_noargs(self, **options):
        from django.core import serializers
        from os import listdir
        from os.path import isfile, join
        from django.db import IntegrityError

        json_files = [ join('shoghlanah/fixtures/',f) for f in listdir('shoghlanah/fixtures/') if isfile(join('shoghlanah/fixtures/',f)) and f.endswith('json') ]
        while len(json_files) > 0:
            json_file = json_files[0]
            json_data = open(json_file)
            res = serializers.deserialize("json", json_data, ignorenonexistent=True)
            try:
                for obj in res:
                    obj.save()
                json_data.close()
                del json_files[0]
            except IntegrityError:
                json_files.insert(len(json_files), json_file)
                del json_files[0]
                    

           
