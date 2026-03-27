@echo off
echo === Building density map ===
python build_density_map.py
IF %ERRORLEVEL% NEQ 0 (
  echo Error occurred during build_density_map.py
  exit /b %ERRORLEVEL%
)

echo === Computing Fisher information ===
python fisher_analysis.py
IF %ERRORLEVEL% NEQ 0 (
  echo Error occurred during fisher_analysis.py
  exit /b %ERRORLEVEL%
)

echo === Running TDA ===
python tda_phi.py
IF %ERRORLEVEL% NEQ 0 (
  echo Error occurred during tda_phi.py
  exit /b %ERRORLEVEL%
)

echo === Computing ETF-score ===
python etf_correlation.py
IF %ERRORLEVEL% NEQ 0 (
  echo Error occurred during etf_correlation.py
  exit /b %ERRORLEVEL%
)

echo Done.
