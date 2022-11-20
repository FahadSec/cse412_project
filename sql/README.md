To use the database dump:

1. Download psql
https://www.postgresql.org/download/


2. Create DB

```
createdb -T template0 cse412_dev
```

3. Restore dump
```
psql cse412_dev < database_dump.sql
```
