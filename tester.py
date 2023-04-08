import random
import os
import statistics
import queue
import threading
import time

CHECKER_BINARY = "./checker"
PUSH_SWAP_BINARY = "./push_swap"
COMPUTE_SORT = 'ARG="{}"; ./push_swap $ARG'
CHECK_SORT = 'ARG="{}"; echo "{}" | ./checker $ARG'
CHECK_SPECIAL = 'ARG="{}"; ./push_swap $ARG | ./checker $ARG'
TEST_QUANTITY = 10_000
THREADS = 8

queue_5 = queue.Queue()
queue_100 = queue.Queue()
queue_500 = queue.Queue()

std_out_file = "std_out.txt"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def generate_random_list(size):
    """Generates a random list of integers between int_min and int_max"""
    int_min = -2_147_483_648
    int_max = 2_147_483_647
    return random.sample(range(int_min, int_max), size)


def test_for(args):
    compute_sort_cmd = COMPUTE_SORT.format(" ".join(map(str, args)))
    operations = os.popen(compute_sort_cmd).read().strip()
    if operations == "":
        check_ok_cmd = CHECK_SPECIAL.format(" ".join(map(str, args)))
        check_len = 0
    else:
        check_ok_cmd = CHECK_SORT.format(" ".join(map(str, args)), operations)
        check_len = len(operations.split("\n"))
    check_ok = os.popen(check_ok_cmd).read().strip()
    return check_ok, check_len


def worker(queue, ok_results, ko_results):
    while not queue.empty():
        args = queue.get()
        # print("Testing for args: {}".format(" ".join(map(str, args))))
        check_ok, length = test_for(args)
        if check_ok == "OK":
            ok_results.append((check_ok, length, " ".join(map(str, args))))
        else:
            ko_results.append((check_ok, length, " ".join(map(str, args))))
        queue.task_done()


def print_progress_bar(queue):
    while not queue.empty():
        print(
            "["
            + "#" * int((TEST_QUANTITY - queue.qsize()) / TEST_QUANTITY * 20)
            + " " * (20 - int((TEST_QUANTITY - queue.qsize()) / TEST_QUANTITY * 20))
            + "]"
            + " {}%".format(int((TEST_QUANTITY - queue.qsize()) / TEST_QUANTITY * 100)),
            end="\r",
        )
    # print in green the full progress bar
    print(f"{bcolors.OKGREEN} [####################] 100%{bcolors.ENDC}")


def launch_queue(queue):
    ok_results = list()
    ko_results = list()
    progress_thread = threading.Thread(target=print_progress_bar, args=(queue,))
    progress_thread.start()
    for _ in range(THREADS):
        thread = threading.Thread(target=worker, args=(queue, ok_results, ko_results))
        thread.start()
    queue.join()
    return ok_results, ko_results


def fill_queue(size, queue):
    for _ in range(TEST_QUANTITY):
        queue.put(generate_random_list(size))


def print_results(ok_results, ko_results):
    if len(ko_results) > 0:
        print(f"{bcolors.FAIL}KO for {len(ko_results)} random lists{bcolors.ENDC}")
    else:
        print(f"{bcolors.OKGREEN}OK for {TEST_QUANTITY} random lists{bcolors.ENDC}")
        min_len = min(map(lambda x: int(x[1]), ok_results))
        max_len = max(map(lambda x: int(x[1]), ok_results))
        median_len = int(statistics.median(map(lambda x: int(x[1]), ok_results)))
        print(f"{bcolors.OKGREEN}Min length: {min_len}{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Max length: {max_len}{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Median length: {median_len}{bcolors.ENDC}")


def test_5():
    first_5_args = [1, 5, 2, 4, 3]
    # print in green the name of the test
    print(f"{bcolors.HEADER} TEST 5 {bcolors.ENDC}")
    ok, length = test_for(first_5_args)
    if ok == "OK":
        print(
            f"{bcolors.OKGREEN}OK for {' '.join(map(str, first_5_args))}{bcolors.ENDC}"
        )
        print(f"{bcolors.OKGREEN}Length: {length}{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}KO for {' '.join(map(str, first_5_args))}{bcolors.ENDC}")
    fill_queue(5, queue_5)
    # print queue size
    print(f"{bcolors.OKCYAN} Testing with {TEST_QUANTITY} random args{bcolors.ENDC}")
    ok_results, ko_results = launch_queue(queue_5)
    print_results(ok_results, ko_results)


def test_100():
    print(f"{bcolors.HEADER} TEST 100 {bcolors.ENDC}")
    print(f"{bcolors.OKCYAN} Testing with {TEST_QUANTITY} random args{bcolors.ENDC}")
    fill_queue(100, queue_100)
    ok_results, ko_results = launch_queue(queue_100)
    print_results(ok_results, ko_results)


def test_500():
    print(f"{bcolors.HEADER} TEST 500 {bcolors.ENDC}")
    print(f"{bcolors.OKCYAN} Testing with {TEST_QUANTITY} random args{bcolors.ENDC}")
    fill_queue(500, queue_500)
    ok_results, ko_results = launch_queue(queue_500)
    print_results(ok_results, ko_results)


def main():
    now = time.time()
    # tester(3)
    # return
    test_5()
    test_100()
    test_500()
    print("Total time: {}s".format(time.time() - now))


if __name__ == "__main__":
    main()
