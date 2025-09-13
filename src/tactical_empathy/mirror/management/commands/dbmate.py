from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from mirror.models import Role
import urllib.parse
import subprocess
import os


class Command(BaseCommand):
  help = 'Run dbmate database migrations'

  def add_arguments(self, parser):
    parser.add_argument(
        'action',
        choices=['up', 'down', 'new', 'status', 'rollback'],
        help='Dbmate action to perform'
    )
    parser.add_argument(
        'name',
        nargs='?',
        help='Migration name (required for new migrations)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of migrations to rollback'
    )

  def handle(self, *args, **options):
    # Build DATABASE_URL from Django settings with proper URL encoding
    db_config = settings.DATABASES['default']

    # URL encode the password to handle special characters
    encoded_password = urllib.parse.quote(db_config['PASSWORD'], safe='')

    database_url = (
        f"postgres://{db_config['USER']}:{encoded_password}"
        f"@{db_config['HOST']}:{db_config['PORT']}"
        f"/{db_config['NAME']}?sslmode=disable"
    )

    # Set environment variable
    env = os.environ.copy()
    env['DATABASE_URL'] = database_url

    # Debug output
    self.stdout.write(f"Using DATABASE_URL: {database_url}")

    # Build dbmate command
    cmd = ['dbmate', options['action']]

    if options['action'] == 'new':
      if not options['name']:
        raise CommandError("Migration name is required for 'new' action")
      cmd.append(options['name'])
    elif options['action'] == 'rollback':
      cmd.extend(['--count', str(options['count'])])

    try:
      self.stdout.write(f"Running: {' '.join(cmd)}")
      result = subprocess.run(
          cmd,
          env=env,
          capture_output=True,
          text=True,
          check=True
      )

      self.stdout.write(self.style.SUCCESS(result.stdout))
      if result.stderr:
        self.stdout.write(self.style.WARNING(result.stderr))

      # Populate roles after successful 'up' migration
      if options['action'] == 'up':
        self._populate_roles()

    except subprocess.CalledProcessError as e:
      self.stdout.write(self.style.ERROR(f"Command failed: {e}"))
      self.stdout.write(self.style.ERROR(f"stdout: {e.stdout}"))
      self.stdout.write(self.style.ERROR(f"stderr: {e.stderr}"))
      raise CommandError(f"dbmate {options['action']} failed")
    except FileNotFoundError:
      raise CommandError("dbmate not found. Please install dbmate first.")

  def _populate_roles(self):
    """Populate the roles table with default user and bot roles."""
    try:
      self.stdout.write("\n--- Populating roles ---")
      roles_to_create = ['user', 'bot']
      
      for role_name in roles_to_create:
        role, created = Role.objects.get_or_create(name=role_name)
        if created:
          self.stdout.write(
              self.style.SUCCESS(f'✓ Created role: {role_name}')
          )
        else:
          self.stdout.write(
              self.style.WARNING(f'• Role already exists: {role_name}')
          )
      
      self.stdout.write(
          self.style.SUCCESS('✓ Role population completed!')
      )
    except Exception as e:
      self.stdout.write(
          self.style.ERROR(f'✗ Error populating roles: {e}')
      )
