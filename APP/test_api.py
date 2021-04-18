def get_str_province():
        list_province = []
        with open('/home/vanhocvp/Code/SmartCall/EVN_bill/APP/process/province.txt', 'r') as f:
            list_province = f.readlines()
        str_province = ''
        for i in list_province:
            str_province += '|' +i.split('\n')[0].lower()
        return str_province[1:]
import re
domain = ['Nghệ An', 'Thanh Hóa', 'Quảng Trị', 'Quảng Bình', 'Thừa Thiên Huế', 'Hà Tĩnh',
'Đà Nẵng', 'Quảng Nam', 'Quảng Ngãi', 'Bình Định', 'Phú Yên', 'Khánh Hòa', 'Ninh Thuận','Bình Thuận',
'Kon Tum', 'Đắk Lắk', 'Gia Lai', 'Đắk Nông','Lâm Đồng']
domain = [i.lower() for i in domain]
print (domain)
x = get_str_province()
print (x)
# k = 'hồ chí minh'
# if re.search(x,k) != None:
#     for i in domain:
#         if i in k:
#             print ('REAL')
#     # if k in domain:
#     #     print ('REAL')
#     # else:
#     #     print ('NO SP')
# else:
#     print ('NO EXIST')

