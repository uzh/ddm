from django.contrib import admin
from ddm_pooled.models import PooledProject


class PooledProjectAdmin(admin.ModelAdmin):
    """
    Provides an overview of all Pooled Donation Projects.
    """
    list_display = ['project']


admin.site.register(PooledProject, PooledProjectAdmin)
