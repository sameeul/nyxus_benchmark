# nyxus_benchmark

The `requirements.txt` file lists all the required top-level dependencies. To install them, use `pip install -r requirements.txt`.


There are two classes `DatasetGenerator` and `Benchmark`.
`DatasetGenerator` can be initialized like the following:
```
dataset_generator = DatasetGenerator(   int_image_dir,
                                        seg_image_dir,
                                        base_mask_image_path,
                                        base_intensity_image_path)
```

Once initialized, an image pair can be created like the following:
```
dataset_generator.generate_image_pair(n_roi ,roi_size, padding)
```

Once image pairs are generated, the benchmark data can be gathered using the `Benchmark` class.
```
benchmark = Benchmark(  int_image_dir,
                        seg_image_dir,
                        work_dir, 
                        nyxus_executable, 
                        feature_list, 
                        generate_missing_image
                    )


benchmark.run_benchmark_suit()
```

After running benchmark data, `h1`, `h2` and `h3` header from the performance reporting csv can be used to generate the plot like the following:
```
benchmark.create_benchmark_plot("Total", "All", "All")
```

`main.py` file has a complete working example.
