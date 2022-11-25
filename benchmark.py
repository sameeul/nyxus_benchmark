import datetime
import os
import re
import shutil
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path, PurePath

class Benchmark:
    def __init__(self,  image_int_dir, 
                        image_seg_dir, 
                        work_dir,
                        nyxus_executable, 
                        feature_list = "*ALL*",
                        generate_missing_image=False) -> None:

        self._image_int_dir = Path(image_int_dir)
        self._image_seg_dir = Path(image_seg_dir)
        self._work_dir = Path(work_dir)
        self._nyxus_executable = Path(nyxus_executable)
        self._feature_list = feature_list
        self._generate_mising_image = generate_missing_image
        self._image_collection = {}
        self._processed_images = []
        self._result_dir = None
        self._merged_result_file = None
        self._num_sample = 3
        self.collect_image_pairs()

        if os.path.exists( PurePath(self._work_dir, Path("results"))):
            self._result_dir = PurePath(self._work_dir, Path("results"))
        else:
            try:
                os.mkdir(PurePath(self._work_dir, Path("results")))
                self._result_dir = PurePath(self._work_dir, Path("results"))
            except:
                print(f"Unable to create {self._work_dir}/results directory")
                exit()

    def create_nyxus_dirs(self, work_dir):
        try:
            os.mkdir(PurePath(self._work_dir, Path("int")))
        except FileExistsError :
            pass
        try:
            os.mkdir(PurePath(self._work_dir, Path("seg")))
        except FileExistsError :
            pass

        try:
            os.mkdir(PurePath(self._work_dir, Path("out")))
        except FileExistsError :
            pass


    def prepare_workdir(self, work_dir, seg_dir, int_dir, base_file_name):
        self.cleanup_workdir(work_dir)
        self.create_nyxus_dirs(work_dir)
        try:
            shutil.copyfile(PurePath(int_dir, Path(base_file_name)), PurePath(work_dir,Path("int"), Path(base_file_name)))
        except:
            pass

        try:
            shutil.copyfile(PurePath(seg_dir, Path(base_file_name)), PurePath(work_dir,Path("seg"),Path(base_file_name)))
        except:
            pass

    def collect_result(self, base_file_name, out_dir, result_dir, tag):
    
        dest_file_name = None
        if result_dir == None:
            pass
        base_file_name_wo_ext, tmp = os.path.splitext(base_file_name)
        abs_result_file_name = PurePath(out_dir, Path(f"{base_file_name_wo_ext}_nyxustiming.csv"))
        if(os.path.exists(abs_result_file_name)):
            try:
                dest_file_name = PurePath(result_dir, Path(f"{base_file_name_wo_ext}_nyxustiming.csv._{tag}"))
                shutil.copyfile(abs_result_file_name, dest_file_name)
            except:
                print(f"Result not generated for {base_file_name}")
        return dest_file_name
        
    def cleanup_workdir(self, work_dir):
        try:
            shutil.rmtree(PurePath(work_dir, Path("int")))
        except:
            pass
        try:
            shutil.rmtree(PurePath(work_dir, Path("seg")))
        except:
            pass

        # try:
        #     shutil.rmtree(PurePath(work_dir, Path("out")))
        # except:
        #     pass

    def run_nyxus(self, base_file_name, seg_dir, int_dir, out_dir, feature_list):
        print(f"Running nyxus for {base_file_name}")
        subprocess.run([
                        self._nyxus_executable, 
                        f"--features={feature_list}",
                        f"--segDir={seg_dir}",
                        f"--intDir={int_dir}",
                        f"--outDir={out_dir}",
                        "--csvFile=singlecsv",
                        "--verbosity=3"
                        ])

    def merge_benchmark_suit_results(self):
        input_csv_list = self._work_dir.glob("results/*.csv")
        timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        out_file_name = PurePath(self._work_dir, Path(f"merged_result_{timestamp}.csv")) 
        self.merge_csv_files(input_csv_list, out_file_name)
        self._merged_result_file = out_file_name
        

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



    def get_benchmark_data(self, roi_count, roi_area, feature_list):
        base_file_name = f"synthetic_nrois={roi_count}_roiarea={roi_area}.tif"
        seg_dir = PurePath(self._work_dir, Path("seg"))
        int_dir = PurePath(self._work_dir, Path("int"))
        out_dir = PurePath(self._work_dir, Path("out"))
        result_dir = self._result_dir

        if (roi_count, roi_area) in self._image_collection and \
            self._image_collection[(roi_count, roi_area)] == base_file_name :
                result_file_list = []
                for i in range(self._num_sample):
                    self.prepare_workdir(self._work_dir, self._image_seg_dir, self._image_int_dir, base_file_name)
                    self.run_nyxus(base_file_name, seg_dir, int_dir, out_dir, feature_list)
                    result_file = self.collect_result(base_file_name, out_dir, result_dir, "run_"+str(i))
                    if result_file != None:
                        result_file_list.append(result_file)
                    self.cleanup_workdir(self._work_dir)
                self.calculate_average(base_file_name, result_file_list, result_dir)
        else:
            print("weird stuff")

    def calculate_average(self, base_file_name, result_file_list, result_dir):
        dest_file_name = None
        if result_dir == None:
            pass
        base_file_name_wo_ext, tmp = os.path.splitext(base_file_name)
        primary_result_df = pd.read_csv(result_file_list[0])
        data_column_list = ["rawtime"]
        for count, result_file in enumerate(result_file_list[1:]):
            result_data = pd.read_csv(result_file)
            rawtime_col = result_data["rawtime"]
            col_title = "rawtime" + str(count)
            primary_result_df.insert(len(primary_result_df.columns), col_title, rawtime_col)
            data_column_list.append(col_title)
        primary_result_df["rawtime_avg"] = primary_result_df[data_column_list].mean(axis=1)
        
        dest_file_name = PurePath(result_dir, Path(f"{base_file_name_wo_ext}_nyxustiming.csv")) 
        primary_result_df.to_csv(dest_file_name)
        self._processed_images.append(base_file_name)

    def collect_image_pairs(self):
        #file_list = glob.glob(self._image_int_dir+"/*.tif")
        file_list = self._image_int_dir.glob("*.tif")
        for full_file_name in file_list:
            base_file_name = full_file_name.name
            roi_count, roi_size = re.findall("=(\d+)", base_file_name)
            self._image_collection[(int(roi_count), int(roi_size))] = base_file_name


    def run_benchmark_suit(self):
        for roi_param in self._image_collection:
            self.get_benchmark_data(roi_param[0], roi_param[1], self._feature_list)
        self.merge_benchmark_suit_results()

    def create_benchmark_plot(self, feature_l1, feature_l2, feature_l3, rerun_merge=False):
        if self._merged_result_file == None or rerun_merge:
            self.merge_benchmark_suit_results()

        df = pd.read_csv(self._merged_result_file)
        filtered_view = df[(df["h1"]==feature_l1) & (df["h2"]==feature_l2) & (df["h3"]==feature_l3)]
        roi_area_list = filtered_view["roiarea"].unique()

        for value in roi_area_list:
            tmp_df = filtered_view[filtered_view["roiarea"] == value].sort_values("nrois")
            plt.loglog(tmp_df.nrois, tmp_df.rawtime_avg, label=str(value), marker='o')

        plt.title(f"Timing Data for {feature_l1}, {feature_l2}, {feature_l3}")
        plt.xlabel("Number of ROIs")
        plt.ylabel("Time (s)")
        plt.legend()
        merged_result_file_wo_ext, dummy = os.path.splitext(self._merged_result_file)
        plot_file_name = f"{merged_result_file_wo_ext}_{feature_l1}_{feature_l2}_{feature_l3}.jpg"
        plt.savefig(plot_file_name)