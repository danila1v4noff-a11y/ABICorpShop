@echo off
set PGPASSWORD=superABI_admin
"D:\Postgre\bin\psql.exe" -U postgres -d ABICorpShop -c "SELECT generate_daily_batches();"