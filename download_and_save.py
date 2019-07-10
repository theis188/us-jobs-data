
import requests
import zipfile
import os
import pandas as pd
import time
from config import DATA_FOLDER,FULL_FOLDER,NAT_FOLDER,STATE_FOLDER,METRO_FOLDER
import io

FULL_URLS = {
    '2018':'https://www.bls.gov/oes/special.requests/oesm18all.zip',
    '2017':'https://www.bls.gov/oes/special.requests/oesm17all.zip',
    '2016':'https://www.bls.gov/oes/special.requests/oesm16all.zip',
    '2015':'https://www.bls.gov/oes/special.requests/oesm15all.zip',
    '2014':'https://www.bls.gov/oes/special.requests/oesm14all.zip',
    '2013':'https://www.bls.gov/oes/special.requests/oesm13all.zip',
    '2012':'https://www.bls.gov/oes/special.requests/oesm12all.zip',
    '2011':'https://www.bls.gov/oes/special.requests/oesm11all.zip',
}

STATE_URLS = {
    '1999':'https://www.bls.gov/oes/special.requests/oes99st.zip',
    '2000':'https://www.bls.gov/oes/special.requests/oes00st.zip',
    '2001':'https://www.bls.gov/oes/special.requests/oes01st.zip',
    '2002':'https://www.bls.gov/oes/special.requests/oes02st.zip',
    '2003':'https://www.bls.gov/oes/special.requests/oesm03st.zip',
    '2004':'https://www.bls.gov/oes/special.requests/oesm04st.zip',
    '2005':'https://www.bls.gov/oes/special.requests/oesm05st.zip',
    '2006':'https://www.bls.gov/oes/special.requests/oesm06st.zip',
    '2007':'https://www.bls.gov/oes/special.requests/oesm07st.zip',
    '2008':'https://www.bls.gov/oes/special.requests/oesm08st.zip',
    '2009':'https://www.bls.gov/oes/special.requests/oesm09st.zip',
    '2010':'https://www.bls.gov/oes/special.requests/oesm10st.zip',
}

NATL_URLS = {
    '1999':'https://www.bls.gov/oes/special.requests/oes99nat.zip',
    '2000':'https://www.bls.gov/oes/special.requests/oes00nat.zip',
    '2001':'https://www.bls.gov/oes/special.requests/oes01nat.zip',
    '2002':'https://www.bls.gov/oes/special.requests/oes02nat.zip',
    '2003':'https://www.bls.gov/oes/special.requests/oesm03nat.zip',
    '2004':'https://www.bls.gov/oes/special.requests/oesm04nat.zip',
    '2005':'https://www.bls.gov/oes/special.requests/oesm05nat.zip',
    '2006':'https://www.bls.gov/oes/special.requests/oesm06nat.zip',
    '2007':'https://www.bls.gov/oes/special.requests/oesm07nat.zip',
    '2008':'https://www.bls.gov/oes/special.requests/oesm08nat.zip',
    '2009':'https://www.bls.gov/oes/special.requests/oesm09nat.zip',
    '2010':'https://www.bls.gov/oes/special.requests/oesm10nat.zip',
}

METRO_URLS = {
    '1999':'https://www.bls.gov/oes/special.requests/oes99ma.zip',
    '2000':'https://www.bls.gov/oes/special.requests/oes00ma.zip',
    '2001':'https://www.bls.gov/oes/special.requests/oes01ma.zip',
    '2002':'https://www.bls.gov/oes/special.requests/oes02ma.zip',
    '2003':'https://www.bls.gov/oes/special.requests/oesm03ma.zip',
    '2004':'https://www.bls.gov/oes/special.requests/oesm04ma.zip',
    '2005':'https://www.bls.gov/oes/special.requests/oesm05ma.zip',
    '2006':'https://www.bls.gov/oes/special.requests/oesm06ma.zip',
    '2007':'https://www.bls.gov/oes/special.requests/oesm07ma.zip',
    '2008':'https://www.bls.gov/oes/special.requests/oesm08ma.zip',
    '2009':'https://www.bls.gov/oes/special.requests/oesm09ma.zip',
    '2010':'https://www.bls.gov/oes/special.requests/oesm10ma.zip',
}

ALL_URLS = {
    FULL_FOLDER:FULL_URLS,
    METRO_FOLDER:METRO_URLS,
    STATE_FOLDER:STATE_URLS,
    NAT_FOLDER:NATL_URLS,
}

def process_all():
    # import pdb; pdb.set_trace()
    for folder, urls_dict in ALL_URLS.items():
        print('beginning', folder)
        for year in urls_dict:
            process_one_file(year, folder)
            print('complete--wating...')
            time.sleep(5)

def make_dir(path):
    if not os.path.exists( path ):
        os.makedirs( path )

def process_one_file(year,folder):
    url = ALL_URLS[ folder ][ year ]
    print('downloading', year)
    zip_path = download_zip_url(folder,year,url)
    print('processing zip')
    if (folder==METRO_FOLDER):
        if int(year)<=2004:
            return
        process_metro_zip( zip_path  )
    else:
        process_zip( zip_path )

def process_metro_zip(zip_path):        
    xlsx_path = zip_path.replace('.zip','.xlsx')
    dfs = []
    with zipfile.ZipFile(zip_path, 'r') as zipp:
        for to_extract in zipp.infolist():
            filename = to_extract.filename
            if 'field_descriptions' in filename:
                continue
            data = zipp.open( to_extract.filename , 'r' ).read()
            b = io.BytesIO( data )
            df = pd.read_excel( b )
            if 'BOS' in to_extract.filename:
                df['AREA_TYPE'] = 6
            else:
                df['AREA_TYPE'] = 5
            dfs.append(df)
    ret_df = pd.concat(dfs)
    excel = pd.ExcelWriter(xlsx_path)
    ret_df.to_excel( excel , 'data', index=False )
    excel.close()

def open_df_smart(filepath):
	df = pd.read_excel(filepath)
	num_fields = (~df.isna()).sum(axis=1)
	min_val = num_fields.min()
	if min_val>10:
		return df
	max_val = num_fields.max()
	index = num_fields[ num_fields==max_val].index[0]
	df = pd.read_excel(filepath,skiprows=0,header=index+1)
	return df

def process_zip( zip_path ):
    xlsx_path = zip_path.replace('.zip','.xlsx')
    with zipfile.ZipFile(zip_path, 'r') as zipp:
        to_extract = max( zipp.infolist() ,key=lambda x: x.file_size )
        data = zipp.open( to_extract.filename , 'r' ).read()
    with open(xlsx_path,'wb') as f:
        f.write( data )

def download_zip_url(folder, year, url):
    subfolder = os.path.join( DATA_FOLDER, folder )
    make_dir( subfolder )
    dest_path = os.path.join( subfolder , year+'.zip' )
    r = requests.get(url, allow_redirects=True)
    open(dest_path, 'wb').write(r.content)
    return dest_path

process_all()