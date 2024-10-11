import tempfile
import os
import shutil
import json
import subprocess
import pandas as pd


class TestRunner:
    def __init__(self, hack_code, problem) -> None:
        self.hack_code = hack_code
        self.tst_file_text = problem.tst_file_text
        self.cmp_file_text = problem.cmp_file_text
        self.timeout_cycles = problem.timeout_cycles

    def run_test(self):
        tempdir = tempfile.mkdtemp()
        try:
            asm_file_path = os.path.join(tempdir, "assembly.hack")
            cmp_file_path = os.path.join(tempdir, "compare.cmp")
            tst_file_path = os.path.join(tempdir, "test.tst")
            out_file_path = os.path.join(tempdir, "assembly.out")

            with open(asm_file_path, "w") as asm_file:
                asm_file.write(self.hack_code)

            with open(cmp_file_path, "w") as cmp_file:
                cmp_file.write(self.cmp_file_text)

            with open(tst_file_path, "w") as tst_file:
                tst_file.write(self.tst_file_text)

            result = subprocess.CompletedProcess(args=[], returncode=None)
            try:
                result = subprocess.run(
                    [
                        "java",
                        "-jar",
                        "judgement/static/judgement/CPUEmulator-2.5-SNAPSHOT.jar",
                        tst_file.name,
                        str(self.timeout_cycles),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
            except subprocess.TimeoutExpired:
                result.stderr = "Timeout, ran code for 30 seconds."
                result.returncode = 1

            try:
                with open(out_file_path, "r") as out_file:
                    self.out_file_string = out_file.read()
            except FileNotFoundError:
                self.out_file_string = None

        finally:
            shutil.rmtree(tempdir)

        self.passed = result.returncode == 0
        self.message = result.stderr

        if self.passed:
            self.message = result.stdout.splitlines()[0]
            stats = json.loads(result.stdout.splitlines()[1])
            self.rom = len(self.hack_code.splitlines())
            self.ram = stats["ram_used"]
            self.cycles = stats["cycles_used"]
