import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, Tuple, Optional
from fs import clean
import os

class IVAnalyzer:
    """
    This class provides methods for analyzing current-voltage characteristics
    of semiconductor/metal materials across different temperatures 
    by rounding up temperatures of different ranges into groups and providing the corresponding
    graphs with their respective slopes.
    """
    
    def __init__(self, sample_area: float = 32e-6):
        """
        Laucher of class IVAnalyzer
        
        Parameters:
        -----------
        sample_area [geometry needed for the device being measured] : float
            Sample area in m² (default: 32e-6 m^2 - this was the default value in the 
            original code and may be modified based on the actual sample area being tested)
        """
        self.sample_area = sample_area
        self.results = {}
        
    def load_and_process_data(self, filepath: str, data_type: str = 'metal') -> pd.DataFrame:
        """
        Load and process I-V data from file
        
        Parameters:
        -----------
        filepath : str
            Path to the data file
        data_type : str
            Type of material ('metal' or 'semiconductor') [doesn't work for thin films]
            
        Returns:
        --------
        pd.DataFrame
            Processed dataframe with current density calculations or and I-V characteristics
        """
        try:
            from fs import clean
            df = clean(filepath)
            
            if df.empty:
                raise ValueError("No data found in file")
                
            #current density calculation 
            if data_type == 'metal':
                df['current_density'] = df['i-v_current_ch1_ma'] / self.sample_area
                df['temperature_group'] = df['temperature_k'].round(0)
                
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error processing data: {str(e)}")
    
    def calculate_conductivity_slopes(self, df: pd.DataFrame) -> Dict[float, Dict]:
        """
        Calculate temperature-dependent conductivity slopes with statistical validation
        
        Parameters:
        -----------
        df : pd.DataFrame
            Processed I-V data with temperature groups
            
        Returns:
        --------
        Dict[float, Dict]
            Dictionary containing slope analysis results for each temperature
        """
        slopes_data = {}
        
        for temp, group in df.groupby('temperature_group'):
            # Extract V and J
            voltage = group['i-v_voltage_ch1_v']
            current_density = group['current_density']
            
            # Remove NaN values
            valid_mask = voltage.notna() & current_density.notna() #ensures that both voltage and current density are valid!!
            x = voltage[valid_mask]
            y = current_density[valid_mask]
            
            # Check for sufficient data points
            if len(x) < 3 or x.nunique() < 2:
                print(f"Warning: Insufficient data for temperature {temp} K")
                continue
                
            # Calculate slope 
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            slopes_data[temp] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'std_error': std_err,
                'n_points': len(x),
                'conductivity': slope  # For metals, slope ≈ conductivity
            }
            
        return slopes_data
    
    def create_iv_plots(self, df: pd.DataFrame, save_path: Optional[str] = None, 
                       show_plots: bool = True, dpi: int = 300) -> None:
        """
        Generate publication-quality I-V characteristic plots
        
        Parameters:
        -----------
        df : pd.DataFrame
            Processed I-V data
        save_path : str, optional
            Directory to save plots
        show_plots : bool
            Whether to display plots
        dpi : int
            Resolution for saved plots
        """
        
        for temp, group in df.groupby('temperature_group'):
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Create scatter plot
            ax.scatter(group['i-v_voltage_ch1_v'], group['current_density'], 
                      color='black', marker='.', alpha=0.7, s=20)
            
            # Add linear fit line if we have slope data
            if hasattr(self, 'slope_results') and temp in self.slope_results:
                x_fit = np.linspace(group['i-v_voltage_ch1_v'].min(), 
                                   group['i-v_voltage_ch1_v'].max(), 100)
                y_fit = (self.slope_results[temp]['slope'] * x_fit + 
                        self.slope_results[temp]['intercept'])
                ax.plot(x_fit, y_fit, 'r--', alpha=0.8, linewidth=2, 
                       label=f'Linear fit (R² = {self.slope_results[temp]["r_squared"]:.3f})')
            
            # Formatting
            ax.set_xlabel('Voltage (V)', fontsize=12)
            ax.set_ylabel('Current Density (mA/m²)', fontsize=12)
            ax.set_title(f'I-V Characteristics at {temp:.0f} K', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            if hasattr(self, 'slope_results') and temp in self.slope_results:
                ax.legend()
            
            plt.tight_layout()
            
            # Save plot if path provided
            if save_path:
                os.makedirs(save_path, exist_ok=True)
                filename = f'iv_characteristic_{int(temp)}K.png'
                plt.savefig(os.path.join(save_path, filename), dpi=dpi, bbox_inches='tight')
            
            if show_plots:
                plt.show()
            else:
                plt.close()
    
    def generate_analysis_report(self, slopes_data: Dict[float, Dict]) -> str:
        """
        Generate a comprehensive analysis report
        
        Parameters:
        -----------
        slopes_data : Dict[float, Dict]
            Results from conductivity slope analysis
            
        Returns:
        --------
        str
            Formatted analysis report
        """
        report = []
        report.append("=" * 60)
        report.append("I-V CHARACTERISTICS ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Sample Area: {self.sample_area:.2e} m²")
        report.append(f"Number of Temperature Points: {len(slopes_data)}")
        report.append("")
        
        report.append("TEMPERATURE-DEPENDENT CONDUCTIVITY ANALYSIS:")
        report.append("-" * 50)
        
        for temp in sorted(slopes_data.keys()):
            data = slopes_data[temp]
            report.append(f"Temperature: {temp:.0f} K")
            report.append(f"  Slope (Conductivity): {data['slope']:.2f} mA/m²/V")
            report.append(f"  R-squared: {data['r_squared']:.4f}")
            report.append(f"  P-value: {data['p_value']:.2e}")
            report.append(f"  Standard Error: {data['std_error']:.2f}")
            report.append(f"  Data Points: {data['n_points']}")
            report.append("")
        
        # Add temperature trend analysis
        temps = sorted(slopes_data.keys())
        conductivities = [slopes_data[t]['slope'] for t in temps]
        
        if len(temps) > 2:
            temp_slope, _, temp_r, temp_p, _ = stats.linregress(temps, conductivities)
            report.append("TEMPERATURE DEPENDENCE:")
            report.append(f"  Conductivity vs Temperature Slope: {temp_slope:.4f} mA/m²/V/K")
            report.append(f"  Temperature Correlation R²: {temp_r**2:.4f}")
            report.append(f"  Temperature Correlation P-value: {temp_p:.2e}")
        
        return "\n".join(report)
    
    def analyze_complete_dataset(self, filepath: str, save_path: Optional[str] = None) -> Dict:
        """
        Complete analysis pipeline for I-V data
        
        Parameters:
        -----------
        filepath : str
            Path to data file
        save_path : str, optional
            Directory to save results
            
        Returns:
        --------
        Dict
            Complete analysis results
        """
        # Load and process data
        df = self.load_and_process_data(filepath, 'metal')
        
        # Calculate slopes
        self.slope_results = self.calculate_conductivity_slopes(df)
        
        # Create plots
        self.create_iv_plots(df, save_path)
        
        # Generate report
        report = self.generate_analysis_report(self.slope_results)
        
        # Save report if path provided
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            with open(os.path.join(save_path, 'analysis_report.txt'), 'w') as f:
                f.write(report)
        
        print(report)
        
        return {
            'data': df,
            'slopes': self.slope_results,
            'report': report
        }

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = IVAnalyzer(sample_area=32e-6)
    
    # Run complete analysis
    path = r"C:\Users\Famil\Desktop\DATA ANALYSIS\experimental data\data\ETO_IV_metal_9T.dat"
    plot_path = r"C:\Users\Famil\Desktop\DATA ANALYSIS\experimental data\plots"
    
    results = analyzer.analyze_complete_dataset(path, save_path=plot_path)
    
    # Access individual results
    print("\nSlope Results:")
    for temp, data in results['slopes'].items():
        print(f"T = {temp} K: Slope = {data['slope']:.2f} ± {data['std_error']:.2f}")

