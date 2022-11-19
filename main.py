from benchmark import Benchmark

int_image_dir = "/home/samee/Downloads/synthetic1_nrois=10,50/int"
seg_image_dir = "/home/samee/Downloads/synthetic1_nrois=10,50/seg"
work_dir = "/home/samee/axle/dev/nyxus_paper/nyxus_work_dir"
nyxus_executable = "/home/samee/axle/dev/nyxus_paper/nyxus/build_man/nyxus"
feature_list = "*ALL*"
generate_missing_image = False

if __name__ == '__main__':
    benchmark = Benchmark(  int_image_dir,
                            seg_image_dir,
                            work_dir, 
                            nyxus_executable, 
                            feature_list, 
                            generate_missing_image
                        )


    benchmark.run_benchmark_suit()
    benchmark.create_benchmark_plot("Total", "All", "All")

    #benchmark.get_benchmark_data(50, 100, "*ALL*")