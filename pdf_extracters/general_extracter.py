from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal


def getGeneralPdfData(path):


    plcy_data_list = [
        {'field_name': 'Policy No.', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}, 'check' : False},
        {'field_name': 'Issue Date', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}, 'check' : False},
        {'field_name': 'Insured', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}, 'check' : False},
        {'field_name': 'Agent / Broker', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}, 'check' : False},
        {'field_name': 'Period of Insurance', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}, 'check' : False},
    ]

    myData = {'Policy No.': '', 'Issue Date': '', 'Insured': '', 'Agent / Broker': '', 'Period of Insurance': ''}

    document = open(path, 'rb')
    #Create resource manager
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    fLimit = 5
    fCount = 0
    vLimit = fLimit
    vCount = 0

    for page in PDFPage.get_pages(document):
        if fCount>=fLimit and vCount>=vLimit:
            break
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        for element in layout:
            for pluData in plcy_data_list:
                if not pluData['check']:
                    break
                else:
                    fCount = fCount + 1
            if fCount>=fLimit:
                break
            else:
                fCount = 0
            if isinstance(element, LTTextBoxHorizontal):
                print(element)
                #'''
                field_name = element.get_text().replace('\n', '')
                field_x1 = element.bbox[2]
                field_y0 = element.bbox[1]
                field_y1 = element.bbox[3]


                for plcy_data in plcy_data_list:
                    if plcy_data['field_name'] == field_name:
                        plcy_data['data']['field_x1_crdnt'] = field_x1
                        plcy_data['data']['field_y0_crdnt'] = field_y0
                        plcy_data['data']['field_y1_crdnt'] = field_y1
                        plcy_data['check'] = True
                        print('field name is %s, field_x1 = %f, field_y0 = %f, field_y1 = %f' % (field_name, field_x1, field_y0, field_y1))
                        break
                    elif field_name == 'Insured Name' or field_name == 'Customer Name' or field_name == 'Insured :' or field_name == 'Customer :Insured':
                        if plcy_data['field_name'] == 'Insured':
                            plcy_data['field_name'] = field_name
                            replacement = {"Insured": field_name}

                            for k, v in list(myData.items()):
                                myData[replacement.get(k, k)] = myData.pop(k)

                            plcy_data['data']['field_x1_crdnt'] = field_x1
                            plcy_data['data']['field_y0_crdnt'] = field_y0
                            plcy_data['data']['field_y1_crdnt'] = field_y1
                            plcy_data['check'] = True
                            print('field name is %s, field_x1 = %f, field_y0 = %f, field_y1 = %f' % (field_name, field_x1, field_y0, field_y1))
                            break
                    elif field_name == 'Period of Insurance :':
                        if plcy_data['field_name'] == 'Period of Insurance':
                            plcy_data['field_name'] = field_name
                            replacement = {"Period of Insurance": field_name}

                            for k, v in list(myData.items()):
                                myData[replacement.get(k, k)] = myData.pop(k)
                            plcy_data['data']['field_x1_crdnt'] = field_x1
                            plcy_data['data']['field_y0_crdnt'] = field_y0
                            plcy_data['data']['field_y1_crdnt'] = field_y1
                            plcy_data['check'] = True
                            print('field name is %s, field_x1 = %f, field_y0 = %f, field_y1 = %f' % (field_name, field_x1, field_y0, field_y1))
                            break
                            
                #'''
        #'''
        #print('\n')
        for element in layout:
            if vCount>=vLimit:
                break
            if isinstance(element, LTTextBoxHorizontal):
                raw_value = element.get_text()
                if raw_value != ':\n' and raw_value != ':\n:\n':
                    value = raw_value.replace('\n', '')
                    value_x0 = element.bbox[0]
                    value_y0 = element.bbox[1]
                    value_y1 = element.bbox[3]


                    for new_plcy_data in plcy_data_list:
                        field_x1 = new_plcy_data['data']['field_x1_crdnt']
                        field_y0 = new_plcy_data['data']['field_y0_crdnt']
                        field_y1 = new_plcy_data['data']['field_y1_crdnt']
                        if field_x1 != -1 and (value_x0 - field_x1) > 1 and (abs(field_y0 - value_y0) < 5 or abs(field_y1 - value_y1) < 5) and (value_x0 - field_x1) < 80:
                            myData[new_plcy_data['field_name']] = value
                            vCount = vCount+1
                            break
        #'''
    #print(plcy_data_list)
    #print(myData)
    final_data = list(myData.values())
    return final_data