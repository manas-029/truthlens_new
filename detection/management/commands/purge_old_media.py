from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from detection.models import Scan


class Command(BaseCommand):
    help = 'Delete uploaded media files older than MEDIA_RETENTION_DAYS while retaining scan records.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=settings.MEDIA_RETENTION_DAYS)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(days=options['days'])
        scans = Scan.objects.filter(created_at__lt=cutoff).exclude(file='')
        purged = 0
        for scan in scans.iterator():
            if not scan.file:
                continue
            name = scan.file.name
            self.stdout.write(f'Purging {name} from scan {scan.id}')
            if not options['dry_run']:
                scan.file.delete(save=False)
                scan.file = None
                scan.save(update_fields=['file'])
            purged += 1
        self.stdout.write(self.style.SUCCESS(f'{purged} media file(s) matched retention policy.'))
