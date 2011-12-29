

import urllib
import urllib2
import pickle
import cookielib
import getopt
import os
import sys
import sgmllib
#web
#import tornado.ioloop
#import tornado.web


default_dpath="C:\Users\stefan\Documents\Meine Save.TV-Aufnahmen"

class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

def get_file(url,dlFile,fsize,path="."):
    loop = 1    
    existSize = 0
    myUrlclass = myURLOpener()
    if os.path.exists(path+"\\"+dlFile):
        outputFile = open(path+"\\"+dlFile,"ab")
        existSize = os.path.getsize(path+"\\"+dlFile)
        #If the file exists, then only download the remainder
        myUrlclass.addheader("Range","bytes=%s-" % (existSize))
    else:
        outputFile = open(path+"\\"+dlFile,"wb")
    
    webPage = myUrlclass.open(url)
    
    print "Remote Size:  "+ fsize
    print "Local Size:   "+ str(existSize)
    if int(fsize) == existSize:
        loop = 0
        print "File already downloaded"
    
    numBytes = 0
    if existSize==0:
        count=0
    else:
        count=existSize/8192;
    while loop:
        data = webPage.read(8192)
        ret_hook(count,8192,int(fsize))
        if not data:
            break
        outputFile.write(data)
        numBytes = numBytes + len(data)
        count+=1
    
    webPage.close()
    outputFile.close()
    
    

class TitleManager:
    
    
    def __init__(self, verbose=0):
        self.current_item={'Title':"",'SubTitle':"",'Date':"",'Time':"",'Length':"",'Id':0,'Url':"",'Expandable':False}
        self.item_list=[]
    def add_item(self,item):
        self.item_list.append(item)
    def add_title(self,name):                
        self.current_item["Title"]=name
    def set_expandable(self,value):                
        #print "set_expandable"
        self.current_item["Expandable"]=value
    def is_expandable(self):                
        return self.current_item["Expandable"]
    def add_sub_title(self,name):
        self.current_item["SubTitle"]=name
    def is_title_set(self):        
        return self.current_item["Title"]!=""    
    def add_date(self,date):
        self.current_item["Date"]=date
    def add_time(self,date):
        self.current_item["Time"]=date
    def add_length(self,date):
        self.current_item["Length"]=date
    def get_fresh(self):
        #print "***Fresh***"
        print self.current_item
        if self.current_item["Title"]!="":
            self.item_list.append(self.current_item)
            self.current_item={'Title':"",'SubTitle':"",'Date':"",'Time':"",'Length':"",'Id':0,'Url':"",'Expandable':False}    
    def add_url(self,url):
        self.current_item["Url"]=url
        items=url.split('?')
        for i in items:
            if "TelecastID" in  i:
                items=i.split('=')
                break;
        x=0
        for i in items:            
            if "TelecastID" == i:                
                self.current_item["Id"]=items[x+1]
            x+=1;       
    def print_list(self):
            print "##############List printing###########"
            for item in self.item_list:
                print item
                
    
    def ser(self,filename='tm.dat'):
        output = open(filename, 'wb')
        pickle.dump(self.item_list, output)
        output.close()
    def deser(self,filename='tm.dat'):
        if os.path.exists(filename):
                output = open(filename, 'rb')
                self.item_list=pickle.load(output)                
                output.close() 
        



