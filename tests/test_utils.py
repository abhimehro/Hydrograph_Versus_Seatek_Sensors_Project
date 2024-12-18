import unittest
from pathlib import Path
from unittest.mock import patch

from pandas import DataFrame
from src.visualization import (
	create_visualization ,
	DataVisualizationError ,
	save_visualization ,
	setup_plot_style ,
	)

# Check if matplotlib is available to gracefully skip tests that require it
try :
	from matplotlib.figure import Figure
	
	has_matplotlib = True
except ImportError :
	has_matplotlib = False


class TestVisualization ( unittest.TestCase ) :
	
	def setUp ( self ) :
		"""
		Set up shared test resources to avoid redundancy.
		"""
		self.plot_data = DataFrame (
				{
						"Time_(Hours)" : [ 0 , 1 , 2 , 3 ] ,
						"Hydrograph (Lagged)" : [ 10 , 20 , 30 , 40 ] ,
						"Sensor_1" : [ 15 , 25 , 35 , 45 ] ,
						}
				)
		self.column_mappings = {
				"time" : "Time_(Hours)" ,
				"hydrograph" : "Hydrograph (Lagged)" ,
				"year" : "Year" ,
				}
		self.output_path = Path ( "test_output.png" )
	
	def tearDown ( self ) :
		"""Clean up after tests if needed."""
		if self.output_path.exists ( ) :
			self.output_path.unlink ( )  # Ensure test output files are removed
	
	def test_setup_plot_style ( self ) :
		"""
		Test that setup_plot_style() executes without exceptions.
		"""
		try :
			setup_plot_style ( )
		except Exception as e :
			self.fail ( f"setup_plot_style() raised an exception: {e}" )
	
	@unittest.skipIf ( not has_matplotlib , "matplotlib is required for this test" )
	def test_create_visualization ( self ) :
		"""
		Test that create_visualization() generates the expected outputs.
		"""
		try :
			fig , correlation = create_visualization (
					self.plot_data , 1.0 , 2023 , "Sensor_1" , self.column_mappings
					)
			self.assertIsInstance ( fig , Figure )
			self.assertIsInstance ( correlation , float )
		except DataVisualizationError as e :
			self.fail ( f"create_visualization() raised DataVisualizationError: {e}" )
	
	@unittest.skipIf ( not has_matplotlib , "matplotlib is required for this test" )
	@patch ( "src.visualization.Path.exists" )
	@patch ( "src.visualization.Path.unlink" )
	def test_save_visualization ( self , mock_unlink , mock_exists ) :
		"""
		Test that save_visualization() saves the figure and performs cleanup.
		"""
		mock_exists.return_value = True  # Mock that the file exists
		
		# Create the visualization to save
		fig , _ = create_visualization (
				self.plot_data , 1.0 , 2023 , "Sensor_1" , self.column_mappings
				)
		
		try :
			save_visualization ( fig , self.output_path )
			self.assertTrue ( self.output_path.exists ( ) )  # File should exist
		except DataVisualizationError as e :
			self.fail ( f"save_visualization() raised DataVisualizationError: {e}" )
		
		# Assertions to ensure file cleanup occurred
		mock_unlink.assert_called_once ( )
		mock_exists.assert_called_once ( )
	
	def test_invalid_column_mapping ( self ) :
		"""
		Test that create_visualization() raises an error for invalid column mappings.
		"""
		invalid_column_mappings = {
				"invalid_key" : "Time_(Hours)" ,  # This key doesn't exist in the DataFrame
				}
		with self.assertRaises ( DataVisualizationError ) :
			create_visualization (
					self.plot_data , 1.0 , 2023 , "Sensor_1" , invalid_column_mappings
					)
	
	def test_empty_plot_data ( self ) :
		"""
		Test that create_visualization() raises an error for empty plot_data.
		"""
		empty_data = DataFrame ( )  # Empty DataFrame
		with self.assertRaises ( DataVisualizationError ) :
			create_visualization (
					empty_data , 1.0 , 2023 , "Sensor_1" , self.column_mappings
					)
	
	def test_insufficient_numeric_data ( self ) :
		"""
		Test that create_visualization() raises an error for insufficient valid data.
		"""
		insufficient_data = DataFrame (
				{
						"Time_(Hours)" : [ 0 ] ,
						"Hydrograph (Lagged)" : [ 10 ] ,
						"Sensor_1" : [ 15 ] ,
						}
				)  # Only one data point
		with self.assertRaises ( DataVisualizationError ) :
			create_visualization (
					insufficient_data , 1.0 , 2023 , "Sensor_1" , self.column_mappings
					)


if __name__ == "__main__" :
	unittest.main ( )
`
