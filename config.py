import pandas as pd
from typing import NamedTuple, Callable, List
import operator

DB_PATH = 'OE.db'

DATA_FOLDER = 'data'
FULL_FOLDER = 'full'
NAT_FOLDER = 'nat'
STATE_FOLDER = 'state'
METRO_FOLDER = 'metro'
FINAL_OCCS = pd.read_csv("OE/occupation_codes_simple_2018.txt", sep="\t")
DATA_CODE_AGG_FUNCS = {'01':'sum','13':'mean'}

class Transformation(NamedTuple):
	from_code: str
	to_code: str

class TransformationGroup(NamedTuple):
	year: int
	operation: Callable
	transformations: List[Transformation]

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
	OCCUPATION_CODE_PATH ='OE/occupation_codes_simple_2018.txt'
	STATE_AREA_CODE_TABLE = 'state_area_code'
	SERIES_CODE_TABLE = 'series_code'
	STATEWIDE_CODE = '00000'
	SERIES_PREFIX = 'OEU'
	DATA_TYPES = ['13','01']
	VALUE_TABLE = 'value'
	INDUSTRY_CODES = ['000000']
	NATIONAL_AREA_CODE = 'N0000000'
	ALL_INDUSTRY_CODE = '000000'


class XLS_Constants(object):
	def __init__(self):
		self.transformations = []
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
		self.add_transformations()

	def add_transformations(self):
		self.transformation_groups = []
		self.degrouping_transformation_groups = []
		# 2010 transformations
		transformations_2010 = self.get_transformations_2010()
		transformation_group = TransformationGroup(transformations=transformations_2010, year=2010, operation=operator.le)
		self.transformation_groups.append(transformation_group)
		# 2018 transformations
		transformations_2018 = self.get_transformations_2018()
		transformation_group = TransformationGroup(transformations=transformations_2018, year=2018, operation=operator.le)
		self.transformation_groups.append(transformation_group)
		# 2010 transformation degrouping
		group_2010_transformations = self.get_group_2010_transformations()
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=group_2010_transformations, year=2010, operation=operator.eq))
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=group_2010_transformations, year=2011, operation=operator.eq))
		# 2018 transformations
		transformations_2018 = self.get_group_transformations_2018()
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=transformations_2018, year=2019, operation=operator.eq))
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=transformations_2018, year=2018, operation=operator.eq))
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=transformations_2018, year=2017, operation=operator.eq))
		# 2019 transformations
		transformations_2019 = self.get_group_transformations_2019()
		self.degrouping_transformation_groups.append(TransformationGroup(transformations=transformations_2019, year=2019, operation=operator.eq))

	def get_transformations_2010(self):
		crosswalk_2010_df = pd.read_excel('soc_2000_to_2010_crosswalk.xls',skiprows=6)
		transformations = [
			Transformation(from_code=row["2000 SOC code"], to_code=row["2010 SOC code"])
			for _,row in crosswalk_2010_df.iterrows()
		]
		##
		transformations.append(Transformation(from_code='29-1111', to_code='29-1141'))
		transformations.append(Transformation(from_code='13-1079', to_code='13-1071'))
		transformations.append(Transformation(from_code='13-1078', to_code='13-1071'))
		transformations.append(Transformation(from_code='33-9032', to_code='33-9032'))
		transformations.append(Transformation(from_code='27-3031', to_code='27-3031'))
		transformations.append(Transformation(from_code='47-2111', to_code='47-2111'))
		transformations.append(Transformation(from_code='13-1121', to_code='13-1121'))
		transformations.append(Transformation(from_code='13-1071', to_code='13-1071'))
		transformations.append(Transformation(from_code='21-1091', to_code='21-1091'))
		transformations.append(Transformation(from_code='21-1099', to_code='21-1099'))
		transformations.append(Transformation(from_code='15-1081', to_code='15-1152'))
		transformations.append(Transformation(from_code='29-2099', to_code='29-2099'))
		transformations.append(Transformation(from_code='13-1199', to_code='13-1199'))
		transformations.append(Transformation(from_code='49-9099', to_code='49-9099'))
		transformations.append(Transformation(from_code='31-9099', to_code='31-9099'))
		transformations.append(Transformation(from_code='33-9099', to_code='33-9099'))
		transformations.append(Transformation(from_code='47-4099', to_code='47-4099'))
		transformations.append(Transformation(from_code='13-1041', to_code='13-1041'))
		transformations.append(Transformation(from_code='47-2181', to_code='47-2181'))
		transformations.append(Transformation(from_code='41-9099', to_code='41-9099'))
		transformations.append(Transformation(from_code='25-3099', to_code='25-3099'))
		transformations.append(Transformation(from_code='31-1012', to_code='31-1015'))
		transformations.append(Transformation(from_code='51-9199', to_code='51-9199'))
		transformations.append(Transformation(from_code='15-1051', to_code='15-1051'))
		transformations.append(Transformation(from_code='29-9099', to_code='29-9099'))
		transformations.append(Transformation(from_code='29-2034', to_code='29-2034'))
		transformations.append(Transformation(from_code='51-5021', to_code='51-5113'))
		transformations.append(Transformation(from_code='29-1129', to_code='29-1129'))
		transformations.append(Transformation(from_code='23-2092', to_code='23-2011'))
		transformations.append(Transformation(from_code='43-9199', to_code='43-9199'))
		transformations.append(Transformation(from_code='11-9061', to_code='11-9061'))
		transformations.append(Transformation(from_code='49-9021', to_code='49-9021'))
		transformations.append(Transformation(from_code='25-2041', to_code='25-2052'))

		return transformations

	# def get_reverse_transformations_2018

	def get_transformations_2018(self):
		crosswalk_df = pd.read_excel('soc_2010_to_2018_crosswalk.xlsx',skiprows=8)
		transformations = [
			Transformation(from_code=row["2010 SOC Code"], to_code=row["2018 SOC Code"])
			for _,row in crosswalk_df.iterrows()
		]
		transformations.append(Transformation(from_code='29-1069', to_code='29-1229'))
		transformations.append(Transformation(from_code='15-1199', to_code='15-1299'))
		transformations.append(Transformation(from_code='11-9199', to_code='11-9199'))
		transformations.append(Transformation(from_code='39-1021', to_code='39-1022'))
		transformations.append(Transformation(from_code='51-9199', to_code='51-9199'))
		transformations.append(Transformation(from_code='53-1031', to_code='53-1043'))
		transformations.append(Transformation(from_code='29-1067', to_code='29-1242'))
		transformations.append(Transformation(from_code='25-9041', to_code='25-9042'))
		transformations.append(Transformation(from_code='25-3099', to_code='25-3099'))
		transformations.append(Transformation(from_code='29-9099', to_code='29-9099'))
		
		return transformations


	def get_group_transformations_2018(self):
		transformations = [
			Transformation(from_code='13-1020', to_code='13-1023'),
			Transformation(from_code='47-4090', to_code='47-4091'),
			Transformation(from_code='29-2010', to_code='29-2011'),
			Transformation(from_code='39-7010', to_code='39-7011'),
			Transformation(from_code='15-2090', to_code='15-2099'),
			Transformation(from_code='39-1010', to_code='39-1011'),
		]
		return transformations

	def get_group_transformations_2019(self):
		transformations = [
			Transformation(from_code='51-2090', to_code='51-2099'),
			Transformation(from_code='31-1120', to_code='31-1122'),
			Transformation(from_code='11-2030', to_code='11-2031'),
			Transformation(from_code='29-2040', to_code='29-2042'),
			Transformation(from_code='19-4010', to_code='19-4012'),
			Transformation(from_code='27-2090', to_code='27-2099'),
			Transformation(from_code='13-2020', to_code='13-2022'),
			Transformation(from_code='33-1090', to_code='33-1091'),
			Transformation(from_code='11-3010', to_code='11-3011'),
		]
		return transformations

	def get_group_2010_transformations(self):
		transformations = [
			Transformation(from_code='15-1150', to_code='15-1151'),
		]
		
		return transformations

