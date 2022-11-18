import os
import glob
import re
import shutil
import subprocess
from unittest import result

class Benchmark:
    def __init__(self,  image_int_dir, 
                        image_seg_dir, 
                        work_dir,
                        nyxus_executable, 
                        generate_missing_image=False) -> None:
        self._image_int_dir = image_int_dir
        self._image_seg_dir = image_seg_dir
        self._work_dir = work_dir
        self._nyxus_executable = nyxus_executable
        self._generate_mising_image = generate_missing_image
        self._image_collection = {}
        self._processed_images = []
        self.collect_image_pairs()
        try:
            os.mkdir(f"{self._work_dir}/int")
        except FileExistsError :
            pass
        try:
            os.mkdir(f"{self._work_dir}/seg")
        except FileExistsError :
            pass

        try:
            os.mkdir(f"{self._work_dir}/out")
        except FileExistsError :
            pass

        try:
            os.mkdir(f"{self._work_dir}/results")
        except FileExistsError :
            pass


    def copy_files_to_workdir(self, base_file_name):
        try:
            shutil.copyfile(f"{self._image_int_dir}/{base_file_name}", f"{self._work_dir}/int/{base_file_name}")
        except:
            pass
        try:
            shutil.copyfile(f"{self._image_seg_dir}/{base_file_name}", f"{self._work_dir}/seg/{base_file_name}")
        except:
            pass

    def copy_results_from_workdir(self, base_file_name):
        abs_result_file_name = f"{self._work_dir}/out/{base_file_name}_nyxustiming.csv"
        if(os.path.exists(abs_result_file_name)):
            try:
                dest_file_name = f"{self._work_dir}/results/{base_file_name}_nyxustiming.csv"
                shutil.copyfile(abs_result_file_name, dest_file_name)
                self._processed_images.append(base_file_name)
            except:
                print(f"Result not generated for {base_file_name}")
        

        pass

    def cleanup_workdir(self, base_file_name):
        pass

    def run_nyxus(self, base_file_name):
       
        cmd_args = f"--features=*ALL* --segDir={self._work_dir}/seg --intDir={self._work_dir}/int" + \
                f" --outDir={self._work_dir}/out  --csvFile=singlecsv --verbosity=3"
        print(self._nyxus_executable)
        print(cmd_args)
        subprocess.run([
                        self._nyxus_executable, 
                        "--features=*ALL*",
                        f"--segDir={self._work_dir}/seg",
                        f"--intDir={self._work_dir}/int",
                        f"--outDir={self._work_dir}/out",
                        "--csvFile=singlecsv",
                        "--verbosity=3"
                        ])

    def merge_results(self):
        pass

    def get_benchmark_data(self, roi_count, roi_area):
        base_file_name = f"synthetic_nrois={roi_count}_roiarea={roi_area}.tif"
        if (roi_count, roi_area) in self._image_collection and \
            self._image_collection[(roi_count, roi_area)] == base_file_name :
                print(base_file_name)
                self.copy_files_to_workdir(base_file_name)
                self.run_nyxus(base_file_name)
                self.copy_results_from_workdir(base_file_name)
                self.cleanup_workdir(base_file_name)


    def collect_image_pairs(self):
        file_list = glob.glob(self._image_int_dir+"/*.tif")
        for full_file_name in file_list:
            base_file_name = os.path.basename(full_file_name)
            roi_count, roi_size = re.findall("=(\d+)", base_file_name)
            self._image_collection[(int(roi_count), int(roi_size))] = base_file_name



if __name__ == '__main__':
    print("hello")
    benchmark = Benchmark("/home/samee/Downloads/synthetic1_nrois=10,50/int",
                            "/home/samee/Downloads/synthetic1_nrois=10,50/seg",
                            "/home/samee/axle/dev/nyxus_paper/nyxus/data", 
                            "/home/samee/axle/dev/nyxus_paper/nyxus/build_man/nyxus",
                            False)
    benchmark.collect_image_pairs()
    benchmark.get_benchmark_data(10,500)
    benchmark.get_benchmark_data(10,10)