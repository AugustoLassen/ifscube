# Parallelization Implementation Guide for ifscube

This document provides technical details about the parallelization implementation in the ifscube package.

## Overview of Changes

The parallelization implementation focuses on distributing the processing of spatial pixels across multiple CPU cores. The main bottleneck in the original implementation was the sequential processing of each spaxel in a data cube, which has been addressed by implementing a parallel processing framework.

## Key Components

### 1. `parallel_utils.py`

This new module provides the core functionality for parallel processing:

- `get_optimal_workers()`: Determines the optimal number of worker processes based on system resources
- `process_spaxel()`: Wrapper function for processing a single spaxel in parallel
- `parallel_map()`: Generic function to apply a function to items in parallel
- `parallel_process_cube()`: Specialized function for processing data cube spaxels in parallel

### 2. `LineFit3D.fit_parallel()` Method

A new method added to the `LineFit3D` class that:

- Prepares the data cube for parallel processing
- Distributes spaxels across multiple worker processes
- Collects and combines results from all processes
- Returns the fitted object with all results integrated

### 3. Modified `fitter.py`

The `do_fit()` function has been enhanced to:

- Accept new parameters for controlling parallelization (`n_workers`, `parallel`)
- Automatically use parallel processing for cube data when enabled
- Provide timing information for performance monitoring

## Implementation Details

### Parallelization Strategy

The implementation uses Python's `concurrent.futures.ProcessPoolExecutor` for parallel processing, which:

1. Creates a pool of worker processes
2. Distributes tasks (spaxels) to these processes
3. Collects results as they complete
4. Handles exceptions gracefully

### Data Independence

The parallelization works because each spaxel can be processed independently:

- No data dependencies between different spatial positions
- Results from one spaxel don't affect the processing of others
- Each worker process gets a copy of the necessary data

### Memory Management

Care has been taken to minimize memory usage:

- Only essential data is copied to worker processes
- Results are collected and integrated efficiently
- Temporary objects are cleaned up properly

### Error Handling

The implementation includes robust error handling:

- Exceptions in worker processes are caught and reported
- Failed spaxels are marked with appropriate status codes
- The main process continues even if some spaxels fail

## Performance Considerations

### Optimal Number of Workers

The default is to use 75% of available CPU cores, which balances:

- Processing speed (more workers = faster processing)
- Memory usage (more workers = higher memory consumption)
- System responsiveness (leaving some cores free for other tasks)

### When to Use Parallelization

Parallelization is most beneficial for:

- Large data cubes with many spaxels
- Complex fitting procedures with many parameters
- Systems with multiple CPU cores

For very small cubes or simple fits, the overhead of parallelization might outweigh the benefits.

### Scaling

Performance scaling depends on:

- Number of spaxels in the data cube
- Complexity of the fitting procedure
- Number of available CPU cores
- Memory constraints

In ideal conditions, speedup is approximately linear with the number of cores up to a certain point.

## Compatibility Notes

The parallelized version maintains compatibility with the original API:

- All existing scripts and workflows should continue to work
- New parallelization options are optional and have sensible defaults
- Sequential processing can still be used when preferred

## Future Improvements

Potential areas for further enhancement:

- Implement shared memory for large data structures to reduce memory usage
- Add support for distributed processing across multiple nodes in a cluster
- Optimize the chunking strategy for different types of data cubes
- Implement adaptive worker pool sizing based on system load
