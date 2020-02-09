# Generic single-database configuration.

PyWPS uses [alambic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) for
database configuration.

## To initialize new database and apply all changes

Run

```
export PYWPS_CFG=path/to/your/pywps.cfg
alembic -c alembic.ini upgrade head
```

With `alembic.ini`

```
[alembic]
script_location = pywps:alembic
```

You should get output similar to

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade eead25e2ad3a -> 01d5298bfc61, Add process column to Request
```

## To make changes in database structure

1. Change ORM

        Currently, all changes in the database are done in `pywps/dblog.py` - make the
        changes there to the objects `ProcessInstance` and `RequestInstance`.

2. Set fake configuration file variable

        ```
        export PYWPS_CFG=pywps/alembic/fake_pywps.cfg
        ```

    **NOTE:** If you use your own PyWPS configuration, just make sure, the
    database is up-to-date to previous PyWPS ORM models.

3. Run the initial import

        ```
        alembic -c alembic.ini upgrade head
        ```

4. Autogenerate new change

        ```
        alembic -c alembic.ini revision --autogenerate -m "[DESCRIPTION TEXT]"
        ```

5. Apply change on fake database

        ```
        alembic -c alembic.ini upgrade head
        ```

6. If everything works, `git add && git commit && git push` to PyWPS code base.
