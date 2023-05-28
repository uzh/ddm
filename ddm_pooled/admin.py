from django.contrib import admin
from ddm_pooled.models import PooledProject


# Register your models here.
class PooledProjectAdmin(admin.ModelAdmin):
    """
    Provides an overview of all active Donation Projects.
    """
    list_display = ['project']


admin.site.register(PooledProject, PooledProjectAdmin)
