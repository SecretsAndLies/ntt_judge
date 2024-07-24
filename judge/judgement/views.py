from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from .services.code import Code
from .models import Problem, Solution
from scipy.stats import rankdata
import pandas as pd

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
    # todo: sort problems by requested, filter problems
    return render(
        request,
        "judgement/problems.html",
        {"problems": Problem.objects.all().order_by("rating")},
    )


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
        {"form": form, "problem": Problem.objects.get(id=problem_id)},
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


def solution(request, problem_id: int, code: Code):
    problem = Problem.objects.get(id=problem_id)
    roms = []
    rams = []
    cycles = []
    messages = []
    tests_passed = [0]
    out_str = []

    run_test_and_collect_results(
        problem, roms, rams, cycles, code, tests_passed, messages, out_str
    )
    if tests_passed[0] != 1:
        context = {
            "tst": problem.tst_file_text,
            "cmp": pd.read_csv(io.StringIO(problem.cmp_file_text)).to_html(
                index=False, classes=["table", "table-striped"], justify="match-parent"
            ),
            "message": messages[0],
            "students_out": pd.read_csv(io.StringIO(out_str[0])).to_html(
                index=False, classes=["table", "table-striped"], justify="match-parent"
            ),
        }
        return render(request, "judgement/failed.html", context)

    rom = roms[0]
    ram = rams[0]
    cycles = cycles[0]

    user_solution = Solution(problem=problem, cycles=cycles, rom=rom, ram=ram)
    user_solution.save()

    solutions = Solution.objects.filter(problem=problem)

    rom_values = [solution.rom for solution in solutions]
    ram_values = [solution.ram for solution in solutions]
    cycles_values = [solution.cycles for solution in solutions]

    # todo: ideally if there were a tie, we'd use the first one. You'll need a fancier sort I think.
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

    # Prettier number formats. Used to change 1 into 1st, and 99 into 99th etc.
    p = inflect.engine()

    cycle_data = solutions.values_list("cycles", flat=True)
    cycle_hist = generate_histogram(cycle_data, "Average Cycles used", cycles)
    rom_data = solutions.values_list("rom", flat=True)
    rom_hist = generate_histogram(rom_data, "Average ROM used", rom)
    ram_data = solutions.values_list("ram", flat=True)
    ram_hist = generate_histogram(ram_data, "Average RAM used", ram)

    # TODO: Add the message from the CPU emulator to the output.

    # (percentiles, ranks, histogram)
    context = {
        "problem": problem,
        "solutions": solutions,
        "user_solution": user_solution,
        "rom_rank": user_rom_rank,
        "cycle_rank": user_cycles_rank,
        "ram_rank": user_ram_rank,
        "out_of_rank": total_solutions,
        "ram_percentile": p.ordinal(round(user_ram_percentile)),
        "rom_percentile": p.ordinal(round(user_rom_percentile)),
        "cycle_percentile": p.ordinal(round(user_cycles_percentile)),
        "rom_hist": rom_hist,
        "ram_hist": ram_hist,
        "cycle_hist": cycle_hist,
    }

    return render(request, "judgement/solved.html", context)
