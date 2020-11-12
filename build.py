import json
import os
import subprocess
import sys

BUILD_DIR = "./build/"
PROJ_SRC_DIR = [
    "./Core/Src/",
    "./Src/"
]
DRV_SRC_DIR = "./Driver/Src/"
DRV_SRCS = [
    # Sources that are applicable to all models
    # Comment/Delete the peripherals that are not used to reduce code size
    "stm8s_awu.c", "stm8s_beep.c", "stm8s_clk.c", "stm8s_exti.c", "stm8s_flash.c",
    "stm8s_gpio.c", "stm8s_i2c.c", "stm8s_itc.c", "stm8s_iwdg.c", "stm8s_rst.c", 
    "stm8s_spi.c", "stm8s_tim1.c", "stm8s_wwdg.c"
]
MODEL_DIC = {
    # Sources that are only applicable to selective models
    # Comment/Delete the peripherals that are not used to reduce code size
    "stm8s_adc1.c" : 
        ["STM8S105", "STM8S005", "STM8S103", "STM8S003", "STM8S001", 
        "STM8S903", "STM8AF626x", "STM8AF622x"],
    "stm8s_adc2.c" :
        ["STM8S208", "STM8S207", "STM8S007", "STM8AF52Ax", "STM8AF62Ax"],
    "stm8s_can.c" :
        ["STM8S208", "STM8AF52Ax"],
    "stm8s_tim2.c" :
        ["STM8S103", "STM8S903", "STM8AF622x"],
    "stm8s_tim3.c" :
        ["STM8S208", "STM8S207", "STM8S007", "STM8S105", "STM8S005", 
        "STM8AF52Ax", "STM8AF62Ax", "STM8AF626x"],
    "stm8s_tim4.c" :
        ["STM8S903", "STM8AF622x"],
    "stm8s_tim5.c" :
        ["STM8S903", "STM8AF622x"],
    "stm8s_tim6.c" :
        ["STM8S903", "STM8AF622x"],
    "stm8s_uart1.c" :
        ["STM8S208", "STM8S207", "STM8S007", "STM8S103", "STM8S003", 
        "STM8S001", "STM8S903", "STM8AF52Ax", "STM8AF62Ax"],
    "stm8s_uart2.c" :
        ["STM8S105", "STM8S005", "STM8AF626x"],
    "stm8s_uart3.c" :
        ["STM8S208", "STM8S207", "STM8S007", "STM8AF52Ax", "STM8AF62Ax"],
    "stm8s_uart4.c" :
        ["STM8AF622x"]
}
MODELS = {
    'STM8AF62Ax', 'STM8S903', 'STM8S007', 'STM8S003', 'STM8S208', 
    'STM8S005', 'STM8S103', 'STM8S001', 'STM8S105', 'STM8S207', 
    'STM8AF626x', 'STM8AF52Ax', 'STM8AF622x'
}

with open("./.vscode/c_cpp_properties.json") as confFile:
    confs = json.load(confFile)['configurations']

# Read compiler parameters from VS Code config
for c in confs:
    if c['name'] == "SDCC":
        cInc = c['includePath']
        cDef = c['defines']
        cc = c['compilerPath']
        cStd = c['cStandard']
        cOpt = c['compilerArgs']
        break
del confs

# Remove macros used for VS Code syntax checking
for i in range(len(cDef)):
    if cDef[i].startswith("__SDCC"): break
cDef = cDef[:i]

# Replace VS Code constants in includes and remove compiler includes
cInc = [i.replace("${workspaceFolder}", ".") for i in cInc if not i.endswith("sdcc/include")]

# Detect chip model from definitions
chip = [d for d in cDef if d in MODELS]
if len(chip) != 1:
    print("Cannot detect chip model. Quitting.")
    exit()
chip = chip[0]

if not os.path.exists(BUILD_DIR): 
    os.makedirs(BUILD_DIR)
else:
    subprocess.run(["ls", BUILD_DIR], cwd=".")

# Compile object files
cmd = [cc] + cOpt + ["-D"+d for d in cDef] + ["-I"+i for i in cInc]
objList = []

for srcDir in PROJ_SRC_DIR + [DRV_SRC_DIR]:
    objDir = BUILD_DIR + srcDir
    if not os.path.exists(objDir): os.makedirs(objDir)
    for src in os.listdir(srcDir):
        if srcDir == DRV_SRC_DIR:
            if src in MODEL_DIC.keys():
                if chip not in MODEL_DIC[src]: continue
            elif src not in DRV_SRCS: continue
        objList.append(objDir + src + ".rel")
        if "-v" in sys.argv: print("Building %s ..." % (srcDir + src))
        res = subprocess.run(cmd + 
            ["-c", srcDir + src, "-o", objDir + src + ".rel"], capture_output=True)
        print(res.stdout.decode("utf-8"), end='')

# Linking object files
outFile = "main.ihx"
if "-v" in sys.argv: print("Linking %s ..." % outFile)
subprocess.run(cmd + objList + ["-o", BUILD_DIR + outFile])
subprocess.run(cmd + objList + ["-o", BUILD_DIR + outFile[0:-4] + ".elf", "--out-fmt-elf"])

# Optionally use srec_cat to get binary form
subprocess.run(["srec_cat", "-disable-sequence-warning", BUILD_DIR + outFile, "-intel", 
    "-offset", "-0x8000", "-o", BUILD_DIR + outFile + ".bin", "-binary"])
