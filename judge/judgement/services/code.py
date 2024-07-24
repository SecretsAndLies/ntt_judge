import subprocess
from .test_runner import TestRunner


class Code:
    def __init__(self, code_text: str) -> None:
        self.code_text = code_text

    def compile(self):
        result = subprocess.run(
            [
                "java",
                "-jar",
                "judgement/AssemblerCommandLine-2.5-SNAPSHOT.jar",
                self.code_text,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            self.hack_code = result.stdout
            return True
        else:
            self.error_message = result.stderr
            return False

    def run_test(self, problem):
        test = TestRunner(hack_code=self.hack_code, problem=problem)
        test.run_test()
        return test
