import glob
import itertools
import subprocess
import os
import sys


for cool_f in itertools.chain(glob.glob("tests/*.cl")):
    test_name = os.path.basename(cool_f)
    test_f = cool_f + "-type"
    output_f = cool_f[:-3] + ".s"
    correct_f = output_f + ".correct"
    #print(cool_f)
    #print(test_name)
    if os.path.exists(output_f):
        os.remove(output_f)
    if os.path.exists(correct_f):
        os.remove(correct_f)
    # subprocess.run(["../cool", "--lex", cool_f])
    subprocess.run(["../cool", "--type", cool_f])
    #correct_result = subprocess.run(["../cool", "--x86", cool_f], capture_output=True, text=True)

    # make sure we can actually build every program
    our_result = subprocess.run([sys.executable, "main.py", test_f], capture_output=True, text=True)
    file_created = os.path.isfile(output_f)

    if not file_created:
        print(f"FAIL: {test_name}")
        print(our_result.stdout)
        print(our_result.stderr)
        break
    
    print(f"PASS: {test_name}")
