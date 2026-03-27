@echo off
echo ============================================================
echo      SDSS Cosmic Web Pipeline Execution (Full Run)
echo ============================================================
echo.

echo === 1. Building density map ===
python data_processing_and_maps\build_density_map.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 2. Degrading maps (low resolution) ===
python data_processing_and_maps\degrade_maps.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 3. Classifying Cosmic Web ===
python data_processing_and_maps\classify_cosmic_web.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 4. Running TDA (Phi) ===
python tda_and_topology\tda_phi.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 5. Running TDA (Ripser) ===
python tda_and_topology\tda_ripser.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 6. Computing Fisher information ===
python information_theory_analysis\fisher_analysis.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 7. Computing Information Bottleneck (Eta IB) ===
python information_theory_analysis\compute_eta_IB_cosmic.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === 8. Computing ETF-score and Correlation ===
python statistical_metrics\etf_correlation.py
IF %ERRORLEVEL% NEQ 0 ( echo Error occurred! & exit /b %ERRORLEVEL% )

echo.
echo === Pipeline Completed Successfully! ===
pause