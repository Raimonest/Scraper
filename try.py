import requests
import zipfile
import os
import datetime

##from xmldiff import main
import xml.etree.ElementTree as ET

#download
url = 'https://www.cbr.ru/s/newbik'
myfile = requests.get(url)
currentdir=os.getcwd()
zipdir=currentdir + "\download.zip"
archivo=open(zipdir, "wb")
archivo.write(myfile.content)


#remove old downloads
destoday = currentdir + "\downloads"
if os.path.exists(destoday):
    for file in os.scandir(destoday):
        os.remove(destoday+"\\" + file.name)
    os.rmdir(destoday)

#unzip
with zipfile.ZipFile("download.zip","r") as z:
    z.extractall("downloads//")

#copy download to old
with zipfile.ZipFile("download.zip","r") as z:
    z.extractall("old//")

#get today's file name and complete directory

for file in os.scandir(destoday):
    pass
todayf=file.name
destodaycompl = destoday + "\\" + todayf



#destination directory
destold = currentdir + "\old"



#identify last old file, whith datetime
found=False
i=1
date=datetime.datetime.now()
date-=datetime.timedelta(1)#date=yesterday
d=str(date.year)+str(date.month).zfill(2)+str(date.day).zfill(2)
while i < 1000 and not found:
    for file in os.scandir(destold):
        if found!=True and file.name[:8].isnumeric() and file.name[-4:]=='.xml':
            lastf=file.name
            #print(i)
            #print(lastf)#if there is an open excel it has an error
            #print(int(d))
            if int(lastf[:8])== int(d):
                found=True
                lastfile=lastf
                #print(found)
    i+=1
    date-=datetime.timedelta(1)
    d=str(date.year)+str(date.month).zfill(2)+str(date.day).zfill(2)


                
#https://pypi.org/project/xmldiff/
#https://xmldiff.readthedocs.io/en/stable/api.html#the-edit-script

'''
#comparefiles
if found != False:
    destoldcompl = destold + str("\\") + lastfile
    print(destoldcompl)
    print(destodaycompl)
    #print(main.diff_files(destoldcompl,destodaycompl))
    
    tree1 = ET.parse(destoldcompl)
    root1 = tree1.getroot()
    tree2 = ET.parse(destodaycompl)
    root2 = tree2.getroot()
    c=0
    for child in root1:
        if c<10:
            print ( child[0].attrib)

        c+=1
else:
    print("There are no old files to compare to!!! Today's file was saved, tomorrow you can compare already or now look for old files and add them to folder named 'old' and try again")
'''

destination = destold + "\\" + todayf

tree1 = ET.parse(destination)
root1 = tree1.getroot()


d={}
headers=['BIC']
for child in root1:
    
    BIC=child.items()[0][1]
    d[BIC]={}
    for atr in child[0].attrib:
        if atr not in headers:
            headers.append(atr)
        d[BIC][atr]=child[0].attrib[atr]
    d[BIC]['BIC']=BIC

        
import pandas as pd
path=destination[:-4]+".xlsx"
df = pd.DataFrame(d, index= headers).transpose()
fecha=todayf[:8]#str(date.year)+str(date.month).zfill(2)+str(date.day).zfill(2)
writer = pd.ExcelWriter(path)
df.to_excel(writer,sheet_name=fecha)







#old file to compare
destoldcompl = destold + "\\" + lastfile
tree2 = ET.parse(destoldcompl)
root2 = tree2.getroot()


d2={}
headers2=['BIC']
for child in root2:
    
    BIC=child.items()[0][1]
    d2[BIC]={}
    for atr in child[0].attrib:
        if atr not in headers2:
            headers2.append(atr)
        d2[BIC][atr]=child[0].attrib[atr]
    d2[BIC]['BIC']=BIC

#compare
new={}
modified={}
modif=[]
deleted={}
    
for BIC in d:
    if BIC in d2:
        dicc={}
        for atr in d[BIC]:
            dicc[atr]=d[BIC][atr]
            
            if atr in d2[BIC]:
                if d[BIC][atr] != d2[BIC][atr]:
                    #if the field is modified
                    modified[BIC]=dicc
                else:
                    pass
                    #the field is the same in both
            else:
                #field wasn't in the old file
                modified[BIC]=dicc



                
            
    else:
        #company not in old file
        new[BIC]=d[BIC]

for BIC in d2:
    if BIC not in d:
        #company not in new file
        deleted[BIC]=d2[BIC]

    else:
        dicc={}
        for atr in d2[BIC]:
            dicc[atr]=d2[BIC][atr]
            
            if atr not in d[BIC]:
                #field wasn't in the new file
                modified[BIC]=dicc

       
dfnew = pd.DataFrame(new, index= headers)
dfnew.to_excel(writer,sheet_name='new')


dfmod = pd.DataFrame(modified, index= headers)
dfmod.to_excel(writer,sheet_name='modified')


dfdel = pd.DataFrame(deleted, index= headers)
dfdel.to_excel(writer,sheet_name='deleted')
writer.save()
writer.close()
