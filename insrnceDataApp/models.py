from django.db import models
from adamInsrnceMngmnt.myStorage import OverwriteStorage
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.html import format_html

# Create your models here.
class UserInfoManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserInfo(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    id_code = models.CharField(max_length=200, blank=True, null=True, unique=True,)
    is_admin = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_surveyor = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='profile_images', blank=True, null=True, storage=OverwriteStorage())
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    phoneNumber = models.CharField(max_length=30, blank=True, null=True)
    socialImageUrl = models.CharField(max_length=500, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    remarks= models.TextField(blank=True, null=True,)

    objects = UserInfoManager()

    USERNAME_FIELD = 'email'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        verbose_name_plural = "      1. Agents, surveyers and clients"

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name_plural = "     2. Categories"

class Policy_pdf(models.Model):
    policy_pdf_file = models.FileField(upload_to='temp_policies', blank=True, null=True, storage=OverwriteStorage())

class Policy(models.Model):
    category = models.ForeignKey(Category, related_name='policies', on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100, blank=True, null=True,)
    policy_issue_date = models.DateField(blank=True, null=True)
    client = models.ForeignKey(UserInfo, related_name='clientPolicies', on_delete=models.CASCADE, blank=True, null=True)
    client_name = models.CharField(max_length=100, blank=True, null=True,)
    policy_expiry_date = models.DateField(blank=True, null=True)
    policy_pdf = models.FileField(
        upload_to='policies', blank=True, null=True, storage=OverwriteStorage())
    gross_premium = models.IntegerField(default=0)
    percentage_on_gross_premium_for_comission = models.DecimalField(default=0.0, max_digits=4,decimal_places=2)
    premium = models.IntegerField(default=0)
    personal_comission = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    policy_added_to_system_date = models.DateTimeField(auto_now_add=True)
    branch_ref_code = models.CharField(max_length=100, blank=True, null=True)
    main_acc_code = models.CharField(max_length=100, blank=True, null=True)
    agent = models.ForeignKey(UserInfo, related_name='agentPolicies', on_delete=models.CASCADE, blank=True, null=True)
    end_claim_number = models.CharField(max_length=100, blank=True, null=True,)
    outstanding = models.IntegerField(default=0)
    percentage_premium_paid = models.IntegerField()
    l_c_number = models.CharField(max_length=100, blank=True, null=True,)
    b_l_number = models.CharField(max_length=100, blank=True, null=True,)
    remarks = models.TextField(blank=True, null=True,)
    latest_financial_endorsement = models.OneToOneField('Endorsement', related_name='if_latest_then_policy', blank=True, null=True, on_delete=models.DO_NOTHING)


    def save(self, *args, **kwargs):

        self.personal_comission = (float(self.gross_premium) * float(self.percentage_on_gross_premium_for_comission)/100) * (1-0.18)
        if self.premium != 0:
            if self.outstanding == 0:
                self.outstanding = self.premium
            self.percentage_premium_paid = ((self.premium - self.outstanding)/self.premium)*100
        else:
            self.percentage_premium_paid = -1
        super(Policy, self).save(*args, **kwargs)

    def __str__(self):
        if self.policy_number != None:
            return self.policy_number
        else:
            return str(self.id)

    class Meta:
        verbose_name_plural = "    3. Policies"
        ordering = ['-policy_issue_date']





class Receipt(models.Model):
    policy = models.ForeignKey(Policy, related_name='paymentsRecieved', on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, blank=True, null=True,)
    receipt_pdf = models.FileField(upload_to='receipts', blank=True, null=True, storage=OverwriteStorage())
    receipt_date = models.DateField(blank=True, null=True)
    premium_paid = models.IntegerField()
    edit_premium_paid = models.IntegerField(default=0)
    receipt_added_to_system_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.receipt_number

    def save(self, *args, **kwargs):
        paid_policy = self.policy
        paid_policy.outstanding = paid_policy.outstanding + self.edit_premium_paid - self.premium_paid
        paid_policy.save()
        self.edit_premium_paid = self.premium_paid
        super(Receipt, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # if related field, then also get all its related fields using filter or related name and delete those aswell
        if args and args[0]==True:
            super(Receipt, self).delete()
        else:
            self.policy.outstanding = self.policy.outstanding + self.premium_paid
            self.policy.save()
            super(Receipt, self).delete()

    class Meta:
        verbose_name_plural = "  5. Receipts"
        ordering = ['-receipt_date']

class Endorsement(models.Model):
    policy = models.ForeignKey(Policy, related_name='endorsements', on_delete=models.CASCADE)
    endorsement_number = models.CharField(max_length=100, blank=True, null=True,)
    endorsement_pdf = models.FileField(upload_to='endorsments', blank=True, null=True, storage=OverwriteStorage())
    endorsement_issue_date = models.DateTimeField()
    previous_financial_endorsement = models.OneToOneField('self', related_name='next_financial_endorsement', blank=True, null=True, on_delete=models.DO_NOTHING)
    previous_premium = models.IntegerField(blank=True, null=True)
    new_premium = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True,)
    endorsement_added_to_system_date = models.DateTimeField(auto_now_add=True)

    def link_next_previous(self, next_endo):
        i_previous_financial_endorsement = self.previous_financial_endorsement
        self.previous_financial_endorsement = None
        self.save(True)
        #### STRANGE ####
        next_endo.previous_financial_endorsement = None
        #################
        next_endo.previous_financial_endorsement = i_previous_financial_endorsement
        next_endo.previous_premium = i_previous_financial_endorsement.new_premium
        next_endo.save(True)

    def link_next_none(self, next_endo):
        next_endo.previous_financial_endorsement = None
        # instead of saving it to new_premium, i save it to previus premium
        next_endo.previous_premium = self.previous_premium
        next_endo.save(True)

    def link_del_endo(self, endorsed_policy):
        # first, lets link the previous of this to the next of this:
        if hasattr(self, 'next_financial_endorsement'):
            # if next exists, then clearly, it would be the latest financial date, so i need not change it
            i_next_financial_endorsement = self.next_financial_endorsement
            if self.previous_financial_endorsement != None:
                self.link_next_previous(i_next_financial_endorsement)
            else:
                self.link_next_none(i_next_financial_endorsement)
        else:
            if self.previous_financial_endorsement != None:
                print('whaa')
                i_previous_financial_endorsement = self.previous_financial_endorsement
                self.previous_financial_endorsement = None
                self.save(True)
                difference = i_previous_financial_endorsement.new_premium - endorsed_policy.premium
                endorsed_policy.outstanding = endorsed_policy.outstanding + difference
                endorsed_policy.premium = i_previous_financial_endorsement.new_premium
                endorsed_policy.latest_financial_endorsement = i_previous_financial_endorsement
                endorsed_policy.save()
            else:
                difference = self.previous_premium - endorsed_policy.premium
                endorsed_policy.outstanding = endorsed_policy.outstanding + difference
                endorsed_policy.premium = self.previous_premium
                endorsed_policy.latest_financial_endorsement = None
                endorsed_policy.save()

    def save(self, *args, **kwargs):
        # for each save, just check if it is not already the case
        # for the case if self.new_premium is changed to None but self. previous financial endorement is not non 
        # only enter the code if change is made to the new_premium
        # create a different situation for the equal to case such that it maintains the status quo
        should_skip = False
        conflicting_endo = ''
        isManaged = False
        endo_count = 0
        if args:
            if args[0]:
                should_skip = True
        if self.new_premium != None and not should_skip:
            endorsed_policy = self.policy
            if (self.previous_financial_endorsement!= None and self.previous_financial_endorsement.policy.id != self.policy.id) or (hasattr(self, 'next_financial_endorsement') and self.next_financial_endorsement.policy.id != self.policy.id):
                if self.previous_financial_endorsement!= None and self.previous_financial_endorsement.policy.id != self.policy.id:
                    myPastPol = self.previous_financial_endorsement.policy
                elif hasattr(self, 'next_financial_endorsement') and self.next_financial_endorsement.policy.id != self.policy.id:
                    myPastPol = self.next_financial_endorsement.policy
                self.link_del_endo(myPastPol)
            # to get previous premium
            #if self.previous_financial_endorsement == None:
            myPlcy_financial_endorsements = list(endorsed_policy.endorsements.all().exclude(id = self.id).exclude(new_premium = None))
            if myPlcy_financial_endorsements:
                # need a for loop on top to check everytime if the position has been switched
                for myPlcy_financial_endorsement in myPlcy_financial_endorsements:
                    # meaning its next is not equal to self
                    if myPlcy_financial_endorsement.endorsement_issue_date == self.endorsement_issue_date:
                        conflicting_endo = myPlcy_financial_endorsement.endorsement_number
                        break
                    if myPlcy_financial_endorsement.endorsement_issue_date < self.endorsement_issue_date and self.previous_financial_endorsement != None and self.previous_financial_endorsement.id == myPlcy_financial_endorsement.id:
                        print('ehh here')
                        break 
                    if endo_count == 0:
                        #check first
                        print('am here')
                        if myPlcy_financial_endorsement.endorsement_issue_date < self.endorsement_issue_date and (endorsed_policy.latest_financial_endorsement == None or endorsed_policy.latest_financial_endorsement.id != self.id):
                            self.save(True)
                            print('also here')
                            endorsed_policy.latest_financial_endorsement = self
                            difference = self.new_premium - endorsed_policy.premium
                            endorsed_policy.outstanding = endorsed_policy.outstanding + difference
                            endorsed_policy.premium = self.new_premium
                            endorsed_policy.save()
                        elif endorsed_policy.latest_financial_endorsement.id != myPlcy_financial_endorsement:
                            endorsed_policy.latest_financial_endorsement = myPlcy_financial_endorsement
                            difference = myPlcy_financial_endorsement.new_premium - endorsed_policy.premium
                            endorsed_policy.outstanding = endorsed_policy.outstanding + difference
                            endorsed_policy.premium = myPlcy_financial_endorsement.new_premium
                            endorsed_policy.save()
                    if myPlcy_financial_endorsement.endorsement_issue_date < self.endorsement_issue_date and (self.previous_financial_endorsement == None or self.previous_financial_endorsement.id != myPlcy_financial_endorsement.id):
                        # if some endorsement in the middle is changed and the next endorsement exists
                        isManaged = True
                        if hasattr(self, 'next_financial_endorsement'):
                            self_next_fnncial_endrsmnt = self.next_financial_endorsement
                            if self.previous_financial_endorsement != None:
                                self.link_next_previous(self_next_fnncial_endrsmnt)
                            else:
                                self.link_next_none(self_next_fnncial_endrsmnt)
                            # but what if there is an endorsement also pointing to this myPlcy_financial_endorsement
                        if hasattr(myPlcy_financial_endorsement, 'next_financial_endorsement'):
                            #what if the next is self, well that is already taken care of above
                            prevy_next_financial_endorsement = myPlcy_financial_endorsement.next_financial_endorsement
                            # what is self's next exists, but its previous doesnt exist, in the case where it was added first to the system but lateron the dates changed
                            self.save(True)
                            prevy_next_financial_endorsement.previous_financial_endorsement = self
                            prevy_next_financial_endorsement.previous_premium = self.new_premium
                            prevy_next_financial_endorsement.save(True)
                        self.previous_financial_endorsement = myPlcy_financial_endorsement
                        self.previous_premium = myPlcy_financial_endorsement.new_premium
                        self.save(True)
                        break
                    elif self.endorsement_issue_date < myPlcy_financial_endorsements[-1].endorsement_issue_date and myPlcy_financial_endorsements[-1].previous_financial_endorsement == None:
                        myFutureEndorsement = myPlcy_financial_endorsements[-1]
                        isManaged = True
                        if hasattr(self, 'next_financial_endorsement'):
                            self_next_fnncial_endrsmnt = self.next_financial_endorsement
                            if self.previous_financial_endorsement != None:
                               self.link_next_previous(self_next_fnncial_endrsmnt)
                            else:
                                self.link_next_none(self_next_fnncial_endrsmnt)
                        self.previous_financial_endorsement = None
                        self.previous_premium = 0
                        self.save(True)
                        myFutureEndorsement.previous_financial_endorsement = self
                        myFutureEndorsement.previous_premium = self.new_premium
                        myFutureEndorsement.save(True)
                        break

                    elif myPlcy_financial_endorsement.previous_financial_endorsement != None and myPlcy_financial_endorsement.previous_financial_endorsement.id == self.id and not isManaged:
                        myPlcy_financial_endorsement.previous_premium = self.new_premium
                        myPlcy_financial_endorsement.save(True)
                    endo_count = endo_count + 1
            else:
                self.previous_premium = 0
                self.save(True)
                endorsed_policy.latest_financial_endorsement = self
                difference = self.new_premium - endorsed_policy.premium
                endorsed_policy.outstanding = endorsed_policy.outstanding + difference
                endorsed_policy.premium = self.new_premium
                endorsed_policy.save()
        elif self.previous_premium != None and not should_skip:
            endorsed_policy = self.policy
            self.link_del_endo(endorsed_policy)
            self.previous_premium = None
        if conflicting_endo == '':
            super(Endorsement, self).save()
        return conflicting_endo

    def clean(self):
        if self.save() != '':
            conflicting_endo = self.save()
            myString = 'The assigned endorsement issue date and time are already taken by ' + conflicting_endo + ' of this policy. Assign a different date. If, however, you intend on using the same date, then assign a different time atleast.'
            raise ValidationError(format_html('<span style="color: #cc0033; font-weight: bold; font-size: large;">{0}</span>', myString))

    def delete(self):
        # if related field, then also get all its related fields using filter or related name and delete those aswell
        if self.new_premium != None:
            endorsed_policy = self.policy
            # first, lets link the previous of this to the next of this:
            self.link_del_endo(endorsed_policy)

        super(Endorsement, self).delete()

    def __str__(self):
        return self.endorsement_number
    
    class Meta:
        verbose_name_plural = "   4. Endorsements"
        ordering = ['-endorsement_issue_date']


class Claim(models.Model):
    policy = models.ForeignKey(Policy, related_name='claims', on_delete=models.CASCADE)
    date_of_loss = models.DateField()
    claim_number = models.CharField(max_length=100, blank=True, null=True,)
    claim_form = models.FileField(upload_to='claim_forms', blank=True, null=True, storage=OverwriteStorage())
    claim_estimate = models.IntegerField(blank=True, null=True)
    claim_bill = models.FileField(upload_to='claim_bills', blank=True, null=True, storage=OverwriteStorage())
    bill_cost = models.IntegerField(blank=True, null=True)
    police_report = models.FileField(upload_to='police_reports', blank=True, null=True, storage=OverwriteStorage())
    departmental_inquiry_report = models.FileField(upload_to='inquiry_reports', blank=True, null=True, storage=OverwriteStorage())
    remarks = models.TextField(blank=True, null=True,)
    # motor
    vehicle_registration_copy = models.FileField(upload_to='registration', blank=True, null=True, storage=OverwriteStorage())
    driving_license = models.FileField(upload_to='driving_license', blank=True, null=True, storage=OverwriteStorage())
    cnic_copy = models.FileField(upload_to='cnic_copies', blank=True, null=True, storage=OverwriteStorage())
    driver_statement = models.TextField(blank=True, null=True,)
    # property
    fire_brigade_report = models.FileField(upload_to='fire_reports', blank=True, null=True, storage=OverwriteStorage())
    # marine
    bill_of_ladding = models.FileField(upload_to='laddings', blank=True, null=True, storage=OverwriteStorage())
    commercial_invoice = models.FileField(upload_to='commercial_invoices', blank=True, null=True, storage=OverwriteStorage())
    # miscellaneous
    misc_document_1 = models.FileField(upload_to='misc_docs', blank=True, null=True, storage=OverwriteStorage())
    misc_document_2 = models.FileField(upload_to='misc_docs', blank=True, null=True, storage=OverwriteStorage())
    misc_document_3 = models.FileField(upload_to='misc_docs', blank=True, null=True, storage=OverwriteStorage())
    misc_document_4 = models.FileField(upload_to='misc_docs', blank=True, null=True, storage=OverwriteStorage())
    misc_document_5 = models.FileField(upload_to='misc_docs', blank=True, null=True, storage=OverwriteStorage())


    def __str__(self):
        return self.claim_number
    
    class Meta:
        verbose_name_plural = " 6. Claims"
        ordering = ['-date_of_loss']