class MyParser(sgmllib.SGMLParser):
    "A simple parser class."
    savevalue=""
    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)                                    
        self.close()
    
    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []
        self.descriptions = []
        self.inside_title = 0
        self.inside_date = 0
        self.inside_state = 0
        self.td_count=0
        self.tm=None;
    def add_tm(self,tm):
        self.tm=tm;
       
    
    def start_a(self,a):
        print "start aaaaa"
        print a
        if len(a)>=1:
            tag,value=a[0]            
            if tag == "href":
                if "TelecastID" in value:
                    print "TAG: "+tag+ "   "+value
                    self.tm.add_url(value)
            if tag == "class" and 'toggle-serial-link':
                self.tm.set_expandable(True);
                
             
        print "end aaaaa"
      
    def end_a(self):
        print "*****end a*****"

    def start_tr(self,a):
        print "////////////////////////////TR start****"        
        print a
        print "////aaaaaaaaaaaaaaaaaaaaaaaaaaaa****"
        
    def end_tr(self):
        print "////////////////////////////TR END*****"

    def start_td(self,a):                
        print "#######td_start--------"
        print a
        if len(a)==1:
            t=a[0];
            tag,type=t
        else:
            tag=None;
        self.td_count+=1;
        print "self.td_count: " +str(self.td_count)
        print a
        
        if  self.td_count==4:            
            print "------title_start--------"
            self.inside_title=1
        if tag=='class' and type=='state':            
            print "------state--------"
            self.inside_state= 1
        if  self.td_count==6:            
            print "------date--------"
            self.inside_date = 1
        
                
        
    def handle_endtag(self,tag,method):
        print "end tag**** "+tag
        if tag =="tr":       
            self.td_count=0;
        if tag =="td" and self.inside_title==1:
            print "------title_end--------"
            self.inside_title=0
        if tag =="td" and self.inside_date==1:
            print "------date_end--------"
            self.inside_date=0
        if tag =="td" and self.inside_state==1:
            print "------state_end--------"
            self.inside_state=0
                
        
    def end_td(self):
        print "#######td_end--------"
        
    
    
    def handle_td(self, data):
        if self.inside_title==1:            
            print "td++++++++ "+data
    
    def handle_data(self, data):
        "Handle the textual 'data'."
        if "Lost" in data:
            print data
        if self.inside_title==1:
            print "title++++++++ "+data;            
            
            cleaned_data=data.replace("\r"," ")
            cleaned_data=cleaned_data.replace("\n"," ")
            
            l=len(cleaned_data)
            cleaned_data=cleaned_data.replace("  "," ")
            while l!=len(cleaned_data):
                l=len(cleaned_data)
                cleaned_data=cleaned_data.replace("  "," ")            
                    
            
            if len(cleaned_data)>1:                                
                if self.tm.is_expandable()==False:
                    if self.tm.is_title_set()==False:
                        print "clean title++++++++ "+cleaned_data;                                                   
                        self.tm.add_title(cleaned_data);                        
                    else:                        
                        print "clean subtitle++++++++ "+cleaned_data;                            
                        self.tm.add_sub_title(cleaned_data);
                else:
                    self.tm.add_title(cleaned_data);
                    self.tm.get_fresh()
                
                
                
        if self.inside_date==1:
            print "date++++++++ "+data
            cleaned_data=data.replace(" ","")
            cleaned_data=cleaned_data.replace("\r","")
            cleaned_data=cleaned_data.replace("\n","")
            
            cleaned_data=cleaned_data.replace(")","")
            cleaned_data=cleaned_data.replace("|"," ")
            cleaned_data=cleaned_data.replace("("," ")
            items=cleaned_data.split(" ");
            if(len(items)==3):
                self.tm.add_date(items[0])
                self.tm.add_time(items[1])
                self.tm.add_length(items[2])                    
                self.tm.get_fresh()            
        """                    
        if self.inside_state==1:
            print "state++++++++ "+data
        """
            
            

    def get_hyperlinks(self):
        "Return the list of hyperlinks."

        return self.hyperlinks

    def get_descriptions(self):
        "Return a list of descriptions."

        return self.descriptions
    
        
        



header = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9b4) Gecko/2008030318 Firefox/3.0b4', 'Accept-Encoding': 'deflate', 'Accept-Charset': 'utf-8'}
data=""

listoflist=[]
downl={}


def ser_list():
        global listoflist;
        output = open('ser.dat', 'wb')
        pickle.dump(listoflist, output)
        output.close()

def ser_down():
        global downl;
        output = open('down.dat', 'wb')
        pickle.dump(downl, output)
        output.close()


def deser_down():
        global downl;
        if os.path.exists('down.dat'):
                output = open('down.dat', 'rb')
                downl=pickle.load( output)
                output.close()

def deser_list():
        global listoflist;
        if os.path.exists('ser.dat'):
                output = open('ser.dat', 'rb')
                listoflist=pickle.load( output)
                output.close()

        



def get_TelecastID(str):
    s=str.split('&')
    for i in s:
        if "TelecastID" in i:
            id= i.split('=')[2]
            return  id.split('"')[0]
            
    return ""
    
