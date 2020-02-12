# Specify the build parameters
$DrvSrcDir = 
    ".\Driver\Src"
$IncDir = 
    ".\Core\Inc", 
    ".\Driver\Inc", 
    ".\Inc"
$SrcDir = 
    ".\Core\Src", 
    $DrvSrcDir, 
    ".\Src"
$DefChipModel = 
    "STM8S003"
$ExtraDefs = 
    @() # Definitions other than chip model
$Opts = 
    "-mstm8",
    "--std-c99"
$BuildDir = 
    ".\build"

# Collate the necessary libraries' sources
$DrvSrcs = @(
    # Sources that are applicable to all models
    # Comment/Delete the peripherals that are not used to reduce code size
    "stm8s_awu.c", "stm8s_beep.c", "stm8s_clk.c", "stm8s_exti.c", "stm8s_flash.c",
    "stm8s_gpio.c", "stm8s_i2c.c", "stm8s_itc.c", "stm8s_iwdg.c", "stm8s_rst.c", 
    "stm8s_spi.c", "stm8s_tim1.c", "stm8s_wwdg.c"
)
$ModelHash = @{
    # Sources that are only applicable to selective models
    # Comment/Delete the peripherals that are not used to reduce code size
    "stm8s_adc1.c" = 
        "STM8S105", "STM8S005", "STM8S103", "STM8S003", "STM8S001", 
        "STM8S903", "STM8AF626x", "STM8AF622x";
    "stm8s_adc2.c" = 
        "STM8S208", "STM8S207", "STM8S007", "STM8AF52Ax", "STM8AF62Ax";
    "stm8s_can.c" = 
        "STM8S208", "STM8AF52Ax";
    "stm8s_tim2.c" = 
        "STM8S903", "STM8AF622x";
    "stm8s_tim3.c" = 
        "STM8S208", "STM8S207", "STM8S007", "STM8S105", "STM8S005", 
        "STM8AF52Ax", "STM8AF62Ax", "STM8AF626x";
    "stm8s_tim4.c" = 
        "STM8S903", "STM8AF622x";
    "stm8s_tim5.c" = 
        "STM8S903", "STM8AF622x";
    "stm8s_tim6.c" = 
        "STM8S903", "STM8AF622x";
    "stm8s_uart1.c" = 
        "STM8S208", "STM8S207", "STM8S007", "STM8S103", "STM8S003", 
        "STM8S001", "STM8S903", "STM8AF52Ax", "STM8AF62Ax";
    "stm8s_uart2.c" = 
        "STM8S105", "STM8S005", "STM8AF626x";
    "stm8s_uart3.c" = 
        "STM8S208", "STM8S207", "STM8S007", "STM8AF52Ax", "STM8AF62Ax";
    "stm8s_uart4.c" = 
        "STM8AF622x"
}
$ModelHash.Keys | ForEach-Object {
    if ($DefChipModel -in $ModelHash.$_) {$DrvSrcs += $_}
}

# Clear all built files in the build directory
Remove-Item -Recurse "$BuildDir\*"

# Construct the option string passing to SDCC
$IncOptStr = ""
$IncDir | ForEach-Object { $IncOptStr += " -I$_" }
$DefsOptStr = " -D$DefChipModel"
$ExtraDefs | ForEach-Object { $DefsOptStr += " -D$_" }
$OptsStr = ""
$Opts | ForEach-Object { $OptsStr += "$_ " }

$ObjDirList = @()
$SrcDir | ForEach-Object {
    $CurrSrcDir = $_
    $ObjDir = "$BuildDir\Obj\" + $CurrSrcDir.Substring(2)
    $ObjDirList += $ObjDir
    New-Item -Path $ObjDir -ItemType Directory -ErrorAction SilentlyContinue | Out-Null
    Get-ChildItem $CurrSrcDir -Filter *.c | Foreach-Object {
        Write-Output "Building `"$($_.Name)`"..."
        if ($CurrSrcDir -eq $DrvSrcDir -and -not ($($_.Name) -in $DrvSrcs)) { return }
        $cmd = ("sdcc.exe " + 
            "$OptsStr $DefsOptStr $IncOptStr -c $CurrSrcDir\$($_.Name) -o $ObjDir\$($_.BaseName).rel")
        Invoke-Expression $cmd
    }
}

$ObjList = @()
$ObjDirList | ForEach-Object {
    Get-ChildItem $_ -Filter *.rel | ForEach-Object {
        $ObjList += $_
    }
}

Write-Output "Linking..."
$OutFile = "$BuildDir\main.ihx"
Start-Process "sdcc.exe" -ArgumentList $($Opts + $ObjList + " -o" + $OutFile) -Wait -NoNewWindow

# Optionally convert the Intel Hex output to binary
Write-Output "Writing binary file..."
& ".\srec_cat.exe" -disable-sequence-warning $OutFile -intel -o $BuildDir\main.bin -binary

Write-Output "Done."