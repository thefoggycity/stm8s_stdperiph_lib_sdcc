# stm8s_stdperiph_lib_sdcc

---

## Overview

This is a SDCC port of the STMicroelectronics official Standard Peripheral Libarary for STM8S/A series microcontrollers ([STSW-STM8069](https://www.st.com/en/embedded-software/stsw-stm8069.html)).

SDCC support is added *in addition to* the originally supported toolchains, inculding IAR, COSMIC and RAISONANCE. Source file `stm8s.h`, `stm8s_itc.h`, together with `main.c`, `stm8s_it.h` are modified for SDCC to work.

An Powershell build script `build.ps1` is included. Change the microcontroller model definition in the file and run the script to build. By default it invokes the `srec_cat.exe` to convert Intel Hex output of SDCC to binary.

## Use the sources

* Code your program in `./Core/Inc`, `./Core/Src` and `./Inc`, `./Src`. Those paths are configured in the build script `build.ps1`.

* Change the variables at the top of the `build.ps1` script, notably the microcontroller model, and run it with Powershell. Alternatively, you can write your own makefile based on that script if you do not want to use Powershell.

* Flash the output `main.ihx` to your microcontroller.

Additionally, if Visual Studio Code is used, the configuration file in `./.vscode` could be useful for C IntelliSense. (Note that the last 2 definitions are meant for warning suppression and should *not* be used with SDCC.)
  
## License

Sources in this repository is subject to STMicroelectronics' Liberty License (refer to [LICENSE](LICENSE)), except for:

* `srec_cat.exe` by Scott Finneran, licensed under [GNU GPL](http://www.gnu.org/licenses/gpl.txt).
* `build.ps1` licensed under the [MIT license](https://opensource.org/licenses/MIT).
