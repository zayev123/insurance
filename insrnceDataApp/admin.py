from insrnceDataApp.models import Claim, Endorsement, Policy, Policy_pdf, Receipt, UserInfo, Category
from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from import_export.admin import ExportActionModelAdmin

 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']


@admin.register(Policy)
class PolicyAdmin(ExportActionModelAdmin):
    list_display = ['id', 'policy_number', 'policy_issue_date', 'client', 'client_name', 'percentage_premium_paid', 'agent', 'end_claim_number', 'policy_expiry_date', 'l_c_number', 'b_l_number']
    search_fields = ['policy_number', 'policy_issue_date', 'client__email', 'client__name', 'client_name', 'end_claim_number', 'agent__email', 'agent__name', 'l_c_number', 'b_l_number']
    readonly_fields=['outstanding', 'premium', 'personal_comission', 'percentage_premium_paid', 'policy_added_to_system_date', 'latest_financial_endorsement']
    raw_id_fields = ('client', 'agent')
    actions = ['delete_selected']

@admin.register(Receipt)
class ReceiptAdmin(ExportActionModelAdmin):
    list_display = ['receipt_number', 'policy', 'receipt_date', 'premium_paid']
    search_fields = ['receipt_number', 'policy__policy_number', 'policy__client_name', 'policy__client__name', 'receipt_date']
    readonly_fields=['edit_premium_paid', 'receipt_added_to_system_date']
    raw_id_fields = ("policy",)
    actions = ['delete_selected']

    def delete_queryset(self, request, queryset):
        for myReceipt in queryset:
            myPolicy = Policy.objects.get(id = myReceipt.policy.id)
            myPolicy.outstanding = myPolicy.outstanding + myReceipt.premium_paid
            myPolicy.save()
            myReceipt.delete(True)
            

@admin.register(Endorsement)
class EndorsementAdmin(ExportActionModelAdmin):
    list_display = ['id', 'endorsement_number', 'policy', 'endorsement_issue_date', 'previous_premium', 'new_premium']
    search_fields = ['endorsement_number', 'policy__policy_number', 'policy__client_name', 'policy__client__name', 'endorsement_issue_date']
    raw_id_fields = ("policy",)
    readonly_fields = ['endorsement_added_to_system_date', 'previous_financial_endorsement', 'previous_premium']

    actions = ['delete_selected']

    def delete_queryset(self, request, queryset):
        for myEndorsement in queryset:
            #myPolicy = Policy.objects.get(id = myEndorsement.policy.id)
            #myPolicy.outstanding = myPolicy.outstanding + myEndorsement.premium_paid
            #myPolicy.save()
            myEndorsement.delete()

@admin.register(Claim)
class ClaimAdmin(ExportActionModelAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('claim_number', 'policy', 'date_of_loss', 'bill_cost')
    search_fields = ['claim_number', 'policy__policy_number', 'policy__client_name', 'policy__client__name', 'date_of_loss']
    raw_id_fields = ("policy",)
    fieldsets = (
        (None, {'fields': ('policy', 'date_of_loss', 'claim_number', 'claim_form', 'claim_estimate', 'claim_bill', 'bill_cost', 'police_report', 'departmental_inquiry_report', 'remarks')}),
        ('Motor', {'fields': ('vehicle_registration_copy', 'driving_license', 'cnic_copy', 'driver_statement',)}),
        ('Property', {'fields': ('fire_brigade_report',)}),
        ('Marine', {'fields': ('bill_of_ladding', 'commercial_invoice')}),
        ('Miscellaneous', {'fields': ('misc_document_1', 'misc_document_2', 'misc_document_3', 'misc_document_4', 'misc_document_5')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = UserInfo
        fields = ('email', 'password', 'name',
                  'id_code', 'is_admin', 'image')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'id_code', 'image', 'phoneNumber', 'birthDate')}),
        ('Permissions', {'fields': ('is_admin', 'is_agent', 'is_client', 'is_surveyor')}),
        ('Remarks', {'fields': ('remarks',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'id_code', 'is_agent', 'is_client', 'is_surveyor', 'password1', 'password2', 'remarks'),
        }),
    )
    search_fields = ('email', 'name', 'id_code')
    ordering = ('email',)
    filter_horizontal = ()
    list_display = ['id', 'email', 'name', 'id_code']


# Now register the new UserAdmin...
admin.site.register(UserInfo, UserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

'''
u = UserInfo.objects.all().get(email='admin@gmail.com')
print(u)
u.set_password('admin')
u.save()
'''