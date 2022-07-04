from django.db.models.signals import post_delete
from django.dispatch import receiver

from ddm.models import DonationInstruction


@receiver(post_delete, sender=DonationInstruction)
def reorder_indices(sender, instance, **kwargs):
    queryset = instance.get_query_object().donationinstruction_set.filter(index__gt=instance.index).order_by('index')
    for q in queryset:
        q.index -= 1
        q.save()
    return
