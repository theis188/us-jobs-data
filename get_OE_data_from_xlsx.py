
from config import XLS_Constants, OE_Constants, CONSTANTS
from config import DATA_FOLDER,FULL_FOLDER,NAT_FOLDER,STATE_FOLDER,METRO_FOLDER,DB_PATH,DATA_CODE_AGG_FUNCS, apply_occ_transformations, sum_groups_df, apply_degrouping_transformations
import os
import sqlite3
import re
import pandas as pd
import time

_conn = sqlite3.connect(DB_PATH)

_constants = CONSTANTS
_column_heads = _constants.column_heads
_data_u_want = _constants.data_u_want

pd.set_option("display.width", 1000)

# df[
# 	(df["AREA_CODE"] == "N0000000") &
# 	(df["INDUSTRY_CODE"] == "000000") &
# 	(df["OCC_CODE"].str.endswith("0"))
# ][["TOT_EMP", "OCC_CODE", "OCC_TITLE"]].OCC_CODE.value_counts()

def process_all():
	for foldername in [FULL_FOLDER,NAT_FOLDER,STATE_FOLDER,METRO_FOLDER]:
		print( 'folder',foldername )
		subfolder_path = os.path.join( DATA_FOLDER,foldername )
		filenames = os.listdir( subfolder_path )
		excel_files = sorted( [f for f in filenames if f.endswith('xlsx')] )
		for filename in excel_files:
			year = filename.split('.')[0]
			## before 2004, and metro before 2005 should be skipped
			if (int(year)<2005) and (foldername == METRO_FOLDER) :
				continue
			if int(year)<2004:
				continue
			filepath = os.path.join( subfolder_path, filename )
			before = time.time()
			# filename = "2019.xlsx"; foldername=FULL_FOLDER; subfolder_path = os.path.join( DATA_FOLDER,foldername ); filepath = os.path.join( subfolder_path, filename ); year = filename.split(".")[0]; data_type_code="01"
			df_original = open_df_smart(filepath)
			after = time.time()
			print(filename)
			print('df opened!')
			print("time taken to open", after - before )
			for data_type_code in ["01"]:
				# translates column names
				df = df_original.copy()
				df = generate_basic_codes(df, year, foldername)
				print("basic codes generated")
				df = numerify_data_col(df, data_type_code)
				print("data col numerified")				
				df = apply_degrouping_transformations(df, year)
				print("degrouping transformations applied")
				df = deduplicate_df(df)
				print("deduplicate df")
				df = apply_occ_transformations(df, year)
				print("transform occ_code dfs")
				df = generate_series_codes(df, data_type_code)
				print('codes generated!')
				df = sum_groups_df(df)
				print("calculate df groups from constituents")
				insert_data(df, year, data_type_code)
				print( 'data inserted!' )


def numerify_data_col(df, data_type_code):
	data_head = _column_heads['data_codes'][data_type_code]
	df[data_head] = pd.to_numeric(df[data_head], errors="coerce")
	return df

def deduplicate_df(df):
	df = df.drop_duplicates(subset=["OCC_CODE", "INDUSTRY_CODE", "AREA_CODE"])
	return df

def generate_basic_codes(df, year, foldername):
	try:
		df['INDUSTRY_CODE'] = df[ _column_heads ['other_codes']['industry_code'] ].apply(interpret_industry_code)
	except Exception as e:
		print(e)
		df['INDUSTRY_CODE'] = '000000'
	df['AREA_CODE'] = df.apply( get_area_code_enclosure(year, foldername),axis=1 )
	return df

def generate_series_codes(df, data_type_code):
	df['OCCUPATION_CODE'] = df[ _column_heads ['other_codes']['occupation_code'] ].apply( rem_hyphen )
	series_code_start = OE_Constants.SERIES_PREFIX + df.AREA_CODE + df.INDUSTRY_CODE + df.OCCUPATION_CODE
	df['SERIES_CODE'] = series_code_start + data_type_code
	return df

def insert_data(df, year, data_type_code):
	groupby_fun = DATA_CODE_AGG_FUNCS[data_type_code]
	data_head = _column_heads['data_codes'][data_type_code]
	temp_df = df[[ data_head , 'SERIES_CODE' ]].reset_index(drop=True)
	temp_df['series_code'] = temp_df['SERIES_CODE']
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
	# if int(year)<=2010:
	# 	occupation_code = _constants.crosswalk_2000_to_2010.get(occupation_code, occupation_code)
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
