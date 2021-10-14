"""Konwertery jednostek w celu lekkiego ułatwienia pracy :)"""

from datetime import timezone
import math, re

month_pl = {
    "01": "stycznia",
    "02": "lutego",
    "03": "marca",
    "04": "kwietnia",
    "05": "maja",
    "06": "czerwca",
    "07": "lipca",
    "08": "sierpnia",
    "09": "września",
    "10": "października",
    "11": "listopada",
    "12": "grudnia"
}

def better_date(date):
    datetm = date.split("T")
    date = datetm[0].split("-")
    time = datetm[1].split(":")
    returndate = (date[2]+" "+month_pl[date[1]]+" "+date[0]+",  "+str(int(time[0])+2)+":"+time[1])
    return returndate

def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    
class VMath():
    def itoo(iloczynowa): #a(x-x1)(x-x2) -> ax^2+bx+c
        i2 = list(filter(None,re.split('[()x]', iloczynowa)))
        if len(i2)<3: i2.insert(0, "1")
        elif i2[0]=="-": i2[0]="-1"
        a,x1,x2 = float(i2[0]),float(i2[1]),float(i2[2])
        b = a*x1+a*x2
        c = a*x1*x2
        return f"Postać ogólna: {a}x²+{b}x+{c}".replace("+-","-")
    

    def itok(iloczynowa): #a(x-x1)(x-x2) -> a(x-p)^2+q
        i2 = list(filter(None,re.split('[()x]', iloczynowa)))
        if len(i2)<3: i2.insert(0, "1")
        elif i2[0]=="-": i2[0]="-1"
        a,x1,x2 = float(i2[0]),-float(i2[1]),-float(i2[2])
        p = (x1+x2)/2
        q = a*(p-x1)*(p-x2)
        return f"Postać kanoniczna: {a}(x-{p})²+{q}".replace("--","+").replace("+-","-")
        
    def otoi(ogolna): #ax^2+bx+c -> a(x-x1)(x-x2)
        o2 = list(filter(None,re.split("x\^2|[x]",ogolna)))
        if len(o2)<3: o2.insert(0, "1")
        elif o2[0]=="-": o2[0]="-1"
        a,b,c = float(o2[0]),float(o2[1]),float(o2[2])
        delta = b**2-(4*a*c)
        if delta>=0:
            x1 = (-b+math.sqrt(delta))/(2*a)
            x2 = (-b-math.sqrt(delta))/(2*a)
            if x1==x2: return f"Postać iloczynowa: {a}(x-{'%.2f'%x1})²".replace("--","+")
            else: return f"Postać iloczynowa: {a}(x-{'%.2f'%x1})(x-{'%.2f'%x2})".replace("--","+")
        else: return "Funkcja nie posiada postaci iloczynowej."
        
    def otok(ogolna): #ax^2+bx+c -> a(x-p)^2+q
        o2 = list(filter(None,re.split("x\^2|[x]",ogolna)))
        if len(o2)<3: o2.insert(0, "1")
        elif o2[0]=="-": o2[0]="-1"
        a,b,c = float(o2[0]),float(o2[1]),float(o2[2])
        p = -b/(2*a)
        delta = b**2-(4*a*c)
        q = -delta/(4*a)
        return f"Postać kanoniczna: {a}(x-{p})²+{q}".replace("--","+").replace("+-","-")
        
    def ktoi(kanoniczna): #a(x-p)^2+q -> a(x-x1)(x-x2)
        k2 = list(filter(None,re.split("\(x|\)\^2",kanoniczna)))
        a,p,q = float(k2[0]),-float(k2[1]),float(k2[2])
        b = -2*a*p
        c = a*p**2+q
        delta = b**2-(4*a*c)
        if delta>=0:
            x1 = (-b+math.sqrt(delta))/(2*a)
            x2 = (-b-math.sqrt(delta))/(2*a)
            if x1==x2: return f"Postać iloczynowa: {a}(x-{'%.2f'%x1})²".replace("--","+")
            else: return f"Postać iloczynowa: {a}(x-{'%.2f'%x1})(x-{'%.2f'%x2})".replace("--","+")
        else: return "Funkcja nie posiada postaci iloczynowej."
        
    def ktoo(kanoniczna): #a(x-p)^2+q -> ax^2+bx+c
        k2 = list(filter(None,re.split("\(x|\)\^2",kanoniczna)))
        a,p,q = float(k2[0]),-float(k2[1]),float(k2[2])
        b = -2*a*p
        c = a*p**2+q
        return f"Postać ogólna: {a}x²+{b}x+{c}".replace("+-","-")