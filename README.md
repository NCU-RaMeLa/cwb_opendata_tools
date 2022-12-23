<h1 align="center">CWB Open Data Radar Tools</h1>

### 此module含有處理CWB Open Data內雷達資料之相關工具


# 相關網站
* [NCU RADAR Lab.](http://radar.atm.ncu.edu.tw)
* [CWB Open Weather Data](https://opendata.cwb.gov.tw)
* [Central Weather Bureau](https://www.cwb.gov.tw)

# 需要的額外modules:
os<br>
gzip<br>
numpy<br>
shutil<br>
urllib3<br>
cartopy<br>
datetime<br>
xmltodict<br>
matplotlib<br>

# 支援的檔案格式
支援氣象局二維全台雷達整合資料之gzip壓縮格式 (e.q. COMPREF.20211127.1430.gz)<br>
P.S.若已解壓縮，則gzipped自行改成False


# 下載 CWB Open weather data
此module另有CWB open data雷達回波資料下載用插件方便下載雷達資料<br>
(需要有氣象會員授權碼: CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)<br>
預設存檔於 './cwb_opendata_radar/', 檔名為COMPREF.OpenData.yyyymmdd.HHMM.???<br>
向CWB請求資料下載時與查找資料之時間區間為使用台灣時間(UTC+8)<br>
下載後之檔名與檔頭內容皆會轉為UTC<br>

### 快速使用方式:
```python
from datetime import datetime, timedelta

import sys
sys.path.append('./cwb_opendata/')
import cwb_opendata

#################### Download data from CWB Open Data Bank (XML)
# 以氣象會員授權碼下載資料(XML格式), 預設存於"./cwb_opendata_radar/xml"
out_list = cwb_opendata.download(authorization="CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")
# cwb_opendata.download() will return filename str list

#################### Convert XML to CWB radar binary file
# 將XML轉檔成CWB雷達回波整合資料格式(預設存於"./cwb_opendata_radar/compref")
# create array
convert_out = []
for fn1 in out_list:
    # xml2compref will return file path, save to temporary variable
    tmp = cwb_opendata.xml2compref(filename_in=fn1, filename_out='.'.join(fn1.split('/')[-1].split('.')[:-1]))

    convert_out.append(tmp) # append to array

# cwb_opendata.xml2compref() will return filename (str)

#################### Display CWB radar binary file head info
# 取convert_out中的最後一個檔名為例
metadata = cwb_opendata.dump_compref(filename=convert_out[-1])

# display metadata, also can use "print(metadata)"
for keys, value in metadata.items():
    print('{:9s} : {}'.format(keys, value))

# cwb_opendata.dump_compref() will return python dictionary

#################### Plot CWB radar binary file
# 預設dpi=96, figsize=[49.67, 49.67]  49.67英吋, 會畫出跟氣象局一樣的3600x3600之png
fig_name = cwb_opendata.plot_compref(filename=convert_out[-1])
print(fig_name)
```

### 進階使用:
```python
from datetime import datetime, timedelta

import sys
sys.path.append('./cwb_opendata/')
import cwb_opendata

#################### Download data from CWB Open Data Bank (XML)
out_list = cwb_opendata.download(
    outpath="./cwb_opendata_radar/xml",
    remove_exist=True,
    authorization="CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    limit=None,
    offset=0,
    timeFrom=(datetime.now()-timedelta(seconds=3600*1)).strftime("%Y-%m-%d %H:%M:%S"),
    timeTo=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#################### Convert XML to CWB radar binary file
# create array
convert_out = []
for fn1 in out_list:
    # xml2compref will return file path, save to temporary variable
    tmp = cwb_opendata.xml2compref(
        filename_in=fn1,
        filename_out='.'.join(fn1.split('/')[-1].split('.')[:-1]),
        outpath='./cwb_opendata_radar/compref',
        gzipped=True)
    
    convert_out.append(tmp) # append to array

#################### Display CWB radar binary file head info
metadata = cwb_opendata.dump_compref(filename=convert_out[-1], gzipped=True)

# display metadata, also can use "print(metadata)"
for keys, value in metadata.items():
    print('{:9s} : {}'.format(keys, value))

#################### Plot CWB radar binary file
fig_name = cwb_opendata.plot_compref(
    filename=convert_out[-1], gzipped=True, dpi=72, figsize=[49.67,49.67],
    outpath='./cwb_opendata_radar/figure', display=True
    )
print(fig_name)
```
