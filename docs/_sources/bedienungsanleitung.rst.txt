Bedienungsanleitung
-------------------

In diesem Abschnitt finden Sie Anpassungs- und Nutzungshinweise für verschiedene Management-Anwendungsfälle.

Die Verwaltung von Kategorien wird am ausführlichsten erklärt. Um andere Objekte wie Menüpunkte, Bestellungen, Rechnungen oder Benutzer zu verwalten, können Sie auch auf `Kategorien verwalten <kategorien-verwalten_>`_ verweisen, da die Verwaltung anderer Objekte analog zu den Kategorien funktioniert.

.. _kategorien-verwalten:

Kategorien verwalten
^^^^^^^^^^^^^^^^^^^^

Um die Menüpunktkategorien zu verwalten, öffnen Sie bitte die Admin-Seite in einem Browser unter `>Host</admin/` und loggen Sie sich mit Ihrem Admin-Konto ein.

Nachdem Sie sich mit Ihrem Admin-Konto angemeldet haben, sehen Sie eine Seite, ähnlich dem folgenden Bild. Klicken Sie nun auf "Kategorien":

.. image:: /_static/Category_(1).png
   :align: center

|

Nun sehen Sie alle Kategorien, die auf der Seite "Alle Produkte" angezeigt werden, und ihre Attribute:

.. image:: /_static/Category_(1.1).png
   :align: center

|

Kategorie hinzufügen
""""""""""""""""""""

Um eine neue Kategorie hinzuzufügen, navigieren Sie zur Admin-Seite der Kategorien und klicken Sie auf "Kategorie hinzufügen +":

.. image:: /_static/Category_(2).png
   :align: center

|

Jetzt befinden Sie sich im Menü, um eine neue Kategorie zu erstellen. Hier können Sie den gewünschten Namen, die Anzeigereihenfolge (die Liste wird aufsteigend sortiert, also erscheint eine niedrige Nummer zuerst) eingeben und festlegen, ob es sich um eine `Eventkategorie` handeln soll (wenn auf wahr gesetzt, wird diese Kategorie nur für den Benutzer mit dem Benutzernamen "event_user" angezeigt).

Um Ihre Änderung zu speichern und die neue Kategorie hinzuzufügen, klicken Sie auf einen der drei rot markierten Buttons im folgenden Bild:

.. image:: /_static/Category_(3).png
   :align: center

|

Nachdem Sie die neue Kategorie gespeichert haben, werden Sie zur Liste der Kategorien weitergeleitet. Hier wird eine Nachricht angezeigt, die angibt, ob die Erstellung erfolgreich war:

.. image:: /_static/Category_(4).png
   :align: center

|

Kategorie bearbeiten
""""""""""""""""""""

Um eine neue Kategorie hinzuzufügen, navigieren Sie zur Admin-Seite der Kategorien und klicken Sie auf den Namen der Kategorie, die Sie bearbeiten möchten:

.. image:: /_static/Category_(5).png
   :align: center

|

Nun können Sie Änderungen vornehmen, indem Sie die Felder bearbeiten und auf einen der drei Buttons unten klicken, um Ihre Änderungen zu speichern:

.. image:: /_static/Category_(6).png
   :align: center

|

Nachdem Sie Ihre Änderungen gespeichert haben, werden Sie zur Liste der Kategorien weitergeleitet. Hier wird eine Nachricht angezeigt, die angibt, ob Ihre Änderungen erfolgreich gespeichert wurden:

.. image:: /_static/Category_(7).png
   :align: center

|

Kategorie entfernen
"""""""""""""""""""

Um eine Kategorie zu entfernen, navigieren Sie zur Admin-Seite der Kategorien und markieren Sie das Kästchen der Kategorie, die Sie entfernen möchten:

.. image:: /_static/Category_(8).png
   :align: center

|

Wählen Sie nun die Option "Ausgewählte Kategorien löschen" aus dem Dropdown-Menü:

.. image:: /_static/Category_(9).png
   :align: center

|

Dann klicken Sie auf "Ausführen", um das Löschen auszuführen:

.. image:: /_static/Category_(10).png
   :align: center

|

Anschließend werden Sie gefragt, ob Sie sicher sind und was genau zusammen mit den ausgewählten Objekten gelöscht wird.
Klicken Sie auf "Ja, bin sicher", um zu bestätigen und mit dem Löschen fortzufahren:

.. image:: /_static/Category_(11).png
   :align: center

|

Nun werden Sie zurück zur Liste der Kategorien weitergeleitet. Hier wird eine Nachricht angezeigt, die angibt, ob das Löschen erfolgreich war:

.. image:: /_static/Category_(12).png
   :align: center

|

Menüpunkte verwalten
^^^^^^^^^^^^^^^^^^^^

Die Verwaltung von Menüpunkten funktioniert analog zur Verwaltung von Kategorien.
Daher wird dieses Kapitel nicht alles so detailliert erklären, wie es `Kategorien verwalten <kategorien-verwalten_>`_ getan hat, und wird nur Besonderheiten für Menüpunkte erklären.

Um auf die Admin-Seite der Menüpunkte von der Admin-Indexseite aus zuzugreifen, klicken Sie auf "Menüpunkte":

.. image:: /_static/MenuItem_(0).png
   :align: center

|

Nun sehen Sie alle Menüpunkte, die potenziell auf der Seite "Alle Produkte" angezeigt werden und ihre Attribute:

.. image:: /_static/MenuItem_(1).png
   :align: center

|

