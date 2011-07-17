

import urllib
import urllib2
import pickle
import cookielib
import getopt
import os
import sys
import sgmllib

default_dpath="C:\Users\stefan\Documents\Meine Save.TV-Aufnahmen"

class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

def get_file(url,dlFile,path="."):
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
    
    #If the file exists, but we already have the whole thing, don't download again
    if int(webPage.headers['Content-Length']) == existSize:
        loop = 0
        print "File already downloaded"
    
    numBytes = 0
    if existSize==0:
        count=0
    else:
        count=existSize/8192;
    while loop:
        data = webPage.read(8192)
        ret_hook(count,8192,int(webPage.headers['Content-Length']))
        if not data:
            break
        outputFile.write(data)
        numBytes = numBytes + len(data)
        count+=1
    
    webPage.close()
    outputFile.close()
    
    for k,v in webPage.headers.items():
        print k, "=",v
    print "copied", numBytes, "bytes from", webPage.url

class TitleManager:
    
    
    def __init__(self, verbose=0):
        self.current_item={'Title':"",'SubTitle':"",'Date':"",'Time':"",'Length':"",'Id':0,'Url':""}
        self.item_list=[]
    def add_item(self,item):
        self.item_list.append(item)
    def add_title(self,name):                
        self.current_item["Title"]=name
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
        
        
        if self.current_item["Title"]!="" and self.current_item["Url"]!="":
            self.item_list.append(self.current_item)
            self.current_item={'Title':"",'SubTitle':"",'Date':"",'Time':"",'Length':"",'Id':0,'Url':""}
    def print_list(self):
            print self.item_list
    
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
        self.tm=None;
    def add_tm(self,tm):
        self.tm=tm;
       
    
    def start_a(self,a):
        if len(a)==1:
            tag,value=a[0]
            #if self.inside_a_element==1 and tag == "href":
            if tag == "href" and self.inside_state==1:
                if "TelecastID" in value:
                    print "TAG: "+tag+ "   "+value
                    self.tm.add_url(value)
        
    def end_a(self):
        print "*****end a*****"

    def start_tr(self,a):
        print "////////////////////////////TR start****"
        
    def end_tr(self):
        print "////////////////////////////TR END*****"

    def start_td(self,a):                
        print "#######td_start--------"
        if len(a)==1:
            t=a[0];
            tag,type=t
        if tag=='class' and type=='title':            
            print "------title_start--------"
            self.inside_title=1
        if tag=='class' and type=='state':            
            print "------state--------"
            self.inside_state= 1
        if tag=='class' and type=='date':            
            print "------date--------"
            self.inside_date = 1
        
                
        
    def handle_endtag(self,tag,method):
        print "end tag**** "+tag
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

        if self.inside_title==1:
            #print "title++++++++ "+data;
            
            cleaned_data=data.replace("\r"," ")
            cleaned_data=cleaned_data.replace("\n"," ")
            
            l=len(cleaned_data)
            cleaned_data=cleaned_data.replace("  "," ")
            while l!=len(cleaned_data):
                l=len(cleaned_data)
                cleaned_data=cleaned_data.replace("  "," ")
                
                
            
                    
            
            if len(cleaned_data)>1:
                if self.tm.is_title_set()==False:
                    print "clean title++++++++ "+cleaned_data;                            
                    self.tm.add_title(cleaned_data);
                else:
                    print "clean subtitle++++++++ "+cleaned_data;                            
                    self.tm.add_sub_title(cleaned_data);
                
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
                            
        if self.inside_state==1:
            print "state++++++++ "+data
            
            

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
    

    

    
def get_durl(TelecastID):
    mobile='4004_1279453091276'
    highdef='2209_1279380457512'
    flash="4728_1290356320883"    
    param0='number:'+TelecastID
    durl=""
#GetAdFreeAvailable
#GetDownloadUrl
#number:0 means high qual
#number:1 mean low qual
                                
    data=urllib.urlencode({'ajax':'true','c0-id':flash,'clientAuthenticationKey':'','c0-methodName':'GetDownloadUrl','c0-param0':param0,'c0-param1':'number:0','c0-param2':'boolean:true','c0-scriptName':'null','callCount':1});
    request = urllib2.Request("http://www.save.tv/STV/M/obj/cRecordOrder/croGetDownloadUrl.cfm?null.GetDownloadUrl", data, header)
    url = urllib2.urlopen(request)
    html = url.read()    
    split =html.split(',')
    for line in split:
        if "http://" in line:        
            durl=line;        
            durl=durl.strip('\'')
            return  durl
    url.close()
    return durl

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
        
        for e in i:
                if "filename=" in e:                        
                        i=e.split("=");
                        filename_with_r=i[1]
                        filename_without_r=filename_with_r.split('\r')
                        return  filename_without_r[0]
                        
                        
        

        
def get_remote_filename(durl):
        f=urllib.urlopen(durl)
        info= str(f.info())       
        fname=getfilename(info)        
        f.close()
        return fname
        
        

def usage():
        print "-p -i database | parse save.tv and store information in database"
        print "-d  date -i input_db -o output_db | extract movies from the given date from one db and add them in the next"
        print "-n name -i input_db -o output_db | extract movies from the given name from one db and add them in the next"
        print "-w -o out_db | download movies"
        print "-l -o out_db | print download links"
        print "-s -o out_db | show_db"


user=""
pass=""

try:
    opts, args = getopt.getopt(sys.argv[1:], "spi:o:d:n:wl",[])
except getopt.GetoptError, err:    
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
    
in_db=""
out_db=""
parse=False
down=False
list=False
show=False
date=""
name=""
for o, a in opts:
    if o == "-p":
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
    elif o in "-o":
        out_db=a;
    else:
        assert False, "unhandled option"

if parse==True and (in_db==""):
    usage();
    sys.exit(2)

if show==True and (out_db==""):
    usage();
    sys.exit(2)

if date!="" and (in_db=="" or out_db==""):
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
        login(user,pass);
        i=1
        
        
        while 1:
                print "Parsing page "+str(i)+" !"
                html=getArchive(i)        
                html2=getArchive(i+1)     
                print    len(html)
                print    len(html2)
                if len(html)==len(html2):
                        break;
                myparser = MyParser()
                myparser.add_tm(tm);
                myparser.parse(html)
                
                myparser = MyParser()
                myparser.add_tm(tm);
                myparser.parse(html2)                
                i=i+1
        
      
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

elif date!="":
        tm.deser(out_db);
        tm_temp=TitleManager();
        tm_temp.deser(in_db);
        login(user,pass);
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
        login(user,pass);
        for item in tm.item_list:            
            if item["Title"]==sys.argv[2]:
                print item["Title"]
                print item["SubTitle"]
                print item["Date"]                
                tm_temp.add_item(item);
        tm_temp.ser(in_db);
                
        
elif down:
        tm_temp=TitleManager();        
        tm_temp.deser(out_db);        
        
        for item in tm_temp.item_list:
                login(user,pass);
                print item["Title"]
                print item["SubTitle"]
                print item["Date"]
                durl=get_durl(item["Id"])
                fname=get_remote_filename(durl)
                print durl
                print fname
                get_file(durl,fname,default_dpath)               
                
        
            
            
        
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



