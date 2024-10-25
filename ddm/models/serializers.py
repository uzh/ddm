from rest_framework import serializers

from ddm.models.core import DonationProject


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['pk', 'name', 'date_created']