g_count=0
def get_settings():
    global g_count
    request = urllib2.Request("http://www.save.tv/STV/M/obj/user/usEdit.cfm", None, header)
    url = urllib2.urlopen(request)    
    html = url.read()    
    f=open("set_"+str(g_count)+".txt","w")
    f.write(html)
    g_count+=1;
    f.close() 
    url.close()

    
def get_durl(TelecastID):
    mobile='4004_1279453091276'
    highdef='2209_1279380457512'
    flash="4728_1290356320883"    
    param0='number:'+str(TelecastID)
    durl=""
    print param0
#GetAdFreeAvailable
#GetDownloadUrl
#number:0 means high qual
#number:1 mean low qual
    
                                
    data=urllib.urlencode({'ajax':'true','c0-id':flash,'clientAuthenticationKey':'','c0-methodName':'GetDownloadUrl','c0-param0':param0,'c0-param1':'number:0','c0-param2':'boolean:true','c0-scriptName':'null','callCount':1});
    request = urllib2.Request("http://www.save.tv/STV/M/obj/cRecordOrder/croGetDownloadUrl.cfm?null.GetDownloadUrl", data, header)
    url = urllib2.urlopen(request)
    html = url.read()    
    print html
    split =html.split(',')
    for line in split:
        if "http://" in line:        
            durl=line;        
            durl=durl.strip('\'')
            return  durl
    url.close()
    
    return durl

""""
ajax=true&clientAuthenticationKey=&callCount=1&c0-scriptName=null&c0-methodName=GetVideoEntries&c0-id=345_1324907842646 &c0-param0=string:1&c0-param1=string:&c0-param2=string:1&c0-param3=string:96987&c0-param4=string:1&c0-param5=string:0&c0-param6=string:1&c0-param7=string:0&c0-param8=string:1&c0-param9=string:&c0-param10=string:Futurama&c0-param11=string:19&c0-param12=string:toggleSerial&xml=true&extend=function (object) { for (property in object) { this[property] = object[property]; } return this; }&
ajax=true&clientAuthenticationKey=&callCount=1&c0-scriptName=null&c0-methodName=GetVideoEntries&c0-id=5214_1324910267751&c0-param0=string:1&c0-param1=string:&c0-param2=string:1&c0-param3=string:96987&c0-param4=string:1&c0-param5=string:0&c0-param6=string:1&c0-param7=string:0&c0-param8=string:1&c0-param9=string:&c0-param10=string:Tatort&c0-param11=string:18&c0-param12=string:toggleSerial&xml=true&extend=function (object) {
"""

def get_expand_data(str):
    
    
    #ajax=true&clientAuthenticationKey= &callCount=1&c0-scriptName=null&c0-methodName=GetVideoEntries&c0-id=345_1324907842646&c0-param0=string:1& c0-param1=string:&c0-param2=string:1&c0-param3=string:96987&c0-param4=string:1&c0-param5=string:0&c0-param6=string:1&c0-param7=string:0&c0-param8=string:1&c0-param9=string:&c0-param10=string:Futurama&c0-param11=string:19&c0-param12=string:toggleSerial&xml=true&extend=function (object) { for (property in object) { this[property] = object[property]; } return this; }&
    data=urllib.urlencode({'ajax':'true','clientAuthenticationKey':'','callCount':'1','c0-scriptName':'null','c0-methodName':'GetVideoEntries','c0-id':'345_1324907842646','c0-param0':'string:1','c0-param1':'string','c0-param2':'string:1','c0-param3':'string:96987','c0-param4':'string:1','c0-param5':'string:0','c0-param6':'string:1','c0-param7':'string:0','c0-param8':'string:1','c0-param9':'string:','c0-param10':'string:'+str,'c0-param11':'string:19','c0-param12':'string:toggleSerial','xml':'True'});                                    
    #data=urllib.urlencode({'ajax':'true','c0-id':flash,'clientAuthenticationKey':'','c0-methodName':'GetDownloadUrl','c0-param0':param0,'c0-param1':'number:0','c0-param2':'boolean:true','c0-scriptName':'null','callCount':1});
    print "zzzzzzzzzzzzzzzzzz"
    request = urllib2.Request("http://www.save.tv/STV/M/obj/user/usShowVideoArchiveLoadEntries.cfm?null.GetVideoEntries", data, header)
    url = urllib2.urlopen(request)
    html = url.read()    
    print html    
    url.close()
    print "zzzzzzzzzzzzzzzzzz"
    return html
    
    #return durl


