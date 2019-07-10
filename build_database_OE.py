import sqlite3
import pandas as pd
import re
from sqlite3 import IntegrityError
from config import OE_Constants,DB_PATH
import sys
from collections import defaultdict

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def create_table_with_df(path,table_name):
	df = parse_text_file(path)
	df.to_sql(table_name, conn, if_exists='replace', index=False, dtype={'code':'text','name':'text'})

def parse_text_file(path):
	df = pd.read_csv(path, sep='\t',skiprows=1,header=None,
				names=['code','name'], index_col=False, dtype={'code':str,'name':str})
	return df

def drop_table_if_exists(table_name):
	try:
		cur.execute("""DROP TABLE {table_name};""".format(table_name=table_name))
	except:
		pass
	conn.commit()

def create_area_code_table():
	drop_table_if_exists(OE_Constants.AREA_CODE_TABLE)
	cur.execute("""CREATE TABLE area_code
					(code text not null primary key,
					state_code text not null,
					area_code text not null,
					area_type_code text not null,
					name text not null)""")
	insert_into_area_code_table()

def insert_into_area_code_table():
	with open(OE_Constants.AREA_CODE_PATH) as f:
		next(f)
		for line in f:
			insert_one_into_area_code_table(line)

def insert_one_into_area_code_table(line):
	sc,ac,atc,n = line.strip().split('\t')
	code = atc+ac
	cur.execute("""INSERT INTO area_code VALUES 
				("{code}","{sc}","{ac}","{atc}","{n}");
				""".format(code=code,sc=sc,ac=ac,atc=atc,n=n) )

def create_series_code_table():
	# drop_table_if_exists('series_code')
	cur.execute("""CREATE TABLE series_code
				(code text not null primary key,
				occupation_code text not null,
				industry_code text not null,
				area_code text not null,
				data_type text not null,
				complete boolean not null,
				exist boolean not null,
				foreign key (occupation_code) REFERENCES occupation_code(code),
				foreign key (industry_code) REFERENCES industry_code(code)
				foreign key (area_code) REFERENCES area_code(code));""")

def select_codes(table):
	ret = cur.execute( """SELECT code from {};""".format(table) ).fetchall()
	ret = [ i[0] for i in ret ]
	return ret

def occupation_codes():
	codes = select_codes(OE_Constants.OCCUPATION_CODE_TABLE)
	codes = [ code for code in codes if code[3:]=='000' ]
	return codes

def insert_many_areas_into_series_code_table():
	prefix = OE_Constants.SERIES_PREFIX
	for area_code in select_codes(OE_Constants.AREA_CODE_TABLE):
		for industry_code in OE_Constants.INDUSTRY_CODES:
			for occupation_code in occupation_codes():
				for data_type in OE_Constants.DATA_TYPES:
					code = prefix + area_code + industry_code + occupation_code + data_type
					insert_one_into_series_code_table(code,occupation_code,industry_code,area_code,data_type)
	conn.commit()

def insert_one_into_series_code_table(code,oc,ic,ac,dt,complete='0',exist='0',cursor=cur):
	# try:
		cursor.execute("""INSERT INTO series_code VALUES 
		('{code}','{oc}','{ic}','{ac}','{dt}',{complete},{exist})
		;""".format( code=code,oc=oc,ic=ic,ac=ac,dt=dt,
					complete=complete,exist=exist  ) )
	# except:
		# print("non-unique series_code",code)
		# print( get_name_from_code('occupation_code',oc),
		# get_name_from_code('area_code',ac),
		# get_name_from_code('industry_code',ic) )

def create_value_table():
	cur.execute("""CREATE TABLE IF NOT EXISTS {}
					(series_code text not null,
					year integer not null,
					period text not null,
					data_date date not null,
					value real not null,
					primary key(series_code,data_date)
					foreign key(series_code) REFERENCES series_code(code) )""".format(OE_Constants.VALUE_TABLE))

def insert_all_occupations_into_series_code_table():
	prefix = OE_Constants.SERIES_PREFIX
	area_code = OE_Constants.NATIONAL_AREA_CODE
	for occupation_code in select_codes('occupation_code'):
		for data_type in OE_Constants.DATA_TYPES:
			for industry_code in OE_Constants.INDUSTRY_CODES:
				code = prefix + area_code + industry_code + occupation_code + data_type
				insert_one_into_series_code_table(code,occupation_code,industry_code,area_code,data_type)
	conn.commit()

def get_name_from_code(table_name,code):
	ret = cur.execute("""SELECT name from {table_name}
			WHERE code='{code}';""".format(
				table_name=table_name, code = code) ).fetchall()
	return ret[0][0]

def new_occ_group_table():
	drop_table_if_exists('occ_group')
	cur.execute("""CREATE TABLE occ_group 
					(code text not null primary key,
					group_name text not null
					)""")

def rem_hyphen(s):
	ret = s.replace('-','')
	return ret

def load_occ_grps():
	df = pd.read_csv('group_names.csv')
	ret = defaultdict(list)
	for _,row in df.iterrows():
		ret[ row['group_name'] ].append( str( row['occ_code'] ) )
	return ret

def create_occ_group_table():
	new_occ_group_table()
	for grp in grps:
		for code in grps[grp]:
			code = rem_hyphen(code)
			insert_one_into_occ_group_table(code,grp)
	conn.commit()

def insert_one_into_occ_group_table(code,group_name):
	# name = get_name_from_code('occupation_code',code)
	try:
		cur.execute("""INSERT into occ_group VALUES
	( '{code}'  , '{group_name}' )""".format(
		code=code,#name=name.replace("'","''"),
		group_name=group_name.replace("'","''")) )
	except:
		print(code,'|',name,'|',group_name)

def insert_all_areas_occupations_into_series_code_table():
	prefix = OE_Constants.SERIES_PREFIX
	for area_code in select_codes(OE_Constants.AREA_CODE_TABLE):
		for industry_code in OE_Constants.INDUSTRY_CODES:
			for occupation_code in select_codes('occ_group'):
				for data_type in OE_Constants.DATA_TYPES:
					code = prefix + area_code + industry_code + occupation_code + data_type
					insert_one_into_series_code_table(code,occupation_code,industry_code,area_code,data_type)
	conn.commit()

if __name__ == '__main__':
	grps = load_occ_grps()
	create_table_with_df(OE_Constants.OCCUPATION_CODE_PATH,OE_Constants.OCCUPATION_CODE_TABLE)
	create_table_with_df(OE_Constants.INDUSTRY_CODE_PATH,OE_Constants.INDUSTRY_CODE_TABLE)
	create_table_with_df(OE_Constants.STATE_CODE_PATH,OE_Constants.STATE_CODE_TABLE)
	create_table_with_df(OE_Constants.DATA_TYPE_PATH,OE_Constants.DATA_TYPE_TABLE)
	create_table_with_df(OE_Constants.STATE_ABBREV_PATH,OE_Constants.STATE_ABBREV_TABLE)

	create_area_code_table()
	create_series_code_table()
	insert_all_occupations_into_series_code_table()
	create_value_table()
	create_occ_group_table()

	conn.commit()

