from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from .services.code import Code
from .models import Problem, Solution
from scipy.stats import rankdata
import pandas as pd
import numpy as np

from .forms import CodeForm

import inflect


import matplotlib

matplotlib.use(
    "Agg"
)  # Use the Agg backend for non-GUI rendering see https://stackoverflow.com/questions/69924881/userwarning-starting-a-matplotlib-gui-outside-of-the-main-thread-will-likely-fa
matplotlib.rcParams["font.family"] = "sans-serif"
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render


def generate_histogram(data, xlabel, number_to_highlight):
    # Create a histogram
    plt.figure()
    plt.style.use("dark_background")

    n, bins, patches = plt.hist(
        data, bins=10, linewidth=0.5, edgecolor="black", color="lightsteelblue"
    )  # https://medium.com/@arseniytyurin/how-to-make-your-histogram-shine-69e432be39ca

    # highlight the bucket where the number is.
    for i in range(len(bins) - 1):
        if number_to_highlight >= bins[i] and number_to_highlight <= bins[i + 1]:
            patches[i].set_fc("blue")
            break

    plt.xlabel(xlabel)
    plt.ylabel("Frequency")

    # Save the histogram to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Encode the image in base64
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    # Render the image in the template
    return image_base64


def index(request):
    # TODO: sort problems by requested, filter problems
    context = {
        "problems": Problem.objects.all().order_by("rating"),
        "current_page": "index",
    }
    return render(request, "judgement/problems.html", context)


@csrf_protect
def problem(request, problem_id):
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = Code(code_text=form.cleaned_data["code"])

            if code.compile():
                return solution(request, problem_id, code)
            else:
                messages.error(request, code.error_message)
                render(
                    request,
                    "judgement/problem.html",
                    {"form": form, "problem": Problem.objects.get(id=problem_id)},
                )
    else:
        form = CodeForm()

    return render(
        request,
        "judgement/problem.html",
        {
            "form": form,
            "problem": Problem.objects.get(id=problem_id),
            "current_page": "index",
        },
    )


def calculate_percentile(rank: int, total: int) -> float:
    return (1 - (rank / total)) * 100


def run_test_and_collect_results(
    problem, roms, rams, cycles, code: Code, tests_passed, messages, out_str
):
    test_result = code.run_test(problem)
    messages.append(test_result.message)
    out_str.append(test_result.out_file_string)
    if test_result.passed:
        tests_passed[0] = 1
        roms.append(test_result.rom)
        rams.append(test_result.ram)
        cycles.append(test_result.cycles)


def resources(request):
    return render(request, "judgement/resources.html", {"current_page": "resources"})


def fetch_problem(problem_id: int):
    return Problem.objects.get(id=problem_id)


def initialize_variables():
    return [], [], [], [], [0], []


def run_tests(problem, code, roms, rams, cycles, tests_passed, messages, out_str):
    run_test_and_collect_results(
        problem, roms, rams, cycles, code, tests_passed, messages, out_str
    )


def int_to_16bit_binary(number):
    return format(number & 0xFFFF, "016b")


def convert_array_to_bin_arr(numbers):
    binary_strings = []
    for number in numbers:
        binary_value = number & 0xFFFF
        binary_string = f"{binary_value:016b}"
        binary_strings.append(binary_string)

    binary_output = "".join(binary_strings)

    binary_array = np.array([int(bit) for bit in binary_output])
    binary_array = (
        1 - binary_array
    )  # Invert the binary array so the colours show up right.
    image_array = binary_array.reshape((256, 512))
    return image_array


def visualise_binary(numbers):
    buf = io.BytesIO()
    image_array = convert_array_to_bin_arr(numbers)
    plt.imshow(image_array, cmap="gray", vmin=0, vmax=1)
    plt.axis("off")
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return image


def visualise_binary_difference(array1, array2):
    buf = io.BytesIO()

    array1 = convert_array_to_bin_arr(array1)
    array2 = convert_array_to_bin_arr(array2)

    difference_array = array1 - array2

    image_array = np.zeros((array1.shape[0], array1.shape[1], 3))

    image_array[difference_array == 1] = [0, 0.8, 0.8]  # cyan
    image_array[difference_array == -1] = [0.8, 0, 0.8]  # purple

    # otherwise it should be regular black and white image.
    for i in range(array1.shape[0]):
        for j in range(array1.shape[1]):
            if difference_array[i, j] == 0:
                if array1[i, j] == 1:
                    image_array[i, j] = [1, 1, 1]
                else:
                    image_array[i, j] = [0, 0, 0]

    plt.imshow(image_array)
    plt.axis("off")
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return image


