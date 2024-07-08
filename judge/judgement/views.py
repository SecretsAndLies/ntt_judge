import random
from statistics import fmean
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from .models import Problem, Solution, Test
from scipy.stats import rankdata

from .forms import CodeForm
from time import sleep
import threading

import inflect

from math import floor


import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI rendering see https://stackoverflow.com/questions/69924881/userwarning-starting-a-matplotlib-gui-outside-of-the-main-thread-will-likely-fa
matplotlib.rcParams['font.family'] = 'sans-serif'
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.http import HttpResponse


class Code:
    def __init__(self, code_text:str) -> None:
        self.code_text = code_text

    def compile(self):
            # todo: this will spin up the assembler and report whatever it does.
            # it will populate the hack file, which will then be sent to the CPU emulator.
        if(self.code_text=="a"):
            self.hack_code = "TBD" # this is where your compiled 1001010 will go.
            return True
        else:
            self.error_message="Compilation error: Error on line whatever"
            return False
        
    def run_test(self, test_text):
        test = Test_Runner(hack_code=self.hack_code, test_code=test_text)
        test.run_test()
        return test

class Test_Runner:
    def __init__(self, hack_code, test_code) -> None:
        self.hack_code = hack_code
        self.test_code = test_code

    def run_test(self):
        # TODO: spin up a cpu emulator, and actually run the test
        # gathering the metrics. THIS IS WHERE THE MAGIC HAPPENS
        # if fail, populate info? expected reality? not sure.
        self.passed=True 
        self.rom = random.randint(1,1000)
        self.ram = random.randint(1,1000)
        self.cycles = random.randint(1,10000)


def generate_histogram(data, xlabel, number_to_highlight):
    # Create a histogram
    plt.figure()
    plt.style.use("dark_background")

    n, bins, patches = plt.hist(
        data, bins=10, linewidth=0.5,edgecolor='black',color="lightsteelblue"
        ) # https://medium.com/@arseniytyurin/how-to-make-your-histogram-shine-69e432be39ca
   
    for i in range(len(bins) - 1):
        if bins[i] <= number_to_highlight < bins[i + 1]:
            patches[i].set_fc('blue')
            break

    plt.xlabel(xlabel)
    plt.ylabel("Frequency")

    # Save the histogram to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the image in base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Render the image in the template
    return image_base64

def index(request):
    # todo: sort problems by requested, filter problems
    return render(request,"judgement/problems.html", 
                  {"problems":Problem.objects.all().order_by("rating")})

def problem(request, problem_id):
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = Code(code_text=form.cleaned_data["code"])

            if(code.compile()):
                return solution(request, problem_id, code)
            else:
                messages.error(request, code.error_message)
                render(request, 
                       "judgement/problem.html", 
                       {"form": form,"problem":Problem.objects.get(id=problem_id)})
    else:
        form = CodeForm()

    return render(request, "judgement/problem.html", {"form": form,"problem":Problem.objects.get(id=problem_id)})

def calculate_percentile(rank:int, total:int)->float:
    return (1 - (rank - 1) / total) * 100

def run_test_and_collect_results(test, roms, rams, cycles, code:Code, tests_passed, lock):
    test_result = code.run_test(test.test_file_text)
    if test_result.passed:
        with lock:
            tests_passed[0] += 1
        roms.append(test_result.rom)
        rams.append(test_result.ram)
        cycles.append(test_result.cycles)

def failed(request, tests_passed, total_tests):
    context = {
        'tests_passed': tests_passed[0],
        'tests_total': total_tests,
    }
    return render(request,"judgement/failed.html", context)


def solution(request, problem_id: int, code:Code):  
    problem = Problem.objects.get(id=problem_id)
    # Tests Stuff
    tests = Test.objects.filter(problem=problem)
    tests_passed = [0] # this is a list so I can pass it by reference.
    roms = []
    rams = []
    cycles = []
    threads = []
    lock = threading.Lock()
    # kick off a new thread for each CPU Emulator test.
    for test in tests:
        thread = threading.Thread(
            target=run_test_and_collect_results, 
            args=(test, roms, rams, cycles, code, tests_passed, lock))
        threads.append(thread)
        thread.start()

    # wait till all the threads are done before continuing.
    for thread in threads:
        thread.join()


    total_tests = tests.count()
    # if not all tests passed, return the failure page.
    if(tests_passed[0]<total_tests):
        return failed(request=request, 
                      tests_passed=tests_passed, 
                      total_tests=total_tests)
    # Otherwise, calculate and return the sucess metrics.

    rom = fmean(roms)
    ram = fmean(rams)
    cycles = fmean(cycles)

    user_solution = Solution(problem=problem,cycles=cycles,rom=rom,ram=ram)
    user_solution.save()

    solutions = Solution.objects.filter(problem=problem)

    rom_values = [solution.rom for solution in solutions]
    ram_values = [solution.ram for solution in solutions]
    cycles_values = [solution.cycles for solution in solutions]

    # todo: ideally if there were a tie, we'd use the first one. You'll need a fancier sort I think.
    rom_ranks = rankdata(rom_values, method='min')
    ram_ranks = rankdata(ram_values, method='min')
    cycles_ranks = rankdata(cycles_values, method='min')

    user_rom_rank = rom_ranks[-1]
    user_ram_rank = ram_ranks[-1]
    user_cycles_rank = cycles_ranks[-1]

    total_solutions = len(solutions)

    user_rom_percentile = calculate_percentile(user_rom_rank, total_solutions)
    user_ram_percentile = calculate_percentile(user_ram_rank, total_solutions)
    user_cycles_percentile = calculate_percentile(user_cycles_rank, total_solutions)

    # Prettier number formats. Used to change 1 into 1st, and 99 into 99th etc.
    p = inflect.engine() 

    cycle_data = solutions.values_list("cycles", flat=True)
    cycle_hist = generate_histogram(cycle_data,"Average Cycles used",cycles)
    rom_data = solutions.values_list("rom", flat=True)
    rom_hist = generate_histogram(rom_data,"Average ROM used", rom)
    ram_data = solutions.values_list("ram", flat=True)
    ram_hist = generate_histogram(ram_data,"Average RAM used", ram)


    # (percentiles, ranks, histogram)
    context = {
        'problem': problem,
        'solutions': solutions,
        'user_solution': user_solution,
        'rom_rank': user_rom_rank,
        'cycle_rank': user_cycles_rank,
        'ram_rank': user_ram_rank,
        'out_of_rank': total_solutions,
        'ram_percentile': p.ordinal(round(user_ram_percentile)),
        'rom_percentile': p.ordinal(round(user_rom_percentile)),
        'cycle_percentile': p.ordinal(round(user_cycles_percentile)),
        'tests_passed': tests_passed[0],
        'tests_total': total_tests,
        'rom_hist' : rom_hist,
        'ram_hist' : ram_hist,
        'cycle_hist' : cycle_hist,
    }

    return render(request,"judgement/solved.html", context)

def getBucket(percentile):
    return 9 - floor(percentile/10)