def login(id,passw):
    global header
    global data
    
    cookies = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
    urllib2.install_opener(opener)    
    login_url="https://www.save.tv/STV/M/Index.cfm?sk=PREMIUM"
    data = urllib.urlencode({'sUsername': id, 'sPassword': passw, 'image.x': 0, 'image.y': 0, 'image': 'Login'})
    request = urllib2.Request(login_url, data, header)
    url = urllib2.urlopen(request)
    html = url.read()
    url.close()

def getArchive(page):
        if page==0:
                data = ""
        else:
                data = urllib.urlencode({'iPageNumber': page, 'bLoadLast': 1})
        request = urllib2.Request("http://www.save.tv/STV/M/obj/user/usShowVideoArchive.cfm", data, header)
        url = urllib2.urlopen(request)
        #html = url.readlines()
        html = url.read()        
        url.close()
        return html

        

        
        
def ret_hook(block_count,block_size,total):
    #print  str(block_size*block_count) + " " +str(total)
    if block_count>0:
        per=int(((float(block_size)*float(block_count))/float(total))*100.00)
        print 'Downloading File [%d%%]\r'%per,
        

def getfilename(info):        
        i=info.split(" ");
        filename=""
        length=""
        x=0
        for e in i:
            if "Content-Length" in e:
                length=i[x+1]
                length=length.replace(" ","")
                items=length.split('\r')
                length=items[0]                
            x+=1
        
        
        for e in i:
                if "filename=" in e:                        
                        i=e.split("=");
                        filename_with_r=i[1]
                        filename_without_r=filename_with_r.split('\r')
                        filename=  filename_without_r[0]
                        
        return filename,length;
        

        
def get_remote_filename_and_size(durl):
        f=urllib.urlopen(durl)
        info= str(f.info())       
        fname,fsize=getfilename(info)        
        f.close()
        return fname,fsize
        
        

def usage():
        print "-x  Username Password| data will be stored in pass"
        print "-p -i database | parse save.tv and store information in database"
        print "-d  date -i input_db -o output_db | extract movies from the given date from one db and add them in the next"
        print "-n name -i input_db -o output_db | extract movies from the given name from one db and add them in the next"
        print "-u  -i input_db -o output_db | extract non sub title movies from the given name from one db and add them in the next"
        print "-w -o out_db | download movies"
        print "-l -o out_db | print download links"
        print "-s -o out_db | show_db"

def ser_secrets(secrets):
    output = open("secrets", 'wb')
    pickle.dump(secrets, output)
    output.close()
def deser_secrets():
        if os.path.exists("secrets"):
                output = open("secrets", 'rb')
                secrets=pickle.load(output)                
                output.close()
                return secrets
        else:
            return {'Username':'','Password':''} 




try:
    opts, args = getopt.getopt(sys.argv[1:], "uxspi:o:d:n:wl",[])
except getopt.GetoptError, err:    
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

"""
secrets=deser_secrets()
login(secrets["Username"],secrets["Password"]);
get_settings()
sys.exit(1)
"""
in_db=""
out_db=""
parse=False
down=False
list=False
show=False
subtitle=False
date=""
name=""
secrets=deser_secrets()
for o, a in opts:
    if o == "-x" and len(sys.argv)==4:
        secrets["Username"]=sys.argv[2]
        secrets["Password"]=sys.argv[3]   
        ser_secrets(secrets)    
        sys.exit(0) 
    elif o == "-p":
        parse = True        
    elif o == "-w":
        down=True        
    elif o in "-i":
        in_db=a;
    elif o in "-d":
        date=a;
    elif o in "-n":
        name=a;
    elif o in "-l":
        list=True
    elif o in "-s":
        show=True
    elif o in "-u":
        subtitle=True    
    elif o in "-o":
        out_db=a;
    else:
        assert False, "unhandled option"
secrets=deser_secrets()

if secrets["Username"]=="" or secrets["Password"]=="":
    print "missing SECRETS!!!!"
    sys.exit(-1)
    

