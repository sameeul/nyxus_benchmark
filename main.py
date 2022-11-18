from benchmark import Benchmark

if __name__ == '__main__':
    benchmark = Benchmark("/home/samee/Downloads/synthetic1_nrois=10,50/int",
                            "/home/samee/Downloads/synthetic1_nrois=10,50/seg",
                            "/home/samee/axle/dev/nyxus_paper/nyxus/data", 
                            "/home/samee/axle/dev/nyxus_paper/nyxus/build_man/nyxus",
                            False)

    # benchmark.get_benchmark_data(10,500)
    # benchmark.get_benchmark_data(10,10)
    # benchmark.merge_results()
    benchmark.run_benchmark_suit()