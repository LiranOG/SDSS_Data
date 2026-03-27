@echo off 
setlocal enabledelayedexpansion 
 
:: ============================================================ 
::   SDSS DR18 Analysis Pipeline - Windows Batch (With Conda) 
:: ============================================================ 
set ENV_NAME=sdss_analysis 
set PYTHON_VERSION=3.12 

:: List of all updated scripts with their folder paths
set SCRIPTS=data_processing_and_maps\build_density_map.py data_processing_and_maps\degrade_maps.py data_processing_and_maps\classify_cosmic_web.py tda_and_topology\tda_phi.py tda_and_topology\tda_ripser.py information_theory_analysis\fisher_analysis.py information_theory_analysis\compute_eta_IB_cosmic.py statistical_metrics\etf_correlation.py

:: Generate clean Timestamp for log file
set "YYYY=%DATE:~6,4%"
set "MM=%DATE:~3,2%"
set "DD=%DATE:~0,2%"
set "HH=%TIME:~0,2%"
set "HH=%HH: =0%"
set "MIN=%TIME:~3,2%"
set "SEC=%TIME:~6,2%"
set LOG_FILE=pipeline_%YYYY%%MM%%DD%_%HH%%MIN%%SEC%.log 
 
:: 1. Locate Conda 
echo [INFO] Checking for Conda... 
where conda >nul 2>&1 
if %errorlevel% neq 0 ( 
    echo [ERROR] Conda not found. Please install Miniforge or Anaconda. 
    echo Download: https://github.com/conda-forge/miniforge 
    pause 
    exit /b 1 
) 
 
:: 2. Ensure Conda is initialized for this shell 
call conda init cmd.exe >nul 2>&1 
 
:: 3. Check if environment exists 
call conda info --envs | findstr /C:"%ENV_NAME%" >nul 2>&1 
if %errorlevel% equ 0 ( 
    echo [INFO] Conda environment '%ENV_NAME%' already exists. 
) else ( 
    echo [INFO] Creating environment '%ENV_NAME%' with Python %PYTHON_VERSION%... 
    call conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y >> "%LOG_FILE%" 2>&1 
    if %errorlevel% neq 0 ( 
        echo [ERROR] Failed to create environment. See %LOG_FILE% 
        pause 
        exit /b 1 
    ) 
) 
 
:: 4. Activate environment 
echo [INFO] Activating environment... 
call conda activate %ENV_NAME% 
if %errorlevel% neq 0 ( 
    echo [ERROR] Could not activate environment. 
    pause 
    exit /b 1 
) 
 
:: 5. Install packages 
echo [INFO] Installing required packages... This may take a few minutes. 
call conda install -y -c conda-forge numpy scipy matplotlib astropy healpy scikit-learn >> "%LOG_FILE%" 2>&1 
if %errorlevel% neq 0 ( 
    echo [ERROR] Conda install failed. Check %LOG_FILE% 
    pause 
    exit /b 1 
) 
call pip install giotto-tda ripser >> "%LOG_FILE%" 2>&1 
if %errorlevel% neq 0 ( 
    echo [ERROR] pip install failed. 
    pause 
    exit /b 1 
) 
 
:: 6. Run each script 
echo [INFO] Starting pipeline execution... 
set SCRIPT_FAILED=0 
for %%s in (%SCRIPTS%) do ( 
    echo [RUN] %%s 
    python %%s >> "%LOG_FILE%" 2>&1 
    if !errorlevel! neq 0 ( 
        echo [ERROR] Script %%s failed. See %LOG_FILE% 
        set SCRIPT_FAILED=1 
        goto :exit_script 
    ) 
    echo [DONE] %%s completed. 
) 
 
:exit_script 
if %SCRIPT_FAILED% equ 1 ( 
    echo [ERROR] Pipeline finished with errors. 
) else ( 
    echo [SUCCESS] All scripts executed successfully! 
) 
 
call conda deactivate 
echo [INFO] Log saved to %LOG_FILE% 
pause