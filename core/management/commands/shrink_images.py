"""Makes web-size copies of photos already uploaded (vehicles, gallery, categories, site hero/about).

Originals stay on disk; each record is pointed at its smaller copy. Run with --dry-run first to see what would change.
"""
from django.core.management.base import BaseCommand

from core.images import shrunk
from core.models import SiteConfig
from vehicles.models import Vehicle, VehicleCategory, VehicleImage

TARGETS = [
    (Vehicle, ["thumbnail"]),
    (VehicleImage, ["image"]),
    (VehicleCategory, ["image"]),
    (SiteConfig, ["hero_image", "hero_bg_1", "hero_bg_2", "hero_bg_3", "about_image"]),
]


class Command(BaseCommand):
    help = "Shrink oversized uploaded photos to web size (originals are kept)."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, dry_run=False, **opts):
        done = saved = 0
        for model, fields in TARGETS:
            for obj in model.objects.all():
                for name in fields:
                    f = getattr(obj, name)
                    if not f:
                        continue
                    try:
                        before = f.size
                        with f.open("rb") as fh:
                            res = shrunk(fh)
                    except (FileNotFoundError, OSError):
                        self.stdout.write(f"  missing: {f.name}")
                        continue
                    if not res:
                        continue
                    new_name, content = res
                    after = len(content)
                    self.stdout.write(f"{model.__name__} #{obj.pk} {name}: {f.name} {before // 1024} KB -> {after // 1024} KB")
                    if not dry_run:
                        stored = f.storage.save(f.field.generate_filename(obj, new_name), content)
                        model.objects.filter(pk=obj.pk).update(**{name: stored})
                    done += 1
                    saved += before - after
        verb = "Would shrink" if dry_run else "Shrank"
        self.stdout.write(self.style.SUCCESS(f"{verb} {done} photo(s), saving {saved // 1024} KB."))
