from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import CommandError

from users.models import User


class Command(createsuperuser.Command):
    '''Custom command to create superuser. To do so write in terminal: 
    
    python manage.py createcustomsuperuser --username <value> --email <value>
    --first_name <value> last_name <value> --password <value>.
    '''
    help = 'Creates custom User instance as superuser'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--first_name', dest='first_name',
            help='Specifies the first name for the superuser.',
        )
        parser.add_argument(
            '--last_name', dest='last_name',
            help='Specifies the last name for the superuser.',
        )
        parser.add_argument(
            '--username', dest='username',
            help='Specifies the username for the superuser.',
        )
        parser.add_argument(
            '--password', dest='password',
            help='Specifies the password for the superuser.',
        )


    def handle(self, *args, **options):
        password = options.get('password')
        username = options.get('username')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        email = options.get('email')
        
        if (
            not password
            or not username
            or not first_name
            or not last_name
            or not email
        ):
            raise CommandError(
                "missed at least one of the following arguments: "
                + "--username, --password, --first_name, --last_name, --email"
            )

        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'role': 'admin',
            'first_name': first_name,
            'last_name': last_name

        }
        try:
            User.objects.create(**user_data)
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write("Superuser created successfully.")
        except:
            self.stdout.write("Failed to create superuser.")
