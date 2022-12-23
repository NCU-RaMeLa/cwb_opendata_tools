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
P.S.若已解壓縮，則gzipped自行改成false


# 下載 CWB Open weather data
此module另有CWB open data雷達回波資料下載用插件方便即時import雷達資料<br>
(需要有氣象會員授權碼: CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)<br>
預設存檔於 './radar/cwb_opendata', 檔名為COMPREF.OpenData.yyyymmdd.HHMM.gz<br>
向CWB請求資料下載時與查找資料之時間區間為使用台灣時間(UTC+8)<br>
下載後之檔名與檔頭內容皆會轉為UTC<br>

### 快速使用方式:
```python
from datetime import datetime, timedelta

import sys
sys.path.append('./cwb_opendata/')
import cwb_opendata

#################### Download data from CWB Open Data Bank (XML)
out_list = cwb_opendata.download(authorization="CWB-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

#################### Convert XML to CWB radar binary file
# create array
convert_out = []
for fn1 in out_list:
    # xml2compref will return file path, save to temporary variable
    tmp = cwb_opendata.xml2compref(filename_in=fn1, filename_out='.'.join(fn1.split('/')[-1].split('.')[:-1]))

    convert_out.append(tmp) # append to array

#################### Display CWB radar binary file head info
metadata = cwb_opendata.dump_compref(filename=convert_out[-1], gzipped=True)

# display metadata, also can use "print(metadata)"
for keys, value in metadata.items():
    print('{:9s} : {}'.format(keys, value))

#################### Plot CWB radar binary file
fig_name = cwb_opendata.plot_compref(
    filename=convert_out[-1], gzipped=True, dpi=72, figsize=[49.67,49.67],
    savefig=False, outpath='./cwb_opendata_radar/figure'
    )
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
    savefig=False, outpath='./cwb_opendata_radar/figure'
    )
print(fig_name)
```
