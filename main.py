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

    n_rois = [10, 50, 100]
    roi_areas = [100, 500, 1000]
    padding = 5
    percent_oversized_roi = 30

    for n_roi in n_rois:
        for roi_size in roi_areas:
            dataset_generator.generate_image_pair(n_roi ,roi_size, padding, percent_oversized_roi)


    benchmark = Benchmark(  int_image_dir,
                            seg_image_dir,
                            work_dir, 
                            nyxus_executable, 
                            feature_list, 
                            generate_missing_image
                        )


    benchmark.run_benchmark_suit()
    benchmark.create_benchmark_plot("Total", "All", "All")