def handle_test_failure(problem, messages, out_str):
    # get the index of the last line of data from the outfile.
    # add an if , only do for screen problems RAM[16384]
    cmp_file_pd = pd.read_csv(io.StringIO(problem.cmp_file_text))
    out_file_pd = pd.read_csv(io.StringIO(out_str[0]))
    expected_image = None
    actual_image = None
    diff = None
    screen_problem = False
    # if cmp file contains a screen location then visualise it
    if "RAM[16384]" in cmp_file_pd:
        screen_problem = True
        last_out_row = len(out_file_pd.index) - 1
        out_first_row = out_file_pd.iloc[last_out_row].to_numpy().flatten()
        cmp_first_row = cmp_file_pd.iloc[last_out_row].to_numpy().flatten()

        outArr = np.array(out_first_row)
        cmpArr = np.array(cmp_first_row)
        expected_image = visualise_binary(cmpArr)
        actual_image = visualise_binary(outArr)
        diff = visualise_binary_difference(cmpArr, outArr)
    context = {
        "tst": problem.tst_file_text,
        "cmp": cmp_file_pd.to_html(
            index=False, classes=["table", "table-striped"], justify="match-parent"
        ),
        "message": messages[0],
        "students_out": out_file_pd.to_html(
            index=False, classes=["table", "table-striped"], justify="match-parent"
        ),
        "screen_problem": screen_problem,
        "expected_image": expected_image,
        "actual_image": actual_image,
        "diff_image": diff,
        "current_page": "index",
    }
    return context


def save_user_solution(problem, rom, ram, cycles):
    user_solution = Solution(problem=problem, cycles=cycles, rom=rom, ram=ram)
    user_solution.save()
    return user_solution


def compute_ranks_and_percentiles(solutions, user_solution):
    rom_values = [solution.rom for solution in solutions]
    ram_values = [solution.ram for solution in solutions]
    cycles_values = [solution.cycles for solution in solutions]

    rom_ranks = rankdata(rom_values, method="min")
    ram_ranks = rankdata(ram_values, method="min")
    cycles_ranks = rankdata(cycles_values, method="min")

    user_rom_rank = rom_ranks[-1]
    user_ram_rank = ram_ranks[-1]
    user_cycles_rank = cycles_ranks[-1]

    total_solutions = len(solutions)

    user_rom_percentile = calculate_percentile(user_rom_rank, total_solutions)
    user_ram_percentile = calculate_percentile(user_ram_rank, total_solutions)
    user_cycles_percentile = calculate_percentile(user_cycles_rank, total_solutions)

    return {
        "rom_rank": user_rom_rank,
        "ram_rank": user_ram_rank,
        "cycles_rank": user_cycles_rank,
        "rom_percentile": user_rom_percentile,
        "ram_percentile": user_ram_percentile,
        "cycles_percentile": user_cycles_percentile,
        "total_solutions": total_solutions,
    }


def generate_histograms(solutions, user_solution):
    cycle_data = solutions.values_list("cycles", flat=True)
    cycle_hist = generate_histogram(
        cycle_data, "Average Cycles used", user_solution.cycles
    )
    rom_data = solutions.values_list("rom", flat=True)
    rom_hist = generate_histogram(rom_data, "Average ROM used", user_solution.rom)
    ram_data = solutions.values_list("ram", flat=True)
    ram_hist = generate_histogram(ram_data, "Average RAM used", user_solution.ram)
    return cycle_hist, rom_hist, ram_hist


def render_failed_template(request, context):
    return render(request, "judgement/failed.html", context)


def render_solved_template(request, context):
    return render(request, "judgement/solved.html", context)


def solution(request, problem_id: int, code: Code):
    problem = fetch_problem(problem_id)
    roms, rams, cycles, messages, tests_passed, out_str = initialize_variables()

    run_tests(problem, code, roms, rams, cycles, tests_passed, messages, out_str)

    if tests_passed[0] != 1:
        context = handle_test_failure(problem, messages, out_str)
        return render_failed_template(request, context)

    user_solution = save_user_solution(problem, roms[0], rams[0], cycles[0])
    solutions = Solution.objects.filter(problem=problem)

    ranks_and_percentiles = compute_ranks_and_percentiles(solutions, user_solution)

    p = inflect.engine()

    cycle_hist, rom_hist, ram_hist = generate_histograms(solutions, user_solution)

    context = {
        "problem": problem,
        "solutions": solutions,
        "user_solution": user_solution,
        "rom_rank": ranks_and_percentiles["rom_rank"],
        "cycle_rank": ranks_and_percentiles["cycles_rank"],
        "ram_rank": ranks_and_percentiles["ram_rank"],
        "out_of_rank": ranks_and_percentiles["total_solutions"],
        "ram_percentile": p.ordinal(round(ranks_and_percentiles["ram_percentile"])),
        "rom_percentile": p.ordinal(round(ranks_and_percentiles["rom_percentile"])),
        "cycle_percentile": p.ordinal(
            round(ranks_and_percentiles["cycles_percentile"])
        ),
        "rom_hist": rom_hist,
        "ram_hist": ram_hist,
        "cycle_hist": cycle_hist,
        "current_page": "index",
    }

    return render_solved_template(request, context)
