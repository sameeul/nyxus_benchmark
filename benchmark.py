import datetime
import os
import glob
import re
import shutil
import subprocess

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
            os.mkdir(f"{self._work_dir}/results")
        except FileExistsError :
            pass


    def copy_files_to_workdir(self, base_file_name):
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
            shutil.copyfile(f"{self._image_int_dir}/{base_file_name}", f"{self._work_dir}/int/{base_file_name}")
        except:
            pass
        try:
            shutil.copyfile(f"{self._image_seg_dir}/{base_file_name}", f"{self._work_dir}/seg/{base_file_name}")
        except:
            pass

    def copy_results_from_workdir(self, base_file_name):
        base_file_name_wo_ext, tmp = os.path.splitext(base_file_name)
        abs_result_file_name = f"{self._work_dir}/out/{base_file_name_wo_ext}_nyxustiming.csv"
        print(abs_result_file_name)
        if(os.path.exists(abs_result_file_name)):
            try:
                dest_file_name = f"{self._work_dir}/results/{base_file_name_wo_ext}_nyxustiming.csv"
                shutil.copyfile(abs_result_file_name, dest_file_name)
                self._processed_images.append(base_file_name)
            except:
                print(f"Result not generated for {base_file_name}")
        

        pass

    def cleanup_workdir(self, base_file_name):
        try:
            shutil.rmtree(f"{self._work_dir}/int")
        except:
            pass
        try:
            shutil.rmtree(f"{self._work_dir}/seg")
        except:
            pass

        try:
            shutil.rmtree(f"{self._work_dir}/out")
        except:
            pass

    def run_nyxus(self, base_file_name):
        print(f"Running nyxus for {base_file_name}")
        subprocess.run([
                        self._nyxus_executable, 
                        "--features=*ALL*",
                        f"--segDir={self._work_dir}/seg",
                        f"--intDir={self._work_dir}/int",
                        f"--outDir={self._work_dir}/out",
                        "--csvFile=singlecsv",
                        "--verbosity=3"
                        ])

    def merge_benchmark_suit_results(self):
        input_csv_list = glob.glob(self._work_dir+"/results/*.csv")
        timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        out_file_name = f"{self._work_dir}/merged_result_{timestamp}.csv"
        self.merge_csv_files(input_csv_list, out_file_name)
        

    def merge_csv_files(self, input_csv_list, output_csv_name):
        with open(output_csv_name, "w") as ofp:
            first_csv = True
            for in_file_name in input_csv_list:
                with open(in_file_name, 'r') as ifp:
                    header_line = True
                    lines = ifp.readlines()
                    for line in lines:
                        if header_line and not first_csv:
                            pass
                        else:
                            ofp.write(line)
                        header_line = False
                first_csv = False



    def get_benchmark_data(self, roi_count, roi_area):
        base_file_name = f"synthetic_nrois={roi_count}_roiarea={roi_area}.tif"
        if (roi_count, roi_area) in self._image_collection and \
            self._image_collection[(roi_count, roi_area)] == base_file_name :
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


    def run_benchmark_suit(self):
        for roi_param in self._image_collection:
            self.get_benchmark_data(roi_param[0], roi_param[1])
        self.merge_benchmark_suit_results()