"""Konwertery jednostek w celu lekkiego ułatwienia pracy :)"""

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
    returndate = (date[2]+" "+month_pl[date[1]]+" "+date[0]+",  "+time[0]+":"+time[1])
    return returndate