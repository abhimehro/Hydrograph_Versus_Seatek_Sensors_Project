import unittest
from pathlib import Path

from pandas import DataFrame , Series
from utils import (
	clean_data , create_output_dir , format_sensor_name , get_project_root , load_excel_file , validate_numeric_data ,
	)


class TestUtils ( unittest.TestCase ) :
	
	def test_get_project_root ( self ) :
		root = get_project_root ( )
		self.assertTrue ( isinstance ( root , Path ) )
		self.assertTrue ( root.exists ( ) )
	
	def test_validate_numeric_data ( self ) :
		data = Series ( [ 1 , 2 , 3 , None , float ( 'inf' ) , -float ( 'inf' ) , 0 , -1 ] )
		validated_data = validate_numeric_data ( data )
		expected_data = Series ( [ 1 , 2 , 3 ] )
		self.assertTrue ( validated_data.equals ( expected_data ) )
	
	def test_clean_data ( self ) :
		data = DataFrame (
				{
						'A' : [ 1 , 2 , 3 , None , float ( 'inf' ) , -float ( 'inf' ) , 0 , -1 ] ,
						'B' : [ 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 ]
						}
				)
		required_columns = [ 'A' , 'B' ]
		cleaned_data = clean_data ( data , required_columns )
		expected_data = DataFrame (
				{
						'A' : [ 1 , 2 , 3 ] ,
						'B' : [ 1 , 2 , 3 ]
						}
				)
		self.assertTrue ( cleaned_data.equals ( expected_data ) )
	
	def test_format_sensor_name ( self ) :
		sensor = "Sensor_1"
		formatted_name = format_sensor_name ( sensor )
		self.assertEqual ( formatted_name , "Sensor 1" )
	
	def test_load_excel_file ( self ) :
		file_path = Path ( 'test_data.xlsx' )
		# Create a test Excel file
		df = DataFrame ( { 'A' : [ 1 , 2 , 3 ] , 'B' : [ 4 , 5 , 6 ] } )
		df.to_excel ( file_path , index = False )
		loaded_df = load_excel_file ( file_path )
		self.assertTrue ( loaded_df.equals ( df ) )
		file_path.unlink ( )  # Clean up the test file
	
	def test_create_output_dir ( self ) :
		rm = 1.0
		output_dir = create_output_dir ( rm )
		self.assertTrue ( output_dir.exists ( ) )
		self.assertTrue ( output_dir.is_dir ( ) )
		output_dir.rmdir ( )  # Clean up the test directory


if __name__ == '__main__' :
	unittest.main ( )
