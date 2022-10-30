import glob
import itertools
import subprocess
import os
import sys


for cool_f in itertools.chain(glob.glob("tests/*.cl")):
    test_name = os.path.basename(cool_f)
    # test_f = cool_f + "-lex"
    output_f = cool_f + "-type"
    correct_f = output_f + ".correct"

    if os.path.exists(output_f):
        os.remove(output_f)
    if os.path.exists(correct_f):
        os.remove(correct_f)

    # subprocess.run(["../cool", "--lex", cool_f])
    correct_result = subprocess.run(["../cool", "--type", cool_f], capture_output=True, text=True)

    file_created = os.path.isfile(output_f)
    if file_created:
        with open(output_f) as f:
            correct_answer = f.read().strip()
        os.replace(output_f, correct_f)

    our_result = subprocess.run([sys.executable, "deserialize_ast.py", correct_f], capture_output=True, text=True)
    if our_result.stdout != correct_result.stdout or our_result.stderr != correct_result.stderr:
        print("FAIL:", test_name)
        with open("tests/our.stdout", "w") as f:
            f.write(our_result.stdout)
        with open("tests/our.stderr", "w") as f:
            f.write(our_result.stderr)
        with open("tests/correct.stdout", "w") as f:
            f.write(correct_result.stdout)
        with open("tests/correct.stderr", "w") as f:
            f.write(correct_result.stderr)

        print("Stdout:")
        subprocess.run(["icdiff", "tests/our.stdout", "tests/correct.stdout"])
        print("Stderr:")
        subprocess.run(["icdiff", "tests/our.stderr", "tests/correct.stderr"])
        os.remove("tests/our.stdout")
        os.remove("tests/our.stderr")
        os.remove("tests/correct.stdout")
        os.remove("tests/correct.stderr")
        break

    if not file_created:
        if os.path.isfile(output_f):
            os.remove(output_f)
            print("FAIL:", test_name)
            print(f"Output file: {output_f} should not have been created")
            break
        # If the file wasn't created, there's nothing else to check
        print("PASS:", test_name)
        continue

    if not os.path.isfile(output_f):
        print("FAIL:", test_name)
        print(f"Output file: {output_f} was not created")
        break

    with open(output_f) as f:
        our_answer = f.read().strip()

    if our_answer != correct_answer:
        print("FAIL:", test_name)
        subprocess.run(["icdiff", output_f, correct_f])
        break
    else:
        print("PASS:", test_name)