if parse==True and (in_db==""):
    usage();
    sys.exit(2)

if show==True and (out_db==""):
    usage();
    sys.exit(2)

if date!="" and (in_db=="" or out_db==""):
    usage();
    sys.exit(2)
if subtitle and (in_db=="" or out_db==""):
    usage();
    sys.exit(2)

if name!="" and (in_db=="" or out_db==""):
    usage();
    sys.exit(2)


if down and (out_db=="" ):
    usage();
    sys.exit(2)
if list and (out_db=="" ):
    usage();
    sys.exit(2)




tm=TitleManager();
        


        
if parse:
           

        login(secrets["Username"],secrets["Password"]);
        i=1
        
        
        while 1:
                print "Parsing page "+str(i)+" !"
                html=getArchive(i)        
                print html
                html2=getArchive(i+1)                
                #print    len(html)
                #print    len(html2)
                if len(html)==len(html2):
                        break;
                myparser = MyParser()
                myparser.add_tm(tm);
                myparser.parse(html)
                
                myparser = MyParser()
                myparser.add_tm(tm);
                myparser.parse(html2)                
                i=i+1
                break;
        print "+++++++++++++++++++finish"
        tm.print_list();
        if tm!=None:
            for item in tm.item_list:
                print item
                if item["Expandable"]:        
                    html=get_expand_data(item["Title"])
                    html=html.replace("\\","")                                         
                    myparser.parse(html)
                    tm.item_list.remove(item)        
        tm.print_list();
        tm.ser(in_db);
        


elif show:     
        tm_temp=TitleManager();        
        tm_temp.deser(out_db);
        for item in tm_temp.item_list:    
            print "############################"        
            print "Title: "+ item["Title"]
            print "SubTitle: "+item["SubTitle"]
            print "Date: "+item["Date"]
            print "Len: "+item["Length"]
            print "############################"

elif subtitle:     
        tm.deser(out_db);
        tm_temp=TitleManager();
        tm_temp.deser(in_db);
        login(secrets["Username"],secrets["Password"]);
        for item in tm.item_list:            
            if item["SubTitle"]=="":
                b_not_add=False
                for temp_item in tm_temp.item_list:
                    if item["Title"]==temp_item["Title"]:
                        b_not_add=True
                if b_not_add==False:
                    print item["Title"]                
                    print item["Date"]                
                    tm_temp.add_item(item);
        tm_temp.ser(in_db);



elif date!="":
        tm.deser(out_db);
        tm_temp=TitleManager();
        tm_temp.deser(in_db);
        login(secrets["Username"],secrets["Password"]);
        for item in tm.item_list:            
            if item["Date"]==date:
                print item["Title"]
                print item["SubTitle"]
                print item["Date"]                
                tm_temp.add_item(item);
        tm_temp.ser(in_db);
        
elif name!="":
        tm.deser(out_db);
        tm_temp=TitleManager();
        tm_temp.deser(in_db);
        login(secrets["Username"],secrets["Password"]);
        for item in tm.item_list:            
            if sys.argv[2] in item["Title"]:
                print item["Title"]
                print item["SubTitle"]
                print item["Date"]                
                tm_temp.add_item(item);
        tm_temp.ser(in_db);
                
        
elif down:
        tm_temp=TitleManager();        
        tm_temp.deser(out_db);        
        login(secrets["Username"],secrets["Password"]);
        for item in tm_temp.item_list:
                #login(secrets["Username"],secrets["Password"]);                
                print item["Title"]
                print item["SubTitle"]
                print item["Date"]
                durl=get_durl(item["Id"])
                print "Download url: "+durl
                fname,fsize=get_remote_filename_and_size(durl)
                #if "375119" not in fname:
                get_settings()
                print durl
                print "file: "+fname
                print "size: "+fsize
                if(fsize!="" and fname !=""):                    
                    get_file(durl,fname,fsize,default_dpath)
                else:
                    print "Sorry cannot get name for file try it later"               
                
        
            
            
        
        """
        deser_list();
        deser_down();
        getdownloadurl_all(None)
        ser_down()
        """


        
        
else:
        usage()
        sys.exit(-2)


sys.exit(0);



