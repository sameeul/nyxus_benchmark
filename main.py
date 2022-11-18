from benchmark import Benchmark

if __name__ == '__main__':
    benchmark = Benchmark("/home/samee/Downloads/synthetic1_nrois=10,50/int",
                            "/home/samee/Downloads/synthetic1_nrois=10,50/seg",
                            "/home/samee/axle/dev/nyxus_paper/nyxus/data", 
                            "/home/samee/axle/dev/nyxus_paper/nyxus/build_man/nyxus",
                            False)


    benchmark.run_benchmark_suit()