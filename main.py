from benchmark import Benchmark
from datageneration import DatasetGenerator

int_image_dir = "/home/samee/axle/dev/nyxus_paper/nyxus_benchmark/int"
seg_image_dir = "/home/samee/axle/dev/nyxus_paper/nyxus_benchmark/seg"
work_dir = "/home/samee/axle/dev/nyxus_paper/nyxus_work_dir"
nyxus_executable = "/home/samee/axle/dev/nyxus_paper/nyxus/build_man/nyxus"
feature_list = "*ALL*"
generate_missing_image = False
base_mask_image_path = "/home/samee/axle/dev/nyxus_paper/nyxus_benchmark/arnoldcat_pure_cat.jpg"
base_intensity_image_path = "/home/samee/axle/dev/nyxus_paper/nyxus_benchmark/Siemens_star.tif"


if __name__ == '__main__':

    dataset_generator = DatasetGenerator(   int_image_dir,
                                            seg_image_dir,
                                            base_mask_image_path,
                                            base_intensity_image_path)

    dataset_generator.generate_image_pair(100,1000,5)
    dataset_generator.generate_image_pair(1000,1000,5)

    benchmark = Benchmark(  int_image_dir,
                            seg_image_dir,
                            work_dir, 
                            nyxus_executable, 
                            feature_list, 
                            generate_missing_image
                        )


    benchmark.run_benchmark_suit()
    benchmark.create_benchmark_plot("Total", "All", "All")