CONSTANTS = XLS_Constants()

def sum_groups_df(df):
	# Aggregate by group. We calculate group totals from constituents, results in more consistent group totals, as totals change per year.
	# WE ALSO SUBSET to only the columns with aggregation functions: DATA_CODE_AGG_FUNCS
	group_values = {}
	INDEX_COLUMNS = ["SERIES_CODE"]
	for data_type_code in ["01"]:
		data_col = CONSTANTS.column_heads["data_codes"][data_type_code]
		agg_func = DATA_CODE_AGG_FUNCS[data_type_code]
		for num_zeros in (1,2,3,4):
			df_copy = df.copy()
			df_copy = df_copy[~df_copy["OCC_CODE"].str.endswith("0")].reset_index(drop=True)
			# df_copy["OCC_CODE"] = df_copy["OCC_CODE"].str.slice(stop=7-num_zeros) + "0"*num_zeros
			df_copy["SERIES_CODE"] = (
				df_copy["SERIES_CODE"].str.slice(stop=25-(2+num_zeros)) + 
				"0"*num_zeros +
				df_copy["SERIES_CODE"].str.slice(start=23)
			)
			agg_df = df_copy[INDEX_COLUMNS + [data_col]].groupby(INDEX_COLUMNS).agg(agg_func).reset_index()
			agg_dict = agg_df.set_index(["SERIES_CODE"])[data_col].to_dict()
			group_values = {**group_values, **agg_dict}
	df[data_col] = [group_values.get(series_code, value)
		for series_code, value 
		in zip(df["SERIES_CODE"], df[data_col])
	]
	return df


def apply_transformation_group(
		transformation_group: TransformationGroup,
		df: pd.DataFrame) -> pd.DataFrame:
	transformation_dict = {
		trans.from_code: trans.to_code for trans in transformation_group.transformations
	}
	df["OCC_CODE"] = df["OCC_CODE"].apply(lambda x: transformation_dict.get(x, x))
	
	return df
	

def apply_occ_transformations(df: pd.DataFrame, year: str) -> pd.DataFrame:
	year = int(year)
	for transformation_group in CONSTANTS.transformation_groups:
		year_condition = transformation_group.operation(year, transformation_group.year)
		if year_condition:
			df = apply_transformation_group(transformation_group, df)
	
	return df


def apply_degrouping_transformations(df: pd.DataFrame, year: str) -> pd.DataFrame:
	year = int(year)
	for transformation_group in CONSTANTS.degrouping_transformation_groups:
		year_condition = transformation_group.operation(year, transformation_group.year)
		if year_condition:
			df = apply_transformation_group(transformation_group, df)
	
	return df
