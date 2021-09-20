from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal

def getMarinePdfData(path):

    plcy_data_list = [
        {'field_name': 'Certificate No.', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}},
        {'field_name': 'Issue Date', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}},
        {'field_name': 'Insured', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}},
        {'field_name': 'Agent / Broker', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}},
        {'field_name': 'L / C No ', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}},
        {'field_name': 'B/L  No.', 'data': {'field_x1_crdnt': -1, 'field_y0_crdnt': -1, 'field_y1_crdnt': -1}}
    ]

    myData = {'Certificate No.': '', 'Issue Date': '', 'Insured': '', 'Agent / Broker': '', 'L / C No ': '', 'B/L  No.': ''}

    i = 0
    y = 0
    document = open(path, 'rb')
    #Create resource manager
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(document):
        if i>=6 and y>=6:
            break
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        for element in layout:
            if i>=6:
                break
            if isinstance(element, LTTextBoxHorizontal):
                #print(element)
                field_name = element.get_text().replace('\n', '')
                field_x1 = element.bbox[2]
                field_y0 = element.bbox[1]
                field_y1 = element.bbox[3]


                for plcy_data in plcy_data_list:
                    if plcy_data['field_name'] == field_name:
                        plcy_data['data']['field_x1_crdnt'] = field_x1
                        plcy_data['data']['field_y0_crdnt'] = field_y0
                        plcy_data['data']['field_y1_crdnt'] = field_y1
                        i = i+1
                        #print('field name is %s, field_x1 = %f, field_y0 = %f, field_y1 = %f' % (field_name, field_x1, field_y0, field_y1))
                        break
        #'''
        #print('\n')
        for element in layout:
            if y>=6:
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
                            y = y+1
                            #print(element)
                            break
        #'''
    final_data = list(myData.values())
    return final_data
                    
                
