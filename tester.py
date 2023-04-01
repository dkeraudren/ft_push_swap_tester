import random
import os
import statistics
import queue
import threading

CHECKER_BINARY = "./checker"
PUSH_SWAP_BINARY = "./push_swap"
CHECK_SORT = 'ARG="{}"; ./push_swap $ARG | ./checker $ARG'
CHECK_LEN = 'ARG="{}"; ./push_swap $ARG | wc -l'
TEST_QUANTITY = 1_000
THREADS = 8

queue_5 = queue.Queue()
queue_100 = queue.Queue()
queue_500 = queue.Queue()


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
    # print("Testing for args: {}".format(" ".join(map(str, args))))
    check_ok_cmd = CHECK_SORT.format(" ".join(map(str, args)))
    check_len_cmd = CHECK_LEN.format(" ".join(map(str, args)))
    check_ok = os.popen(check_ok_cmd).read().strip()
    check_len = os.popen(check_len_cmd).read().strip()
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


def tester(len_args):
    result = dict()
    failed = 0
    print("Testing push_swap with {} random lists".format(TEST_QUANTITY))
    for i in range(TEST_QUANTITY):
        args = generate_random_list(len_args)
        # print(" ".join(map(str, args)))
        # return
        cmd_check_sort = CHECK_SORT.format(" ".join(map(str, args)))
        cmd_len = CHECK_LEN.format(" ".join(map(str, args)))
        # print(cmd_len)
        check_sort = os.popen(cmd_check_sort).read()
        check_len = os.popen(cmd_len).read()
        result.setdefault(check_len.strip(), []).append(" ".join(map(str, args)))
        # print(result)
        # return
        if check_sort != "OK\n":
            print("KO for args: {}".format(" ".join(map(str, args))))
            failed += 1
        # print progress bar
        print(
            "["
            + "#" * int(i / TEST_QUANTITY * 20)
            + " " * (20 - int(i / TEST_QUANTITY * 20))
            + "]"
            + " {}%".format(int(i / TEST_QUANTITY * 100))
            + " {} / {}".format(i, TEST_QUANTITY),
            end="\r",
        )
    print("OK for {} nb of args".format(len_args))
    print(
        "Median number of operations: {}".format(
            statistics.median(map(int, result.keys()))
        )
    )
    print("Max number of operations: {}".format(max(map(int, result.keys()))))
    print("Min number of operations: {}".format(min(map(int, result.keys()))))
    print("Failed: {}".format(failed))
    print(
        "args with max operations: {}".format(result[str(max(map(int, result.keys())))])
    )
    # print(
    #     "args with min operations: {}".format(result[str(min(map(int, result.keys())))])
    # )


def main():
    test_5()
    test_100()
    test_500()
    # tester(5)
    # tester(100)
    # tester(500)


if __name__ == "__main__":
    main()
