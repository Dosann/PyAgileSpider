# -*- coding: utf-8 -*-
"""
Spyder Editor
#encoding=utf8
This is a temporary script file.
"""

import pcap,dpkt
import re

a=pcap.pcap()
a.setfilter('tcp port 80')
for i,j in a:
    
    #https=re.findall(r(?<=href=").+?(?=")|(?<=href=').+?(?=')|(?<=src=").+?(?=")|(?<=src=').+?(?='),j)
    https=re.findall(r'''https*?://.*?(?=[",',\s])''',j)
    #https=re.findall(r(?<=src=").+?(?="),j)
    if len(https)>0:
        for http in https:
            if ('.js' not in http) and ('.css' not in http) and ('.png' not in http) and ('.jpg' not in http):
                print http
    