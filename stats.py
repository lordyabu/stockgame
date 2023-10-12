import pstats

p = pstats.Stats('profiling_results.out')
p.sort_stats('time').print_stats(10)  # Sort by time and display top 10 functions
