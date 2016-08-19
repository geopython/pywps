========
REST API
========

Processes published in PyWPS instance.

/processes
==========

Lists running processes.

+--------+-----------------------------------------+----------+--------------+------------+
| Method | Action                                  | Format   | Status Code  | Returns    |
+========+=========================================+==========+==============+============+
| GET    | Returns a list of running processes     | JSON     | 200          | processes  |
+--------+-----------------------------------------+----------+--------------+------------+
| POST   |                                         |          | 405          |            |
+--------+-----------------------------------------+----------+--------------+------------+
| PUT    |                                         |          | 405          |            |
+--------+-----------------------------------------+----------+--------------+------------+
| DELETE |                                         |          | 405          |            |
+--------+-----------------------------------------+----------+--------------+------------+

Returns
-------

**processes**
    Returns a list of running processes, every process is represented by *uuid*.


/processes/<uuid>
=================

Controls a running process.

+--------+--------------------------------------------+----------+--------------+------------+---------------------------------+
| Method | Action                                     | Format   | Status Code  | Parameters | Returns                         |
+========+============================================+==========+==============+============+=================================+
| GET    | Returns a message (description) and status | JSON     | 200          |            | error, message, success, status |
+--------+--------------------------------------------+----------+--------------+------------+---------------------------------+
| POST   | Returns a running description and status   | JSON     | 405          |            | error, status                   |
+--------+--------------------------------------------+----------+--------------+------------+---------------------------------+
| PUT    | Manipulates a running process              | JSON     | 200          | action     | error, status                   |
+--------+--------------------------------------------+----------+--------------+------------+---------------------------------+
| DELETE | Stop a running process                     | JSON     | 200          |            | error, status                   |
+--------+--------------------------------------------+----------+--------------+------------+---------------------------------+

Parameters
----------

**action**
    Specifies what action would you like a process to perform.

    Options:
        **pause** - Pause a running process.

        **resume** - Resume a paused process.

Returns
-------

**message**:
    The last message/status provided by a process. These messages are designed by creators of processes scripts.

**error**:
    Describes why was the request unsuccessful. The *error* field is provided only if the *status* field has a value *false*.

**success**:
    Describes if the request was successful or not.

    Options:
        **true** - A successfully served request.

        **false** - Unsuccessfully served request. An *error* message is also returned with this type of response.

**status**:
    Describes what is the status of the process.

    Options:
        **0** - NO STATUS

        **1** - STORE STATUS

        **2** - STORE AND UPDATE STATUS

        **3** - DONE STATUS

        **4** - PAUSED STATUS

        **5** - STOPPED STATUS

Example
-------

*http://localhost/wps/processes/slakdfj-234-ASDF-234* with PUT request ``{"action": "pause"}`` returns ``{"success": "true"}``

