========
REST API
========

Processes
=========

Processes published in PyWPS instance.

/processes
----------

Controls running processes.

+--------+-----------------------------------------+----------+--------------+
| Method | Action                                  | Format   | Status Code  |
+========+=========================================+==========+==============+
| GET    | Returns a list of running processes     | JSON     | 200          |
+--------+-----------------------------------------+----------+--------------+
| POST   |                                         |          | 405          |
+--------+-----------------------------------------+----------+--------------+
| PUT    |                                         |          | 405          |
+--------+-----------------------------------------+----------+--------------+
| DELETE |                                         |          | 405          |
+--------+-----------------------------------------+----------+--------------+

/processes/<uuid>
-----------------

Controls running process.

+--------+------------------------------------------+----------+--------------+------------+
| Method | Action                                   | Format   | Status Code  | Parameters |
+========+==========================================+==========+==============+============+
| GET    | Returns a list of running processes      | JSON     | 200          |            |
+--------+------------------------------------------+----------+--------------+------------+
| POST   | Returns a running description and status | JSON     | 405          |            |
+--------+------------------------------------------+----------+--------------+------------+
| PUT    | Manipulates a running process            | JSON     | 200          | action     |
+--------+------------------------------------------+----------+--------------+------------+
| DELETE | Stop a running process                   | JSON     | 200          |            |
+--------+------------------------------------------+----------+--------------+------------+

Parameters
~~~~~~~~~~

**action**
    **pause** - Pause a running process.

    **resume** - Resume/Unpause a paused process.

Responses
~~~~~~~~~

**status**
    **true** - A successfully served request.

    **false** - An unsuccessfully served request. An error message is also returned with this type of response.

Example
~~~~~~~

