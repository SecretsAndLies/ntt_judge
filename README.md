This is a web-based version of the Nand2Tetris CPU Emulator. It is a Django application that allows instructors to create problems along with associated test scripts. These test scripts are automatically executed when a student submits a solution, using a modified version of the CPUEmulator Java application, which is run through a Python subprocess. The application is currently deployed at codestuff.online.

The judge/judgement directory contains the application code. The most important file is views.py, which controls routing and some general code. The other two important classes are services/code.py and test_runner.py, which are responsible for executing test cases, compiling results, and visualising statistics. Bootstrap is used for styling. The application has two models: problems, which contain instructor-defined problems, and solutions, which hold statistics about student submissions to those problems. HTML templates are located in the templates folder.

The contents of this repository are subject to the GNU General Public License (GPL) Version 2 or later (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at http://www.gnu.org/copyleft/gpl.html

Software distributed under the License is distributed on an "AS IS" basis, without warranty of any kind, either expressed or implied. See the License
for the specific language governing rights and limitations under the License.
