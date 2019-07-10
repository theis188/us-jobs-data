import pandas as pd

DB_PATH = 'OE.db'

DATA_FOLDER = 'data'
FULL_FOLDER = 'full'
NAT_FOLDER = 'nat'
STATE_FOLDER = 'state'
METRO_FOLDER = 'metro'

class Constants:
	STATE_CODES_PATH = 'SM/state_codes.txt'
	STATE_CODE_TABLE = 'state_code'
	AREA_CODES_PATH = 'SM/area_codes.txt'
	AREA_CODES_TABLE = 'area_code'
	INDUSTRY_CODES_PATH = 'SM/industry_codes.txt'
	INDUSTRY_CODES_TABLE = 'industry_code'
	DATA_TYPES_PATH = 'SM/data_type_codes.txt'
	DATA_TYPES_TABLE = 'data_type'
	STATE_ABBREV_PATH = 'SM/state_abbrev.txt'
	STATE_ABBREV_TABLE = 'state_abbrev'
	STATE_AREA_CODE_TABLE = 'state_area_code'
	SERIES_CODE_TABLE = 'series_code'
	STATEWIDE_CODE = '00000'
	SERIES_PREFIX = 'SMU'
	DATA_TYPES = ['01']
	VALUE_TABLE = 'value'

class OE_Constants:
	STATE_CODE_PATH = 'OE/state_codes.txt'
	STATE_CODE_TABLE = 'state_code'
	AREA_CODE_PATH = 'OE/area_codes.txt'
	AREA_CODE_TABLE = 'area_code'
	INDUSTRY_CODE_PATH = 'OE/industry_codes_simple.txt'
	INDUSTRY_CODE_TABLE = 'industry_code'
	DATA_TYPE_PATH = 'OE/data_types.txt'
	DATA_TYPE_TABLE = 'data_type'
	STATE_ABBREV_PATH = 'OE/state_abbrev.txt'
	STATE_ABBREV_TABLE = 'state_abbrev'
	OCCUPATION_CODE_TABLE='occupation_code'
	OCCUPATION_CODE_PATH ='OE/occupation_codes_simple.txt'
	STATE_AREA_CODE_TABLE = 'state_area_code'
	SERIES_CODE_TABLE = 'series_code'
	STATEWIDE_CODE = '00000'
	SERIES_PREFIX = 'OEU'
	DATA_TYPES = ['13','01']
	VALUE_TABLE = 'value'
	INDUSTRY_CODES = ['000000']
	NATIONAL_AREA_CODE = 'N0000000'
	ALL_INDUSTRY_CODE = '000000'

FULL_COLUMN_HEADS = {
	'2011':{
		'data_codes':{
			'01':'TOT_EMP',
			'02':'EMP_PRSE',
			'03':'H_MEAN',
			'04':'A_MEAN',
			'05':'MEAN_PRSE',
			'06':'H_PCT10',
			'07':'H_PCT25',
			'08':'H_MEDIAN',
			'09':'H_PCT75',
			'10':'H_PCT90',
			'11':'A_PCT10',
			'12':'A_PCT25',
			'13':'A_MEDIAN',
			'14':'A_PCT75',
			'15':'A_PCT90',
			},
		'other_codes':{
				'area_type':'AREA_TYPE',
				'area':'AREA',
				'none':'AREA_TITLE',
				'industry_code':'NAICS',
				'occupation_code':'OCC_CODE',
		}
	}
}

FULL_COLUMN_HEADS['2012'] = { q : { k : FULL_COLUMN_HEADS['2011'][ q ][ k ].lower()
										for k in FULL_COLUMN_HEADS['2011'][ q ] }
										for q in FULL_COLUMN_HEADS['2011'] }

FULL_COLUMN_HEADS['1999'] = { q : { k : FULL_COLUMN_HEADS['2012'][ q ][ k ]
										for k in FULL_COLUMN_HEADS['2012'][ q ] }
										for q in FULL_COLUMN_HEADS['2012'] }

FULL_COLUMN_HEADS['1999']['data_codes']['11']='a_wpct10'
FULL_COLUMN_HEADS['1999']['data_codes']['12']='a_wpct25'
FULL_COLUMN_HEADS['1999']['data_codes']['14']='a_wpct75'
FULL_COLUMN_HEADS['1999']['data_codes']['15']='a_wpct90'


class XLS_Constants(object):
	def __init__(self):
		self.data_u_want = ['11','12','13','14','15','01']
		self.column_heads = {
				'data_codes':{
					'01':'TOT_EMP',
					'02':'EMP_PRSE',
					'03':'H_MEAN',
					'04':'A_MEAN',
					'05':'MEAN_PRSE',
					'06':'H_PCT10',
					'07':'H_PCT25',
					'08':'H_MEDIAN',
					'09':'H_PCT75',
					'10':'H_PCT90',
					'11':'A_PCT10',
					'12':'A_PCT25',
					'13':'A_MEDIAN',
					'14':'A_PCT75',
					'15':'A_PCT90',
					},
				'other_codes':{
						'area_type':'AREA_TYPE',
						'area':'AREA',
						'none':'AREA_TITLE',
						'industry_code':'NAICS',
						'occupation_code':'OCC_CODE',
				}
		}
		self.start_row={
			'2000':39,
			'1999':40,
			'1998':38,
			'1997':38,
		}
		crosswalk_df = pd.read_excel('soc_2000_to_2010_crosswalk.xls',skiprows=6)
		# disagreements = crosswalk_df[ crosswalk_df['2000 SOC code']!=crosswalk_df['2010 SOC code'] ][ ['2000 SOC code','2010 SOC code'] ].reset_index()
		self.crosswalk_2000_to_2010 = {
			str(y2000).strip():str(y2010).strip()
			for y2000,y2010 in
			zip( crosswalk_df['2000 SOC code'],crosswalk_df['2010 SOC code'] )
		}
		self.crosswalk_2000_to_2010['29-1111'] = '29-1141'
		self.crosswalk_2000_to_2010['13-1079'] = '13-1071'
		self.crosswalk_2000_to_2010['33-9032'] = '33-9032'
		self.crosswalk_2000_to_2010['13-1078'] = '13-1071'
		# self.crosswalk_2000_to_2010['13-1199'] = '13-1161'
		self.crosswalk_2000_to_2010['27-3031'] = '27-3031'





