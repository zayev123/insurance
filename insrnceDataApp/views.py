from pdf_extracters.general_extracter import getGeneralPdfData
from insrnceDataApp.models import Category, Policy, Policy_pdf, UserInfo
from insrnceDataApp.serializers import ExcelSrlzr, PlcyToClntSrlzr, PolicyPdfSrlzr, PolicySrlzr
from rest_framework.views import APIView
from rest_framework.response import Response
import os


from datetime import datetime

from pdf_extracters.marine_extracter import getMarinePdfData

import openpyxl

from django.db.models import Q
from datetime import date, timedelta

# Create your views here.
class PolicyUploadView(APIView):
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    '''
    serializer_class = PolicyPdfSrlzr

    def post(self, request, *args, **kwargs):
        expiry = ''
        policyPdf = request.data['policy_pdf']
        categ = Category.objects.get(id = request.data['category'])
        strCateg = categ.category_name

        temp_policy_pdf = Policy_pdf.objects.create(
                policy_pdf_file = policyPdf,
            )
        policy_path = temp_policy_pdf.policy_pdf_file.path
        if strCateg == 'marine':
            myfinalData = getMarinePdfData(policy_path)
        else:
            myfinalData = getGeneralPdfData(policy_path)
            periods = myfinalData[4].split()
            expiry = periods[3]

        #'''
        my_policy_number = myfinalData[0]
        temp_policy_pdf.delete()
        os.remove(policy_path)
        agCode = myfinalData[3]
        if UserInfo.objects.all().filter(id_code = agCode).exists():
            myAgent = UserInfo.objects.get(id_code = agCode)
        else:
            myResponse = Response({'message': 'agent does not exist; first create agent in admin panel'})
            if myResponse.status_code == 200:
                return myResponse
            else:
                return Response({'message': 'Failed'})
        if Policy.objects.all().filter(policy_number = my_policy_number).exists():
            new_policy = Policy.objects.get(policy_number = my_policy_number)
            new_policy.policy_pdf = policyPdf
        else:

            new_policy = Policy.objects.create(
                category = categ,
            )
        new_policy.policy_pdf = policyPdf



        #expiry_date = datetime.strptime(expiry, '%d-%m-%Y').strftime('%Y-%m-%d')
        dateFormats = ['%d-%m-%Y', '%d/%m/%Y', '%d-%b-%y']

        if expiry != '':
            print('ere')
            for dateFormat in dateFormats:
                try:
                    print('here')
                    datetime.strptime(expiry, dateFormat)
                    expiry_date = datetime.strptime(expiry, dateFormat).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    pass
        
        date_string = myfinalData[1]
        if date_string != '':
            for dateFormat in dateFormats:
                try:
                    datetime.strptime(date_string, dateFormat)
                    trueFormat = dateFormat
                    myDate = datetime.strptime(date_string, dateFormat).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    pass

        if strCateg == 'marine':
            new_policy.l_c_number = myfinalData[4]
            new_policy.b_l_number = myfinalData[5]
        elif expiry != '':
            new_policy.policy_expiry_date = expiry_date

        new_policy.policy_number = my_policy_number
        new_policy.agent = myAgent

        if date_string != '':
            new_policy.policy_issue_date = myDate
        new_policy.client_name = myfinalData[2]

        new_policy.save()
        newSrlzdPolicy = PolicySrlzr(new_policy).data

        #'''
        myResponse = Response({'message': 'success', 'data': newSrlzdPolicy})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})

# 1 = branch ref code
# 4 = main account
# 5 = doc date
# 7 = plcy_number
# 8 = end-claim-number
# 11 = client_id_code
# 12 = client_name
# 16 = agent_code
# 19 = agent_name
# 20 = category
# 21 = premium
# 22 = outstanding
class XclOtStndgUpldVw(APIView):

    serializer_class = ExcelSrlzr

    def post(self, request, *args, **kwargs):
        xclWb = request.data['myExcel']

        wb = openpyxl.load_workbook(xclWb)
        users = UserInfo.objects.all()
        myAgent = users.get(id = 1)
        myClient = users.get(id = 1)
        policies = Policy.objects.all()
        for ws in wb:
            for row in ws.iter_rows():
                if row[20].value == 'M1':
                    if policies.filter(policy_number = row[7].value).exists():
                        policy = policy.get(policy_number = row[7].value)
                        policy.branch_ref_code = row[1].value
                        policy.main_acc_code = row[4].value
                        policy.end_claim_number = row[8].value
                        if policy.client == None:
                            if users.filter(id_code = row[11].value).exists():
                                client = users.get(id_code = row[11].value)
                                policy.client = client
                            else:
                                newClient = UserInfo.objects.create(
                                    email = str(row[11].value) + '@adamji.com',
                                    name = str(row[12]).value,
                                    id_code = str(row[11].value),
                                    is_client = True
                                )
                                policy.client = newClient
                        policy.premium = row[21].value
                        policy.outstanding = row[22].value
                    elif row[16].value != None and row[16].value != '':
                        if myAgent.id_code == row[16].value or users.filter(id_code = row[16].value).exists():
                            if myAgent.id_code != row[16].value:
                                myAgent = users.get(id_code = row[16].value)
                            
                            if myClient.id_code != row[11].value:
                                if users.filter(id_code = row[11].value).exists():
                                    myClient = users.get(id_code = row[11].value)
                                else:
                                    myClient = UserInfo.objects.create(
                                        email = str(row[11].value) + '@adamji.com',
                                        name = str(row[12].value),
                                        id_code = str(row[11].value),
                                        is_client = True
                                    )
                            policy.objects.create(
                                policy_number = row[7].value,
                                client = myClient,
                                client_name = row[12].value,
                                agent = myAgent,
                                branch_ref_code = row[1].value,
                                main_acc_code = row[4].value,
                                end_claim_number = row[8].value,
                                premium = row[21].value,
                                outstanding = row[22].value,
                            )
                        


        myResponse = Response({'message': 'success', 'data': 'policies_updated'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class GetExpiryView(APIView):
    def get(self, request, *args, **kwargs):
        today = date.today()
        till_next_week = today + timedelta(days=8)
        policies = Policy.objects.all().exclude(policy_expiry_date = None)

        expiries = policies.filter(policy_expiry_date__range = [
            today, till_next_week]).order_by('policy_expiry_date')

        srlzdExpirs = PlcyToClntSrlzr(expiries, many = True).data

        myResponse = Response({'message': 'Policies Expiring Within Seven Days From Today', 'data': srlzdExpirs})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})