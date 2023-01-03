from django.db.models.signals import post_delete
from django.dispatch import receiver

from ddm.models.core import DonationInstruction, FileUploader


@receiver(post_delete, sender=DonationInstruction)
def reorder_indices(sender, instance, **kwargs):
    # Only execute signal, if model is not deleted due to delete.cascade.
    try:
        queryset = instance.file_uploader.donationinstruction_set.filter(index__gt=instance.index).order_by('index')
        for q in queryset:
            q.index -= 1
            q.save()
    except FileUploader.DoesNotExist:
        pass
    return


@receiver(post_delete, sender=FileUploader)
def reorder_indices(sender, instance, **kwargs):
    # Only execute signal, if model is not deleted due to delete.cascade.
    queryset = FileUploader.objects.filter(project=instance.project, index__gt=instance.index).order_by('index')
    for q in queryset:
        q.index -= 1
        q.save()
    return
