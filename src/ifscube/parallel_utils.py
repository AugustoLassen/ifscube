import os
import warnings
import numpy as np
import concurrent.futures
import multiprocessing as mp

from functools import partial

def get_optimal_workers():
    """
    Determine the optimal number of worker processes based on system resources.
    
    Returns:
        int: Recommended number of worker processes
    """
    # Get the number of available CPU cores
    cpu_count = mp.cpu_count()
    
    # Use 75% of available cores by default, but at least 1
    optimal_workers = max(1, int(cpu_count * 0.75))
    
    return optimal_workers

def process_spaxel(args):
    """
    Process a single spaxel (wrapper function for parallel processing).
    
    Args:
        args: Tuple containing (y, x, fit_function, fit_args)
            y, x: Coordinates of the spaxel
            fit_function: Function to apply to the spaxel
            fit_args: Arguments for the fit function
            
    Returns:
        tuple: (y, x, result) where result is the output of fit_function
    """
    y, x, fit_function, fit_args = args
    try:
        result = fit_function(y, x, **fit_args)
        return (y, x, result)
    except Exception as e:
        warnings.warn(f"Error processing spaxel at ({y}, {x}): {str(e)}")
        return (y, x, None)

def parallel_map(function, items, n_workers=None, chunksize=1):
    """
    Apply a function to each item in a list in parallel.
    
    Args:
        function: Function to apply to each item
        items: List of items to process
        n_workers: Number of worker processes (default: auto-detect)
        chunksize: Size of chunks for parallel processing
        
    Returns:
        list: Results of applying function to each item
    """
    if n_workers is None:
        n_workers = get_optimal_workers()
    
    # Use ProcessPoolExecutor for better exception handling
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        results = list(executor.map(function, items, chunksize=chunksize))
    
    return results

def parallel_process_cube(fit_function, spaxel_indices, fit_args, n_workers=None, chunksize=10):
    """
    Process multiple spaxels in a data cube in parallel.
    
    Args:
        fit_function: Function to apply to each spaxel
        spaxel_indices: List of (y, x) coordinates for spaxels to process
        fit_args: Arguments to pass to fit_function
        n_workers: Number of worker processes (default: auto-detect)
        chunksize: Size of chunks for parallel processing
        
    Returns:
        dict: Dictionary mapping (y, x) coordinates to results
    """
    if n_workers is None:
        n_workers = get_optimal_workers()
    
    # Prepare arguments for each spaxel
    args_list = [(y, x, fit_function, fit_args) for y, x in spaxel_indices]
    
    # Process spaxels in parallel
    results = parallel_map(process_spaxel, args_list, n_workers, chunksize)
    
    # Convert results to dictionary
    result_dict = {(y, x): result for y, x, result in results if result is not None}
    
    return result_dict
