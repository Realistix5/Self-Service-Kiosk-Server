# Self-Service-Kiosk Server by Christopher Trautmann

## Introduction

This project was designed and developed as part of my bachelor thesis, aiming to provide a self-service kiosk for a local tennis club.

This repository contains the server application for the project using the Python Django framework. It is intended to be used together with [Self-Service-Kiosk Client](https://github.com/Realistix5/Self-Service-Kiosk-Client) which contains an Android App that can access the webserver through a webview, process card and mobile payments and communicate the result back to the webserver. Together they provide a self-service-kiosk for a tennis club, allowing members to order food and drinks, pay directly or later and view their account details.

## Features
- **Simple Order Process** with option to pay directly or later
- **Secure Payment Confirmation** on server side via SumUp-API
- **Fast Authentication** using QR-Codes that encode UUID4s for members or simply access as a guest
- **Extensive Account Details** showing old orders and balance payments
- **Various Management Tools** including invoices, yearendstatements and reporting
- **Seasonal Event Items** with custom user to manage items sold only on special occasions

## Limitations
Because the project was custom developed for a german tennis club, there are a few limitations that you should consider before thinking about adapting it in another context:
### Registration
The registration process was specifically designed to use an existing API of the tennis club it was developed for. If adapted in another context this needs to be reworked completely.
### Language
The whole front end of the webserver is in German language. Changing it to another language does require some work, but should be possible in a reasonable amount of time. In particular:
- **HTML-Templates:** Most of the work is going over all the HTML-templates and translating them. Those can be found under [/mysite/self_service_kiosk/templates/self_service_kiosk/](/mysite/self_service_kiosk/templates/self_service_kiosk/).
- **Verbose Names:** The verbose names in models.py are in German and there are also German short descriptions in admin_functions.py and custom filters, with German options in admin.py.
- **Email and Invoice Texts:** The email and invoice texts are hardcoded in send_emails.py and generators.py .
### Payment Service Provider (SumUp)
This project uses the SumUp API to process card payments and is limited to that provider. If you want to use another payment service provider, you need to replace the SumUp API calls in `functions/sumup_api.py` with the respective API calls of your provider.

## Documentation
A detailed documentation of the project can be found in the `docs` folder and can be viewed [here](https://realistix5.github.io/Self-Service-Kiosk-Server/).

## License
This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments
This project is based on [Django](https://github.com/django/django), a high-level Python Web framework.

The project was developed as part of my bachelor thesis at the [Hochschule Darmstadt - University of Applied Sciences](https://h-da.de/).

I would like to thank my supervisor [Prof. Dr. Daniel Burda](https://fbi.h-da.de/personen/daniel-burda) for his support and guidance throughout the project.

I would also like to thank the [tennis department of GSV Gundernhausen e.V.](https://tennis.gsv-gundernhausen.de/) for providing the opportunity to develop this project for them.
