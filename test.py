import glob
import itertools
import subprocess
import os
import sys


for cool_f in itertools.chain(glob.glob("tests/*.cl")):
    test_name = os.path.basename(cool_f)
    test_f = cool_f + "-type"
    input_file = cool_f[:-3] + ".txt"
    asm_file = cool_f[:-3] + ".s"
    output_f = cool_f[:-3] + ".OUTPUT"
    correct_f = output_f + ".correct"

    if os.path.exists(output_f):
        os.remove(output_f)
    if os.path.exists(correct_f):
        os.remove(correct_f)

    subprocess.run(["../cool", "--type", cool_f])
    #input_args = f"<{input_file}" if os.path.isfile(input_file) else ""
    if os.path.exists(input_file):
        correct_result = subprocess.run(f"../cool {cool_f} <{input_file} >{output_f}", shell=True, capture_output=True, text=True)
    else:
        correct_result = subprocess.run(f"../cool {cool_f} >{output_f}", shell=True, capture_output=True, text=True)

    file_created = os.path.isfile(output_f)
    if file_created:
        with open(output_f) as f:
            correct_answer = f.read().strip()
        os.replace(output_f, correct_f)

    subprocess.run(f"python3 main.py {test_f}", shell=True, capture_output=True, text=True)
    
    subprocess.run(f"gcc {asm_file}", shell=True)
    if os.path.exists(input_file):
        our_result = subprocess.run(f"./a.out <{input_file} >{output_f}", shell=True, capture_output=True, text=True)
    else:
        our_result = subprocess.run(f"./a.out >{output_f}", shell=True, capture_output=True, text=True)

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

    def clean(answer):
        lines = answer.splitlines()
        out_lines = []
        skip = False
        for i, line in enumerate(lines):
            if skip:
                skip = False
                continue
            if "## stack room for temporaries" in line:
                skip = True
                continue
            if "## self" in line:
                continue
            if "## obtain vtable for self object of type" in line:
                continue
            out_lines.append(line)
        return "\n".join(out_lines)

    our_answer = clean(our_answer)
    correct_answer = clean(correct_answer)
    if our_answer != correct_answer:
        print("FAIL:", test_name)
        subprocess.run(["icdiff", output_f, correct_f])
        break
    else:
        print("PASS:", test_name)
