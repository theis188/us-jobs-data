
from config import XLS_Constants, OE_Constants
from config import DATA_FOLDER,FULL_FOLDER,NAT_FOLDER,STATE_FOLDER,METRO_FOLDER,DB_PATH
import os
import sqlite3
import re
import pandas as pd
import time

_conn = sqlite3.connect(DB_PATH)

_constants = XLS_Constants()
_column_heads = _constants.column_heads
_data_u_want = _constants.data_u_want

def process_all():
	for foldername in [FULL_FOLDER,NAT_FOLDER,STATE_FOLDER,METRO_FOLDER]:
		print( 'folder',foldername )
		subfolder_path = os.path.join( DATA_FOLDER,foldername )
		filenames = os.listdir( subfolder_path )
		excel_files = sorted( [f for f in filenames if f.endswith('xlsx')] )
		for filename in excel_files:
			year = filename.split('.')[0]
			if (int(year)<2005) and (foldername ==METRO_FOLDER) :
				continue
			if int(year)<2001:
				continue
			print(filename)
			filepath = os.path.join( subfolder_path, filename )
			before = time.time()
			df = open_df_smart(filepath)
			print('df opened!')
			after = time.time()
			print( after - before )
			generate_codes(df,year, foldername)
			print('codes generated!')
			insert_data(df, '01', year)
			print( 'data inserted!' )

def generate_codes(df,year,foldername):
	try:
		df['INDUSTRY_CODE'] = df[ _column_heads ['other_codes']['industry_code'] ].apply(interpret_industry_code)
	except Exception as e:
		print(e)
		df['INDUSTRY_CODE'] = '000000'
	df['OCCUPATION_CODE'] = df[ _column_heads ['other_codes']['occupation_code'] ].apply( process_occupation_code_enclosure(year ) )
	df['AREA_CODE'] = df.apply( get_area_code_enclosure(year, foldername),axis=1 )
	df['SERIES_CODE_START'] = OE_Constants.SERIES_PREFIX + df.AREA_CODE + df.INDUSTRY_CODE + df.OCCUPATION_CODE

def insert_data(codes_df, code, year):
	groupby_fun = {'01':'sum','13':'mean'}[code]
	data_head = _column_heads['data_codes'][code]
	temp_df = codes_df[[ data_head , 'SERIES_CODE_START' ]].reset_index(drop=True)
	temp_df['series_code'] = temp_df['SERIES_CODE_START'] + code
	temp_df['period'] = 'A01'
	temp_df['year'] = year
	temp_df['data_date'] = year+'-01-01'
	temp_df['value'] = temp_df[data_head]
	temp_df = temp_df[['series_code','year','period','data_date','value']][ temp_df.value.apply( lambda x: '*' not in str(x) ) ]
	agg_df = temp_df.groupby(['series_code','year','period','data_date']).agg( {'value':groupby_fun} )
	agg_df = agg_df.reset_index()
	agg_df.to_sql( 'value', _conn, if_exists='append', index=False )

def fix_col_names(arg_df):
	arg_df.columns = [col.upper() for col in arg_df.columns]
	fix_cols = {'OCC CODE':'OCC_CODE','OCC TITLE':'OCC_TITLE'}
	for col in fix_cols:
		if col in arg_df.columns:
			arg_df = arg_df.rename( columns={col:fix_cols[col]} )
	return arg_df

def open_df_smart(filepath):
	df = pd.read_excel(filepath)
	num_fields = (~df.isna()).sum(axis=1)
	min_val = num_fields.min()
	if min_val>10:
		df = fix_col_names( df )
		return df
	max_val = num_fields.max()
	index = num_fields[ num_fields==max_val ].index[0]
	df = pd.read_excel(filepath,skiprows=0,header=index+1)
	df = fix_col_names( df )
	return df

def update_series_code_table():
	cur = _conn.execute( """SELECT distinct series_code FROM VALUE""" )
	value_codes = cur.fetchall()
	values_df = pd.DataFrame(value_codes)
	values_df.columns = ['code']
	split_codes = [(x[17:23],x[11:17],x[3:11],x[23:25]) for x in values_df.code]
	split_df = pd.DataFrame(split_codes)
	split_df.columns = ['occupation_code','industry_code','area_code','data_type']
	values_df[['occupation_code','industry_code','area_code','data_type']] = split_df
	values_df['complete'] = True
	values_df['exist'] = True
	cur = _conn.execute( """SELECT code FROM SERIES_CODE""" )
	series_codes = cur.fetchall()
	series_codes_list = [r[0] for r in series_codes]
	to_insert_df = values_df[ ~values_df.code.isin(series_codes_list) 
							].reset_index(drop=True)[
							['code','occupation_code','industry_code',
							'area_code','data_type','complete','exist']]
	to_insert_df.to_sql( 'series_code', _conn, if_exists='append', index=False )


def rem_hyphen(s):
	return s.replace('-','')

def process_occupation_code(year,occupation_code):
	if int(year)<=2010:
		occupation_code = _constants.crosswalk_2000_to_2010.get(occupation_code, occupation_code)
	occupation_code = rem_hyphen(occupation_code)
	return occupation_code

def process_occupation_code_enclosure(year):
	def inner_fun(occupation_code):
		return process_occupation_code( year, occupation_code )
	return inner_fun

def get_state_area_code(area):
	area_code = 'S'+str(area).zfill(2)+'00000'
	return area_code

def get_area_code_enclosure(year,foldername):
	def inner_fun(row):
		return get_area_code_from_row(row,'2011',foldername)
	return inner_fun

def get_area_code_from_row(row,year,foldername):
	if foldername==NAT_FOLDER:
		return 'N0000000'
	if foldername==STATE_FOLDER:
		area = str(row[ _column_heads['other_codes']['area'] ])
		return get_state_area_code( area )
	area_type = row[ _column_heads['other_codes']['area_type'] ]
	area = str(row[ _column_heads['other_codes']['area'] ])
	if area_type == 1:
		area_code = 'N0000000'
	elif area_type in (2,3):
		area_code = 'S'+area.zfill(2)+'00000'
	elif area_type in (4,5):
		area_code = 'M00'+area.zfill(5)
	elif area_type == 6:
		area_code = 'M'+area.zfill(7)
	return area_code

def get_value_from_row(row,data_code,year):
	value = row[ _column_heads['data_codes'][data_code] ]
	return float(value)

def interpret_industry_code(ic):
	try:
		ic = str(ic)
		if re.match(r'^[0-9][0-9]$',ic):
			code = ic+'--'+str(int(ic)+1).zfill(2)
		elif re.match(r'^[0-9][0-9]-[0-9][0-9]$',ic):
			ic1 = ic[:2] 
			ic2 = ic[3:5]
			code = ic1 + '--' + str(int(ic2)+1).zfill(2)
		elif len(ic) == 6:
			code = ic
		else:
			input('unexpected industry_code:',ic)
			raise KeyError
		return code
	except TypeError:
		print(type(ic))
		print('TypeError',ic)
		input('pause')

if __name__ == '__main__':
	process_all()
	update_series_code_table()
