Technical Documentation
=======================

This chapter provides a technical documentation of the Self-Service-Kiosk Django application. It is structured in the following sections:

-   `Models <models_>`_
-   `Views <views_>`_
-   `Unit Tests <unit-tests_>`_
-   `Building this documentation <building-this-documentation_>`_

.. _models:

Models
------

.. automodule:: self_service_kiosk.models
   :no-undoc-members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, objects, get_next_by_created_at, get_previous_by_created_at, get_next_by_valid_until, get_previous_by_valid_until, get_next_by_changed_at, get_previous_by_changed_at

.. _views:

Views
-----

.. automodule:: self_service_kiosk.views

.. _unit-tests:

Unit Tests
----------

In this chapeter we will explain how to run the unit tests for the Self-Service-Kiosk Django application.

The test concept for the Self-Service-Kiosk Django application is focused the views of the application.
Each view has a corresponding test class in the `self_service_kiosk/tests` directory and is tested with multiple test cases. As a result the code coverage of `views.py` is 100%.

The tests are written using the Django testing framework and are located in the `self_service_kiosk/tests` directory.

Run Unit Tests
^^^^^^^^^^^^^^

To simply run all unit tests, execute the following command in the parent `mysite` directory:

.. code-block:: bash

    python manage.py test

Run Tests with Coverage
^^^^^^^^^^^^^^^^^^^^^^^

To run all unit tests and get a coverage html report you need to first install the `coverage` Python package:

.. code-block:: bash

    pip install coverage

Then you can run the unit tests with coverage and generate the html report with the following commands:

.. code-block:: bash

    coverage run --source='.' manage.py test
    coverage html

After executing the above commands, you can find the coverage html report in the `htmlcov` directory.

.. _building-this-documentation:

Building this documentation
---------------------------

If you want to build this documentation for yourself, you need to install the `sphinx` Python package and the `spinx` extensions used for this project:

.. code-block:: bash

    pip install sphinx sphinx_rtd_theme sphinxcontrib_django

Then you can build the documentation by executing the following command in the `mysite` directory:

.. code-block:: bash

    sphinx-build -b html source build

After executing the above command, you can find the built documentation in the `build` directory.

