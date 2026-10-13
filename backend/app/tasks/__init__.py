"""Background task package (Celery).

Tasks are kept thin: they open a session, select the rows that are due, and call
into ``app.services`` for anything that looks like business logic.
"""
