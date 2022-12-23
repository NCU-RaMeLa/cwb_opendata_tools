#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 11:31:33 2022

@author: mihzou
"""

from datetime import datetime, timedelta
import os
import xmltodict
import numpy as np
import gzip

def download(
        outpath="./cwb_opendata_radar/xml",
        remove_exist=True,
        authorization="",
        limit=None,
        offset=0,
        timeFrom=(datetime.now()-timedelta(seconds=3600*2)).strftime("%Y-%m-%d %H:%M:%S"),
        timeTo=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **kwargs):
    
    from urllib import request

    """
    A detailed description of the importer. A minimal documentation is
    strictly needed since the pysteps importers interface expect docstrings.

    For example, a documentation may look like this:

    Import a precipitation field from the Awesome Bureau of Composites stored in
    Grib format.

    Parameters
    ----------
    outpath : str
        path of the file to save.

    remove_old : bool
        True, False. Remove exist data (default = True)

    authorization : str
        * required 氣象開放資料平台會員授權碼

    limit : int
        int or None, 限制最多回傳的資料, 預設為None

    offset : int
        指定從第幾筆後開始回傳, 預設為第 0 筆開始回傳

    timeFrom : str
        時間區段, 篩選需要之時間區段，時間從「timeFrom」開始篩選，直到內容之最後時間，並可與參數「timeTo」 合併使用，格式為「yyyy-MM-dd hh:mm:ss」

    timeTo : str
        時間區段, 篩選需要之時間區段，時間從內容之最初時間開始篩選，直到「timeTo」，並可與參數「timeFrom」 合併使用，格式為「yyyy-MM-ddThh:mm:ss」

    {extra_kwargs_doc}

    ####################################################################################
    # The {extra_kwargs_doc} above is needed to add default keywords added to this     #
    # importer by the pysteps.decorator.postprocess_import decorator.                  #
    # IMPORTANT: Remove these box in the final version of this function                #
    ####################################################################################

    Returns
    -------

    out_list : list

    """
    if limit is None:
        limit=''
    if remove_exist:
        import shutil
        os.makedirs(outpath, exist_ok=True)
        shutil.rmtree(outpath)        

    timeFrom2 = datetime.strptime(timeFrom, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H%%3A%M%%3A%S")
    timeTo2 = datetime.strptime(timeTo, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%dT%H%%3A%M%%3A%S")
    urlc = 'https://opendata.cwb.gov.tw/historyapi/v1/getMetadata/O-A0059-001' + '?Authorization=' + authorization + '&limit=' + str(limit) + '&offset=' + str(offset) + '&format=' + 'XML' + '&timeFrom=' + timeFrom2 + '&timeTo='  +timeTo2
    
    RawDataList = xmltodict.parse(request.urlopen(urlc).read().decode("utf-8"))
    
    TList = RawDataList['cwbopendata']['dataset']['resources']['resource']['data']['time']
    out_list = []
    for i in np.arange(0,np.size(TList,0),1):
        tLnum  = datetime.strptime(TList[i]['dataTime'], '%Y-%m-%d %H:%M:%S').timestamp()
        tLyy = datetime.utcfromtimestamp(tLnum).strftime('%Y')
        tLmm = datetime.utcfromtimestamp(tLnum).strftime('%m')
        tLdd = datetime.utcfromtimestamp(tLnum).strftime('%d')
        tLhh = datetime.utcfromtimestamp(tLnum).strftime('%H')
        tLmn = datetime.utcfromtimestamp(tLnum).strftime('%M')
        tLpath = outpath+'/'+tLyy+'/'+tLmm+'/'+tLdd+'/COMPREF.OpenData.'+tLyy+tLmm+tLdd+'.'+tLhh+tLmn
        
        os.makedirs(outpath, exist_ok=True)
        if not os.path.isfile(tLpath+'.xml'):
            print("Downloading file:  "+tLpath+'.xml')
            out_list.append(tLpath+'.xml')
            url = TList[i]['url']
            data = request.urlopen(url).read().decode("utf-8")
            os.makedirs(outpath+'/'+tLyy+'/'+tLmm+'/'+tLdd, exist_ok=True)
            fid = open(tLpath+'.xml', 'wt')
            fid.write(data)
            fid.close()

    return out_list

def xml2compref(filename_in, filename_out, outpath="./cwb_opendata_radar/compref", gzipped=True, **kwargs):
    fid = open(filename_in, 'rt')
    RawData = xmltodict.parse(fid.read())
    fid.close()
    
    parameterSet = RawData['cwbopendata']['dataset']['datasetInfo']['parameterSet']['parameter']

    mosradar = parameterSet[0]['radarName'].split('、')
    
    nradar = np.size(mosradar)

    for i in np.arange(0,nradar,1):
        if mosradar[i].find('五分山') !=-1:
            mosradar[i]='RCWF'
        elif mosradar[i].find('花蓮') !=-1:
            mosradar[i]='RCHL'
        elif mosradar[i].find('七股') !=-1:
            mosradar[i]='RCCG'
        elif mosradar[i].find('墾丁') !=-1:
            mosradar[i]='RCKT'
        elif mosradar[i].find('樹林') !=-1:
            mosradar[i]='RCSL'
        elif mosradar[i].find('南屯') !=-1:
            mosradar[i]='RCNT'
        elif mosradar[i].find('林園') !=-1:
            mosradar[i]='RCLY'
        elif mosradar[i].find('馬公') !=-1:
            mosradar[i]='RCMK'
        elif mosradar[i].find('清泉崗') !=-1:
            mosradar[i]='RCCK'
        elif mosradar[i].find('石垣') !=-1:
            mosradar[i]='ISHI'
        elif mosradar[i].find('綠島') !=-1:
            mosradar[i]='RCGI'
        
    lon0 =  np.fromstring(parameterSet[1]['parameterValue'],
                          dtype=np.float16,
                          count=-1,
                          sep=',')[0]

    lat0 =  np.fromstring(parameterSet[1]['parameterValue'],
                          dtype=np.float16,
                          count=-1,
                          sep=',')[1]

    res = float(parameterSet[2]['parameterValue'])

    t0 = parameterSet[3]['parameterValue']
    t0num   = datetime.strptime(t0, '%Y-%m-%dT%H:%M:%S%z').timestamp()
    utct0 = datetime.utcfromtimestamp(t0num).strftime('%Y-%m-%d %H:%M:%S')

    nx = np.fromstring(parameterSet[4]['parameterValue'],
                      dtype=np.int16,
                      count=-1,
                      sep='*')[0]

    ny = np.fromstring(parameterSet[4]['parameterValue'],
                      dtype=np.int16,
                      count=-1,
                      sep='*')[1]

    unit = parameterSet[5]['parameterValue']

    dbz = np.fromstring(RawData['cwbopendata']['dataset']['contents']['content'],
                        dtype=np.float32,
                        count=-1,
                        sep=',').astype(np.int16)

    dbz = dbz.reshape(ny,nx)

    # import matplotlib.pyplot as plt
    # lon,lat = np.meshgrid(
    #     np.arange(lon0,lon0+res*(x-1)+res/2,res),
    #     np.arange(lat0,lat0+res*(y-1)+res/2,res))
    # plt.pcolor(lon,lat,dbz)

    yyyy = utct0[0:4]
    mm = utct0[5:7]
    dd = utct0[8:10]
    hh = utct0[11:13]
    mn = utct0[14:16]
    ss = utct0[17:19]
    nz = 1
    # allocate(var4(nx,ny,nz),var_true(nx,ny,nz),var(nx,ny,nz))
    # allocate(I_var_true(nx,ny,nz))
    # allocate(zht(nz))
    proj = 'LL'
    map_scale = 1000
    projlat0 = 30*map_scale
    projlat1 = 60*map_scale
    projlon = 120.75*map_scale
    xy_scale = 1000
    alon = lon0*xy_scale
    alat = (lat0+res*(ny-1))*xy_scale
    dxy_scale = 100000
    dx = res*dxy_scale
    dy = res*dxy_scale
    zht = 0
    z_scale = 1
    i_bb_mode = -12922
    unkn01 = np.zeros(9)
    varname1 = ['Q','P','E','O']
    varname2 = [1,2,3,4]
    varunit = unit
    unkn02 = 'TRA'
    var_scale = 10
    missing = -999
    nradar = nradar
    mosradar = mosradar

    os.makedirs(outpath+'/'+yyyy+'/'+mm+'/'+dd, exist_ok=True)
 
    #write BUFFER
    
    buffer = np.array([yyyy,mm,dd,hh,mn,ss,nx,ny,nz], dtype='i4').tobytes()
    buffer += np.array(proj, dtype='a4').tobytes()
    buffer += np.array([map_scale,projlat0,projlat1,projlon,alon,alat,xy_scale,dx,dy,
              dxy_scale,zht,z_scale,i_bb_mode], dtype='i4').tobytes()
    buffer += np.array(unkn01, dtype='i4').tobytes()
    buffer += np.array(varname1, dtype='a1').tobytes()
    buffer += np.array(varname2, dtype='i4').tobytes()
    buffer += np.array(varunit, dtype='a3').tobytes()
    buffer += np.array(unkn02, dtype='a3').tobytes()
    buffer += np.array([var_scale,missing,nradar], dtype='i4').tobytes()
    buffer += np.array(mosradar, dtype='S4').tobytes()

    dbz1d = dbz.flatten()
    buffer += np.array(dbz1d*var_scale, dtype='i2').tobytes()
    if gzipped:
        output_file = outpath+'/'+yyyy+'/'+mm+'/'+dd+'/'+filename_out+'.gz'
        fid = gzip.open(output_file, 'wb')
    else:
        output_file = outpath+'/'+yyyy+'/'+mm+'/'+dd+'/'+filename_out
        fid = open(output_file, 'wb')
    print('Convert to: '+output_file)
    fid.write(buffer)
    fid.close()
    return output_file

def dump_compref(filename, gzipped=True, **kwargs):

    if gzipped is False:
        fid = open(filename, mode='rb')
    else:
        fid = gzip.open(filename, 'rb')

    buf = fid.read()
    yyyy,mm,dd,hh,mn,ss,nx,ny,nz = np.frombuffer(buf, dtype=np.int32, count=9)
    proj = np.frombuffer(buf, dtype='S4', count=1, offset=36)
    map_scale,projlat0,projlat1,projlon = np.frombuffer(buf, dtype=np.int32, count=4, offset=40)
    alon,alat,xy_scale,dx,dy,dxy_scale = np.frombuffer(buf, dtype=np.int32, count=6, offset=56)
    zht = np.frombuffer(buf, dtype=np.int32, count=nz, offset=80)
    z_scale,i_bb_mode = np.frombuffer(buf, dtype=np.int32, count=2, offset=80+4*nz)
    unkn01 = np.frombuffer(buf, dtype=np.int32, count=9, offset=88+4*nz)
    varname1 = np.frombuffer(buf, dtype='S4', count=1, offset=124+4*nz)
    varname2 = np.frombuffer(buf, dtype=np.int32, count=4, offset=128+4*nz)
    varunit,unkn02 = np.frombuffer(buf, dtype='S3', count=2, offset=144+4*nz)
    var_scale,missing,nradar = np.frombuffer(buf, dtype=np.int32, count=3, offset=150+4*nz)
    mosradar = np.frombuffer(buf, dtype='S4', count=nradar, offset=162+4*nz)
    var = np.frombuffer(buf, dtype=np.int16, count=-1, offset=162+4*nz+4*nradar)
    fid.close()

    metadata = dict(
        year=yyyy, month=mm, day=dd, hour=hh, minute=mn, second=ss,
        nx=nx, ny=ny, nz=nz, proj=proj.astype('U4'), map_scale=map_scale,
        projlat0=projlat0, projlat1=projlat1, projlon=projlon,
        alon=alon, alat=alat, xy_scale=xy_scale, dx=dx, dy=dy,
        dxy_scale=dxy_scale, zht=zht, z_scale=z_scale, i_bb_mode=i_bb_mode,
        unkn01=unkn01, varname1=varname1.astype('U4'), varname2=varname2,
        varunit=varunit.astype('U4'), unkn02=unkn02, var_scale=var_scale,
        missing=missing, nradar=nradar, mosradar=mosradar.astype('U4'),
    )
    return metadata

def plot_compref(filename, gzipped=True, dpi=96, figsize=[49.67, 49.67], savefig=False, outpath="./cwb_opendata_radar/figure"):

    if gzipped is False:
        fid = open(filename, mode='rb')
    else:
        import gzip
        fid = gzip.open(filename, 'rb')

    buf = fid.read()
    yyyy,mm,dd,hh,mn,ss,nx,ny,nz = np.frombuffer(buf, dtype=np.int32, count=9)
    proj = np.frombuffer(buf, dtype='S4', count=1, offset=36)
    map_scale,projlat0,projlat1,projlon = np.frombuffer(buf, dtype=np.int32, count=4, offset=40)
    alon,alat,xy_scale,dx,dy,dxy_scale = np.frombuffer(buf, dtype=np.int32, count=6, offset=56)
    zht = np.frombuffer(buf, dtype=np.int32, count=nz, offset=80)
    z_scale,i_bb_mode = np.frombuffer(buf, dtype=np.int32, count=2, offset=80+4*nz)
    unkn01 = np.frombuffer(buf, dtype=np.int32, count=9, offset=88+4*nz)
    varname1 = np.frombuffer(buf, dtype='S4', count=1, offset=124+4*nz)
    varname2 = np.frombuffer(buf, dtype=np.int32, count=4, offset=128+4*nz)
    varunit,unkn02 = np.frombuffer(buf, dtype='S3', count=2, offset=144+4*nz)
    var_scale,missing,nradar = np.frombuffer(buf, dtype=np.int32, count=3, offset=150+4*nz)
    mosradar = np.frombuffer(buf, dtype='S4', count=nradar, offset=162+4*nz)
    var = np.frombuffer(buf, dtype=np.int16, count=-1, offset=162+4*nz+4*nradar)
    fid.close()

    dBZ = var/var_scale

    # -999 = No Value, -99 = Clear Sky
    #dBZ[dBZ<-90] = np.nan
    dBZ[np.logical_and(dBZ>-900,dBZ<-90)] = np.nan

    dBZ = dBZ.reshape(ny,nx)

    ul_lon = alon/xy_scale # 115.0
    ul_lat = alat/xy_scale-(ny-1)*(dy/dxy_scale) # 18.0
    lr_lon = alon/xy_scale+(nx-1)*(dx/dxy_scale) # 126.5
    lr_lat = alat/xy_scale # 29.0

    lons = np.linspace(ul_lon, lr_lon, nx)
    lats = np.linspace(ul_lat, lr_lat, ny)

    lons, lats = np.meshgrid(lons, lats)

    fill_lons1, fill_lats1 = np.meshgrid(np.linspace(ul_lon, lr_lon, nx), np.arange(17, 18, 0.0125))
    fill_lons2, fill_lats2 = np.meshgrid(np.linspace(ul_lon, lr_lon, nx), np.arange(29.0125, 30, 0.0125))

    fill_d1 = np.full([np.size(fill_lons1,0), np.size(fill_lons1,1)],-999)
    fill_d2 = np.full([np.size(fill_lons2,0), np.size(fill_lons2,1)],-999)

    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.io.shapereader import Reader
    from  matplotlib import rcParams

    #[R, G, B, A]
    CWBColor = np.array([
        [  0, 255, 255, 255],
        [  0, 237, 255, 255],
        [  0, 219, 255, 255],
        [  0, 200, 255, 255],
        [  0, 182, 255, 255],
        [  0, 164, 255, 255],
        [  0, 146, 255, 255],
        [  0, 128, 255, 255],
        [  0, 109, 255, 255],
        [  0,  91, 255, 255],
        [  0,  73, 255, 255],
        [  0,  55, 255, 255],
        [  0,  36, 255, 255],
        [  0,  18, 255, 255],
        [  0,   0, 255, 255],
        [  0, 255,   0, 255],
        [  0, 244,   0, 255],
        [  0, 233,   0, 255],
        [  0, 222,   0, 255],
        [  0, 211,   0, 255],
        [  0, 200,   0, 255],
        [  0, 190,   0, 255],
        [  0, 180,   0, 255],
        [  0, 170,   0, 255],
        [  0, 160,   0, 255],
        [  0, 150,   0, 255],
        [ 51, 171,   0, 255],
        [102, 192,   0, 255],
        [153, 213,   0, 255],
        [204, 234,   0, 255],
        [255, 255,   0, 255],
        [255, 244,   0, 255],
        [255, 233,   0, 255],
        [255, 222,   0, 255],
        [255, 211,   0, 255],
        [255, 200,   0, 255],
        [255, 184,   0, 255],
        [255, 168,   0, 255],
        [255, 152,   0, 255],
        [255, 136,   0, 255],
        [255, 120,   0, 255],
        [255,  96,   0, 255],
        [255,  72,   0, 255],
        [255,  48,   0, 255],
        [255,  24,   0, 255],
        [255,   0,   0, 255],
        [244,   0,   0, 255],
        [233,   0,   0, 255],
        [222,   0,   0, 255],
        [211,   0,   0, 255],
        [200,   0,   0, 255],
        [190,   0,   0, 255],
        [180,   0,   0, 255],
        [170,   0,   0, 255],
        [160,   0,   0, 255],
        [150,   0,   0, 255],
        [171,   0,  51, 255],
        [192,   0, 102, 255],
        [213,   0, 153, 255],
        [234,   0, 204, 255],
        [255,   0, 255, 255],
        [234,   0, 255, 255],
        [213,   0, 255, 255],
        [192,   0, 255, 255],
        [171,   0, 255, 255],
        [150,   0, 255, 255]
        ])/255

    cwb_size = 49.67
    rcParams["figure.figsize"] = figsize
    rcParams["figure.dpi"] = dpi
    rcParams["figure.facecolor"] = 'w'
    rcParams["figure.edgecolor"] = 'k'
    rcParams["image.aspect"] = 1
    rcParams["axes.facecolor"] = 'w'
    rcParams["axes.spines.left"] = False
    rcParams["axes.spines.bottom"] = False
    rcParams["axes.spines.top"] = False
    rcParams["axes.spines.right"] = False
    rcParams["axes.grid"] = False
    rcParams["xtick.major.bottom"] = False
    rcParams["ytick.major.left"] = False

    fig = plt.figure(frameon=False)
    size = fig.get_size_inches()
    size_ratio = size[0]/cwb_size
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.set_extent([115, 126.5, 17.75, 29.25], crs=ccrs.PlateCarree())

    #ax.add_feature(cfeature.LAND, facecolor='#e5e5e5')

    cm = LinearSegmentedColormap.from_list('CWBcmap', CWBColor, N=66)
    cm.set_under(color=(0, 0, 0), alpha=0.04)

    ax2 = plt.pcolormesh(fill_lons1, fill_lats1, fill_d1, cmap=cm)
    ax2.set_clim(0, 66)
    ax3 = plt.pcolormesh(fill_lons2, fill_lats2, fill_d2, cmap=cm)
    ax3.set_clim(0, 66)

    ax1 = plt.pcolormesh(lons, lats, dBZ, cmap=cm)
    ax1.set_clim(0,66)

    shp_tw = './cwb_opendata/shapefiles/COUNTY_MOI_1080726.shp'
    shp_cn = './cwb_opendata/shapefiles/CHN_adm0.shp'
    shp_jp = './cwb_opendata/shapefiles/JPN_adm0.shp'
    shp_ph = './cwb_opendata/shapefiles/PHL_adm0.shp'

    ax.add_geometries(Reader(shp_cn).geometries(), ccrs.PlateCarree(),
                      facecolor='#e5e5e5', edgecolor='#666666',
                      linewidth=3*size_ratio)
    ax.add_geometries(Reader(shp_jp).geometries(), ccrs.PlateCarree(),
                      facecolor='#e5e5e5',  edgecolor='#666666',
                      linewidth=3*size_ratio)
    ax.add_geometries(Reader(shp_ph).geometries(), ccrs.PlateCarree(),
                      facecolor='#e5e5e5', edgecolor='#666666',
                      linewidth=3*size_ratio)
    ax.add_geometries(Reader(shp_tw).geometries(), ccrs.PlateCarree(),
                      facecolor='#e5e5e5', edgecolor='black',
                      linewidth=3*size_ratio)

    plt.xticks(np.arange(115,126.5,1))
    plt.yticks(np.arange(18,29.1,1))
    plt.grid(visible=True, lw=4*size_ratio)
    plt.xlim(115, 126.5)
    plt.ylim(17.75, 29.25)
    cb = plt.colorbar(cax=ax.inset_axes((0.95, 0.007, 0.02, 0.3)),
                      ticks=np.arange(0, 66, 5), orientation='vertical')

    cb.ax.set_title(label='dBZ', fontdict={'fontsize':30*size_ratio, 'fontweight':'bold'}, loc='left')
    cb.ax.tick_params(direction='in', length=0)
    cb.ax.set_yticklabels(np.arange(0, 66, 5), fontsize=30*size_ratio, weight='bold')
    cb.outline.set_color(None)

    tx_time = str(yyyy) + '/' + str(mm).zfill(2) + '/' + str(dd).zfill(2)
    tx_time += ' ' + str(hh).zfill(2) + ':' + str(mn).zfill(2)

    tx1 = plt.text(115.3, 29, tx_time, ha='left', va='top',
                   fontsize=90*size_ratio, zorder=2,
                   weight='bold', alpha=0.98, color='gray')

    tx2 = plt.text(126.3, 29, 'Composite Reflectivity', ha='right', va='top',
                   fontsize=80*size_ratio, zorder=2,
                   weight='normal', alpha=0.98, color='gray')

    i = 0
    for rcode in ['RCWF','RCHL','RCCG','RCKT','RCSL','RCNT','RCLY']:
        if np.any(mosradar.astype("U4")==rcode):
            light = plt.Circle((115.4,28.5+i), 0.09, fc='#8cdc50', ec='gray', zorder=2)
        else:
            light = plt.Circle((115.4,28.5+i), 0.09, fc='gray', ec='gray', zorder=2)
        ax.add_artist(light)
        plt.text(115.6, 28.5+i, rcode, ha='left', va='center',
                       fontsize=50*size_ratio,
                       weight='bold', alpha=0.98, color='gray')
        i -= 0.25

    fn  = outpath + '/' + '/'.join([str(yyyy),str(mm).zfill(2),str(dd).zfill(2)]) + '/CV1_open_'
    fn += str(yyyy) + str(mm).zfill(2) + str(dd).zfill(2)
    fn += str(hh).zfill(2) + str(mn).zfill(2) + '.png'
    if savefig:
        plt.savefig(fn, bbox_inches='tight', dpi=fig.dpi, pad_inches=0.0)
    return fn
