from django.db.models import fields
from insrnceDataApp.models import Policy
from rest_framework import serializers

class PolicyPdfSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('policy_pdf', 'category')

class ExcelSrlzr(serializers.Serializer):
    myExcel = serializers.FileField()

class PolicySrlzr(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = "__all__"
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = instance.category.category_name
        if instance.client!= None:
            rep['client'] = instance.client.id_code
        rep['agent'] = instance.agent.id_code
        return rep

class PlcyToClntSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Policy
        exclude = ('agent', 'branch_ref_code', 'main_acc_code', 'end_claim_number', 'policy_pdf')