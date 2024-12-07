"""
Functions to calculate and explain the correlation between hydrograph and sensor data.
This implementation demonstrates how Pearson correlation is calculated and applied
to our hydrograph vs. sensor analysis.
"""

from typing import List , Tuple , Union

import numpy as np


def calculate_correlation(
    hydrograph_data: Union[List[float], np.ndarray],
    sensor_data: Union[List[float], np.ndarray]
) -> Tuple[float, str]:
    """
    Calculate the Pearson correlation coefficient between hydrograph and sensor data
    and provide an interpretation of the relationship.
    
    The Pearson correlation coefficient measures the strength and direction of the
    linear relationship between two variables. The coefficient ranges from -1 to 1:
    * 1: Perfect positive correlation (as one increases, the other increases proportionally)
    * 0: No linear correlation
    * -1: Perfect negative correlation (as one increases, the other decreases proportionally)
    
    Args:
        hydrograph_data: List or array of hydrograph discharge values [gpm]
        sensor_data: List or array of sensor readings [mm]
    
    Returns:
        tuple: (correlation coefficient, interpretation string)
    
    Example:
        >>> hydro = [1, 2, 3, 4, 5]
        >>> sensor = [2, 4, 6, 8, 10]
        >>> coef, interp = calculate_correlation(hydro, sensor)
        >>> print(f"Correlation: {coef}")  # Output: 1.0 (perfect positive correlation)
    """
    # Convert inputs to numpy arrays for calculation
    x = np.array(hydrograph_data)
    y = np.array(sensor_data)
    
    # Calculate means
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Calculate deviations from means
    x_dev = x - x_mean
    y_dev = y - y_mean
    
    # Calculate correlation coefficient using the formula:
    # r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² * Σ(y - ȳ)²)
    numerator = np.sum(x_dev * y_dev)
    denominator = np.sqrt(np.sum(x_dev**2) * np.sum(y_dev**2))
    
    # Avoid division by zero
    if denominator == 0:
        return 0.0, "No correlation (insufficient variation in data)"
    
    correlation = numerator / denominator
    
    # Interpret the correlation strength
    interpretation = interpret_correlation(correlation)
    
    return correlation, interpretation

def interpret_correlation(correlation: float) -> str:
    """
    Provide a textual interpretation of the correlation coefficient.
    
    Args:
        correlation: The calculated correlation coefficient
    
    Returns:
        str: A description of the correlation strength and direction
    """
    abs_corr = abs(correlation)
    direction = "positive" if correlation >= 0 else "negative"
    
    if abs_corr >= 0.9:
        strength = "Very strong"
    elif abs_corr >= 0.7:
        strength = "Strong"
    elif abs_corr >= 0.5:
        strength = "Moderate"
    elif abs_corr >= 0.3:
        strength = "Weak"
    else:
        strength = "Very weak or no"
    
    return f"{strength} {direction} correlation"

# Example usage with explanation:
def explain_correlation_example():
    """
    Demonstrate correlation calculation with a simple example.
    """
    # Sample data
    hydrograph = [2.0, 4.0, 6.0, 8.0, 10.0]  # Discharge measurements
    sensor = [1.0, 2.1, 2.9, 4.2, 5.0]       # Sensor readings
    
    correlation, interpretation = calculate_correlation(hydrograph, sensor)
    
    print("Correlation Analysis Example:")
    print("-----------------------------")
    print("Hydrograph measurements:", hydrograph)
    print("Sensor readings:", sensor)
    print(f"Correlation coefficient: {correlation:.2f}")
    print(f"Interpretation: {interpretation}")
    print("\nWhat this means:")
    print("----------------")
    print("- The correlation coefficient of {:.2f} indicates a {} relationship".format(
        correlation, "positive" if correlation > 0 else "negative"))
    print("- This means that as hydrograph discharge increases, sensor readings tend to",
          "increase" if correlation > 0 else "decrease")
    print(f"- The strength of this relationship is captured in the magnitude: {abs(correlation):.2f}")
    print("- Values closer to 1 or -1 indicate stronger relationships")
    print("- Values closer to 0 indicate weaker relationships")
    
if __name__ == "__main__":
    explain_correlation_example()