Usage Instructions
------------------

In this section you will find customization and usage instructions for different management use cases.

The management of categories is explained most extensively. To manage other objects like menu items, orders, invoices or users, you can also refer to `Manage Categories <manage-categories_>`_, because managing other objects works analogue to categories.


.. _manage-categories:

Manage Categories
^^^^^^^^^^^^^^^^^

To manage the menu item categories, please open the admin page in a browser under `>Host</admin/` and login with your admin account.

Once logged in with your admin account you will see a page, similar to the following picture. Now click "Kategorien":

.. image:: /_static/Category_(1).png
   :align: center

|

Now you see all categories that will be shown on the "All Products" page and their attributes:

.. image:: /_static/Category_(1.1).png
   :align: center

|

Add Category
""""""""""""

To add a new category, navigate to the categories admin page and click "Kategorie hinzufügen +":

.. image:: /_static/Category_(2).png
   :align: center

|

Now you are in the menu to create a new category. Here you can insert the desired name, the order_number in which it will be displayed (list gets sorted ascending, so low number comes first) and if it should be a `event category` (if set to true this category gets only displayed for the user with username "event_user").

To save your change and add the new category, click one of the three buttons marked red in the following picture:

.. image:: /_static/Category_(3).png
   :align: center

|

After saving the new category, you will be redirected to the list of categories. Here a message will show, indicating if the creation was successful:

.. image:: /_static/Category_(4).png
   :align: center

|

Edit Category
"""""""""""""

To add a new category, navigate to the categories admin page and click on the name of the category you want to edit:

.. image:: /_static/Category_(5).png
   :align: center

|

Now you can make changes by editing the fields and clicking one of the three buttons on the bottom to save your changes:

.. image:: /_static/Category_(6).png
   :align: center

|

After saving your changes, you will be redirected to the list of categories. Here a message will show, indicating if your changes were saved successfully:

.. image:: /_static/Category_(7).png
   :align: center

|

Remove Category
"""""""""""""""

To remove a category, navigate to the categories admin page and check the box of the category you want to remove:

.. image:: /_static/Category_(8).png
   :align: center

|

Now select the option "Ausgewählte Kategorien löschen" from the drop-down menu:

.. image:: /_static/Category_(9).png
   :align: center

|

Then click on "Ausführen" to execute the deletion:

.. image:: /_static/Category_(10).png
   :align: center

|

Next, you get asked if you are sure and what exactly will be deleted along with the selected objects.
Click "Ja, bin sicher" to confirm and proceed with the deletion:

.. image:: /_static/Category_(11).png
   :align: center

|

Now you get redirected back to the list of categories. Here a message will show, indicating if the deletion was successful:

.. image:: /_static/Category_(12).png
   :align: center

|

Manage Menu Items
^^^^^^^^^^^^^^^^^

The management of menu items works analogue to the management of categories.
Thus this chapter will not explain everything as detailed as `Manage Categories <manage-categories_>`_ did and will only explain peculiarities for menu items.

To access the menu item admin page from the admin index page, click "Menüpunkte":

.. image:: /_static/MenuItem_(0).png
   :align: center

|

Now you see all menu items that will potentially be shown on the "All Products" page and their attributes:

.. image:: /_static/MenuItem_(1).png
   :align: center

|

Here you can see what editing a menu item looks like.
Every menu item needs a category and trying to create one without will not work.
If you wish that a menu item does not get shown anymore and you do not want to remove it,
because removing would also remove relating order items, you can check the "Versteckt" box and save your changes to hide them.

.. image:: /_static/MenuItem_(2).png
   :align: center

|

Create Invoice and Year End Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chapter describes the process to send invoices to users at the end of the year or beginning of the new year.

Creating or recreating a new invoice comes always with the creation or update of a relating yearendstatement and 0-2 relating payments which either reset users debt (because the amount in debt is collected via direct debt) or transfers balance over to the next year (by subtracting the balance in the old and adding it in the new year).

Create Invoice
""""""""""""""

To create a first version of an invoice you need to first navigate to the admin user management page ("Benutzer").

Here you need to check all users you want to create an invoice for:

.. image:: /_static/Invoice_(1).png
   :align: center

|

Next, select from the drop-down list if you want to generate an invoice for this year ("Generiere Abrechnung für dieses Jahr") or last year ("Generiere Abrechnung für letztes Jahr"):

.. image:: /_static/Invoice_(2).png
   :align: center

|

Then, click on "Ausführen" to execute the generation:

.. image:: /_static/Invoice_(3).png
   :align: center

|

Now, you get redirected to the admin invoice page.
There are messages at the top of the window indicating if the creation was successful or not.
If not, the exception gets shown in another error message containing the exception text:

.. image:: /_static/Invoice_(4).png
   :align: center

|

In this example one creation threw an exception, because the user "guest_user" has no relating UserInfo object and thus it was not possible to create an invoice for him.

Recreate Invoice
""""""""""""""""

If you are not satisfied with the first version of an invoice, you got the option to recreate them, or better said, create a new version, because the old one will not get deleted.

To recreate an invoice navigate to the admin invoice page and check the invoices you want to recreate:

.. image:: /_static/Invoice_(5).png
   :align: center

|

Next, select the option "Erstelle Abrechnungen neu" from the dop-down menu and click on "Ausführen" to execute the recreation:

.. image:: /_static/Invoice_(6).png
   :align: center

|

Now you get redirected back to the invoice admin page. Here a message will show, indicating if your recreation was successful:

.. image:: /_static/Invoice_(7).png
   :align: center

|

Send Email
""""""""""

To send an email to a user with the invoice attached, navigate to the admin invoice page and check the invoices you want to send an email for, select "Versende E-Mails" from the drop-down menu and click on "Ausführen":

.. image:: /_static/Invoice_(8).png
   :align: center

|

If the email was sent successfully, the column "E-Mail gesendet" will show a green checkmark instead of a red cross:

.. image:: /_static/Invoice_(9).png
   :align: center

|

Export Year End Statements to CSV
"""""""""""""""""""""""""""""""""

To export year end statements to a CSV file, navigate to the admin year end statements page and then:

- check the year end statements you want to export
- select "Exportiere ausgewählte Jahresendabrechnungen als CSV" from the drop-down menu
- click on "Ausführen"

.. image:: /_static/YearEndStatement.png
   :align: center

|

Now the download of the requested CSV-file should start automatically.

Export Orders to CSV
^^^^^^^^^^^^^^^^^^^^

To export orders to a CSV file, navigate to the admin order page and then:

- check the orders you want to export
- select "Exportiere ausgewählte Bestellungen als CSV" from the drop-down menu
- click on "Ausführen"

.. image:: /_static/Order.png
   :align: center

|

Now the download of the requested CSV-file should start automatically.