Hier sehen Sie, wie das Bearbeiten eines Menüpunkts aussieht.
Jeder Menüpunkt benötigt eine Kategorie, und der Versuch, einen ohne zu erstellen, funktioniert nicht.
Wenn Sie wünschen, dass ein Menüpunkt nicht mehr angezeigt wird und Sie ihn nicht entfernen möchten,
weil das Entfernen auch damit verbundene Bestellposten entfernen würde, können Sie das Kästchen "Versteckt" ankreuzen und Ihre Änderungen speichern, um sie zu verbergen.

.. image:: /_static/MenuItem_(2).png
   :align: center

|

Rechnung und Jahresendabrechnung erstellen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dieses Kapitel beschreibt den Prozess, Rechnungen an Benutzer am Ende des Jahres oder zu Beginn des neuen Jahres zu senden.

Das Erstellen oder Neuerstellen einer neuen Rechnung erfolgt immer zusammen mit der Erstellung oder Aktualisierung einer dazugehörigen Jahresendabrechnung und 0-2 dazugehörigen Zahlungen, die entweder die Schulden des Benutzers zurücksetzen (weil der geschuldete Betrag über Lastschrift eingezogen wird) oder das Guthaben auf das nächste Jahr übertragen (indem das Guthaben im alten Jahr abgezogen und im neuen Jahr hinzugefügt wird).

Rechnung erstellen
""""""""""""""""""

Um eine erste Version einer Rechnung zu erstellen, müssen Sie zunächst zur Admin-Seite der Benutzerverwaltung navigieren ("Benutzer").

Hier müssen Sie alle Benutzer markieren, für die Sie eine Rechnung erstellen möchten:

.. image:: /_static/Invoice_(1).png
   :align: center

|

Wählen Sie dann aus der Dropdown-Liste, ob Sie eine Rechnung für dieses Jahr ("Generiere Abrechnung für dieses Jahr") oder letztes Jahr ("Generiere Abrechnung für letztes Jahr") erstellen möchten:

.. image:: /_static/Invoice_(2).png
   :align: center

|

Dann klicken Sie auf "Ausführen", um die Generierung auszuführen:

.. image:: /_static/Invoice_(3).png
   :align: center

|

Nun werden Sie zur Admin-Rechnungsseite weitergeleitet.
Oben im Fenster gibt es Nachrichten, die anzeigen, ob die Erstellung erfolgreich war oder nicht.
Wenn nicht, wird der Fehler in einer weiteren Fehlermeldung mit dem Fehlertext angezeigt:

.. image:: /_static/Invoice_(4).png
   :align: center

|

In diesem Beispiel hat eine Erstellung eine Ausnahme ausgelöst, weil der Benutzer "guest_user" kein dazugehöriges UserInfo-Objekt hat und daher keine Rechnung für ihn erstellt werden konnte.

Rechnung neu erstellen
""""""""""""""""""""""

Wenn Sie mit der ersten Version einer Rechnung nicht zufrieden sind, haben Sie die Möglichkeit, diese neu zu erstellen, oder besser gesagt, eine neue Version zu erstellen, da die alte nicht gelöscht wird.

Um eine Rechnung neu zu erstellen, navigieren

 Sie zur Admin-Rechnungsseite und markieren Sie die Rechnungen, die Sie neu erstellen möchten:

.. image:: /_static/Invoice_(5).png
   :align: center

|

Wählen Sie dann die Option "Erstelle Abrechnungen neu" aus dem Dropdown-Menü und klicken Sie auf "Ausführen", um die Neuerstellung auszuführen:

.. image:: /_static/Invoice_(6).png
   :align: center

|

Nun werden Sie zurück zur Admin-Rechnungsseite weitergeleitet. Hier wird eine Nachricht angezeigt, die angibt, ob Ihre Neuerstellung erfolgreich war:

.. image:: /_static/Invoice_(7).png
   :align: center

|

E-Mail versenden
""""""""""""""""

Um einem Benutzer eine E-Mail mit der angehängten Rechnung zu senden, navigieren Sie zur Admin-Rechnungsseite und markieren Sie die Rechnungen, für die Sie eine E-Mail senden möchten, wählen Sie "Versende E-Mails" aus dem Dropdown-Menü und klicken Sie auf "Ausführen":

.. image:: /_static/Invoice_(8).png
   :align: center

|

Wenn die E-Mail erfolgreich gesendet wurde, zeigt die Spalte "E-Mail gesendet" einen grünen Haken anstelle eines roten Kreuzes:

.. image:: /_static/Invoice_(9).png
   :align: center

|

Jahresendabrechnungen als CSV exportieren
"""""""""""""""""""""""""""""""""""""""""

Um Jahresendabrechnungen als CSV-Datei zu exportieren, navigieren Sie zur Admin-Seite der Jahresendabrechnungen und dann:

- markieren Sie die Jahresendabrechnungen, die Sie exportieren möchten
- wählen Sie "Exportiere ausgewählte Jahresendabrechnungen als CSV" aus dem Dropdown-Menü
- klicken Sie auf "Ausführen"

.. image:: /_static/YearEndStatement.png
   :align: center

|

Nun sollte der Download der angeforderten CSV-Datei automatisch starten.

Bestellungen als CSV exportieren
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Um Bestellungen als CSV-Datei zu exportieren, navigieren Sie zur Admin-Bestellseite und dann:

- markieren Sie die Bestellungen, die Sie exportieren möchten
- wählen Sie "Exportiere ausgewählte Bestellungen als CSV" aus dem Dropdown-Menü
- klicken Sie auf "Ausführen"

.. image:: /_static/Order.png
   :align: center

|

Nun sollte der Download der angeforderten CSV-Datei automatisch starten.
