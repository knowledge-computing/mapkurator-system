import os 
import glob 
import time
import multiprocessing

sid_dir = '/data/rumsey-sid'
sid_to_jpg_dir = '/data2/rumsey_sid_to_jpg/'
num_process = 20
if_print_command  = True

sid_list = glob.glob(os.path.join(sid_dir, '*/*.sid'))

def execute_command(command, if_print_command):
    t1 = time.time()

    if if_print_command:
        print(command)
    os.system(command)

    t2 = time.time()
    time_usage = t2 - t1 
    return time_usage


def conversion(img_path):
    mrsiddecode_executable="/home/zekun/dr_maps/mapkurator-system/m1_geotiff/MrSID_DSDK-9.5.4.4709-rhel6.x86-64.gcc531/Raster_DSDK/bin/mrsiddecode"
    map_name = os.path.basename(img_path)[:-4]

    redirected_path = os.path.join(sid_to_jpg_dir, map_name + '.jpg')

    run_sid_to_jpg_command = mrsiddecode_executable + ' -quiet -i '+ img_path + ' -o '+redirected_path
    time_usage = execute_command(run_sid_to_jpg_command, if_print_command)



if __name__ == "__main__":
    pool = multiprocessing.Pool(num_process)
    start_time = time.perf_counter()
    processes = [pool.apply_async(conversion, args=(sid_path,)) for sid_path in sid_list]
    result = [p.get() for p in processes]
    finish_time = time.perf_counter()
    print(f"Program finished in {finish_time-start_time} seconds")
    
