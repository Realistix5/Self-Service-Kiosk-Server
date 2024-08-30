import json
import csv
from django.conf import settings

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.http import HttpResponse, JsonResponse, FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from .forms import FeedbackForm
from .functions.send_feedback_email import sendFeedbackEmail
from .models import *
from .functions import send_emails, member_api, sumup_api
from dotenv import load_dotenv
load_dotenv()


# Create your views here.

def user_login(request):
    """
    Handles user authentication with a username and password submitted through POST. If successful, the user is logged in
    and redirected to the all products page. If unsuccessful, the login page is re-rendered with an error message.

    - If a GET request is detected with credentials, those are also used to attempt a login.
    - Utilizes Django's built-in `authenticate` and `login` functions to manage user sessions and security.

    :param request: The HTTP request object.
    :return: A redirect to the all products page upon successful login, or the login page with an error message on failure.
    """

    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
    else:
        return render(request, 'self_service_kiosk/login.html')

    user = authenticate(username=username, password=password)
    if user is not None:
        # Save session as cookie to login the user
        login(request, user)
        # Success, now let's login the user.
        return redirect("self-service-kiosk:all_products", permanent=True)
    else:
        # Incorrect credentials, let's throw an error to the screen.
        messages.error(request, 'Fehlerhafter Nutzername oder Passwort. Bitte erneut versuchen.')
        return render(request, 'self_service_kiosk/login.html')


def guest_login(request):
    """
    Provides a login mechanism for a guest user with a hardcoded username. This function checks if the hardcoded guest user
    exists and logs them in, redirecting to the all products page. If the guest user cannot be authenticated, an error message is displayed.

    - This is intended for limited functionality access without creating a personal account.

    :param request: The HTTP request object.
    :return: A redirect to the all products page on successful login, or the login page with an error message on failure.
    """

    hardcoded_username = "guest_user"
    try:
        user = User.objects.get(username=hardcoded_username)
        # Save session as cookie to login the user
        login(request, user)
        # Redirect to desired page after successful login
        return redirect("self-service-kiosk:all_products", permanent=True)

    except User.DoesNotExist:
        # Incorrect credentials, let's throw an error to the screen.
        messages.error(request, 'Fehler beim Gast-Login. Bitte versuchen Sie es erneut.')
        return render(request, 'self_service_kiosk/login.html')


@login_required
def cart(request):
    """
    Displays the current user's shopping cart. This view provides a detailed list of :class:`~self_service_kiosk.models.MenuItem` in the cart,
    including their quantities, prices, and the subtotal for each item. It calculates the total price of all items in the cart
    and allows users to adjust item quantities through POST requests.

    - The cart contents are displayed with an option to update quantities or proceed to checkout.
    - Adjustments made via POST requests update the cart session data and the view is refreshed to reflect these changes.

    :param request: The HTTP request object.
    :return: An HttpResponse object rendering the cart page with the possibility to modify quantities or proceed to checkout.
    """

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_webview = 'wv' in user_agent.lower()  # 'wv' steht für WebView

    user_cart = request.session.get('cart', None)
    if user_cart and user_cart['items']:
        order_items = []
        total_price = 0
        for product_id, quantity in user_cart['items'].items():
            product = get_object_or_404(MenuItem, pk=product_id)
            subtotal = product.price * quantity
            order_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
            total_price += subtotal
        return render(request, 'self_service_kiosk/cart.html', {'order_items': order_items, 'total_price': total_price,
                                                                'is_webview': is_webview})
    else:
        return render(request, 'self_service_kiosk/cart.html', {'order_items': None, 'total_price': 0,
                                                                'is_webview': is_webview})


@login_required
def confirm_order(request):
    """
    Processes the final step in confirming an order based on the presence of payment details. If payment details (like a transaction ID)
    are provided and validated, an :class:`~self_service_kiosk.models.Order` is created and marked as paid. Otherwise, the order is created
    but marked as not paid.

    - The function checks for a "paid" query parameter in the request to determine if payment has been processed.
    - An :class:`~self_service_kiosk.models.Order` instance is created with a status reflecting the payment state.
    - On successful order creation, the user is redirected to a success page with details about the order status.
    - In the absence of payment confirmation, the order is still processed but marked as pending, and appropriate actions are taken based on the business logic.

    :param request: The HTTP request object.
    :return: Redirects to a success or status page detailing the order outcome.
    """

    tx_id = request.GET.get("paid")
    paid_amount = 0
    if tx_id is not None:
        paid_amount = sumup_api.confirmSumUpTransactionAndGetAmount(tx_id)

    cart = request.session.get('cart', None)
    if cart and cart['items']:
        try:
            order = Order.objects.create(user=request.user)  # Neue Bestellung in Datenbank erstellen
            for product_id, quantity in cart['items'].items():
                product = get_object_or_404(MenuItem, pk=product_id)
                OrderItem.objects.create(order=order, menu_item=product, quantity=quantity)  # OrderItem in Datenbank erstellen
            if paid_amount >= float(order.get_total_price()):
                order.paid = True
                order.save()
                case = 2
            else:
                case = 1
            if paid_amount != 0:
                Payment.objects.create(order=order, user=request.user, amount=paid_amount, transaction_id=tx_id)

            del request.session['cart']
            request.session['checkout_amount'] = str(order.get_total_price())
            return redirect("self-service-kiosk:order_success", case=case)

        except Exception as e:
            messages.error(request, 'An error occurred while confirming your order. Please try again later.')
    else:
        messages.error(request, 'Your cart is empty.')

    return redirect("self-service-kiosk:logout")


@login_required
def account_details(request):
    """
    Displays a comprehensive summary of the logged-in user's account details, including orders and payments made within the current year.
    This view is restricted to non-guest users, ensuring that sensitive financial data remains confidential.

    - Filtering orders and payments specific to the user and the current year.
    - Calculating the total unpaid amount across all orders.
    - Determining if the total amount reflects a debit or credit balance.

    The view also adapts its response based on whether the request is coming from a WebView, enhancing compatibility with mobile apps or embedded browsers.

    :param request: The HTTP request object.
    :return: An HttpResponse object rendering the account details page with order and payment information, or a simple HttpResponse denying access for guest users.
    """

    if request.user.username == "guest_user":
        return HttpResponse("not allowed for guest user")
    else:
        current_year = timezone.now().year
        # Holen Sie alle Bestellungen und Zahlungen des angemeldeten Benutzers für das aktuelle Jahr
        orders = Order.objects.filter(user=request.user, created_at__year=current_year).order_by('created_at')
        payments = Payment.objects.filter(user=request.user, order=None,
                                          created_at__year=current_year).order_by('created_at')

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_webview = 'wv' in user_agent.lower()  # 'wv' steht für WebView

        total = 0
        for order in orders:
            if not order.paid:
                total += order.get_total_price()
        for payment in payments:
            total = total - payment.amount
        isDebit = False
        if total < 0:
            total = -total
            isDebit = True
        return render(request, 'self_service_kiosk/account_details.html', {'orders': orders, 'payments': payments,
                                                                        'total_price': total, 'total_is_debit': isDebit,
                                                                        'is_webview': is_webview})


@login_required
def user_logout(request):
    """
    Handles the logout process for the current user. This function terminates the user session effectively logging out the user,
    and redirects them to the login page. This ensures that all session data is cleared and the user must re-authenticate to access
    protected resources.

    :param request: The HTTP request object.
    :return: A redirect to the login page, ensuring the user session is cleanly terminated.
    """

    logout(request)
    messages.success(request, "Du wurdest erfolgreich abgemeldet.")
    return redirect("self-service-kiosk:login", permanent=True)


@login_required
def update_quantity(request, item_id, quantity):
    """
    Dynamically updates the quantity of a specific :class:`~self_service_kiosk.models.MenuItem` in the user's cart via an AJAX call.
    This view handles quantity updates on the client side, immediately reflecting changes without reloading the page.

    - Validates the new quantity and updates the cart session data accordingly.
    - If the quantity is set to zero, the item is removed from the cart.
    - Returns a JsonResponse indicating the success or failure of the update, including the new quantity or a removal confirmation.

    :param request: The HTTP request object.
    :param item_id: The ID of the :class:`~self_service_kiosk.models.MenuItem` whose quantity is to be updated.
    :param quantity: The new quantity to be set; if zero, the item is removed.
    :return: A JsonResponse indicating the outcome of the operation.
    """
    if 'cart' in request.session:
        cart = request.session['cart']
    else:
        request.session['cart'] = cart = {}
        cart['items'] = {}

    if quantity != 0:
        cart['items'][item_id] = quantity
    else:
        cart['items'].pop(str(item_id))
    request.session['cart'] = cart

    return JsonResponse({'message': 'Quantity updated successfully'})


@login_required
def all_products_view(request):
    """
    Loads and displays all :class:`~self_service_kiosk.models.Category` objects along with their associated
    :class:`~self_service_kiosk.models.MenuItem` objects for users, differentiated by the "event_user". Categories
    and menu items are displayed based on user type and category event settings.

    For a normal user:
    - Only categories where :attr:`~self_service_kiosk.models.Category.event_category` is set to `False` are displayed.

    For the "event_user":
    - Displays all categories, including those where :attr:`~self_service_kiosk.models.Category.event_category` is set to `True`.

    Hidden :class:`~self_service_kiosk.models.MenuItem` objects (where :attr:`~self_service_kiosk.models.MenuItem.hidden` is `True`)
    are excluded from the display for all users.

    :param request: The HTTP request object.
    :return: An HttpResponse object rendering the all products page with dynamic content based on the user type and category settings.
    """

    if request.user.username != "event_user":
        categories = Category.objects.all().filter(event_category=False).order_by("order_number")
    else:
        categories = Category.objects.all().filter(event_category=True).order_by("order_number")

    # Hole den Warenkorb für die aktuelle Session
    cart_items = request.session.get('cart', {}).get('items', {})

    # Kombiniere verfügbare Produkte mit Mengen im Warenkorb
    combined_data = []
    categories_data = []
    product_counts = []
    for category in categories:
        categories_data.append({"category": category, "product_count": len(category.menuitem_set.all())})
        for item in category.menuitem_set.all().filter(hidden=False).order_by("order_number"):
            combined_data.append({
                'item': item,
                'quantity': cart_items.get(str(item.id), 0)  # 0, wenn nicht im Warenkorb
            })

    return render(request, 'self_service_kiosk/all_products.html', {'categories': categories_data, 'data': combined_data})


def register(request):
    """
    Manages user registration through both GET and POST requests. On a GET request, it renders the registration form. On a POST
    request, it processes the provided user data to create a new user account and associated
    :class:`~self_service_kiosk.models.RegistrationToken`. Upon successful creation, a confirmation email is sent.

    - The email is sent using the :class:`~self_service_kiosk.models.RegistrationToken` if the account is successfully created.
    - Appropriate success or error messages are displayed based on the outcome.
    - The user is redirected to the login page after registration or back to the registration form if errors occur.

    :param request: The HTTP request object.
    :return: An HttpResponse object either rendering the registration page or redirecting to the login page with a message.
    """

    if request.method == 'GET':
        return render(request, 'self_service_kiosk/register.html')

    elif request.method == 'POST':
        mitgliedsnummer = request.POST.get('mitgliedsnummer')
        user_exists = False
        try:
            user = User.objects.get_by_natural_key(mitgliedsnummer)
            if user.is_active:
                messages.error(request, "Nutzer ist bereits registriert und aktiviert. Nutze >>Passwort vergessen?<<,"
                                        " wenn du dich nicht mehr anmelden kannst.")
                return redirect("self-service-kiosk:login")
            else:
                messages.error(request, "Nutzer ist bereits registriert, aber nicht aktiviert.")
                user_exists = True
        except User.DoesNotExist:
            pass

        name, email, gender, street, plz, city = member_api.get_user_info(mitgliedsnummer)
        if name == "not authorized":
            messages.error(request, "Abfragen der Mitglieder-API ist fehlgeschlagen. "
                                    "Bitte kontaktiere einen Mitarbeiter.")
            return redirect("self-service-kiosk:login")
        elif name is None:
            messages.error(request, "Mitgliedsnummer konnte nicht gefunden werden. Bitte versuche es erneut.")
            return redirect("self-service-kiosk:login")
        else:
            if not user_exists:
                user = User.objects.create(username=mitgliedsnummer, email=email, password='123456', is_active=False, last_name=name)
                UserInfo.objects.create(user=user, street=street, plz=plz, city=city, gender=gender)
            RegistrationToken.objects.filter(user=user).delete()
            token = RegistrationToken.objects.create(user=user)
            send_emails.sendRegistrationEmail(token)
            messages.success(request, "Registrierungs-Email wurde an {} gesendet.".format(email))
            return redirect("self-service-kiosk:login")


def forgot_password(request):
    """
    Allows users to request a password reset. On GET, it displays the password reset form. On POST, it verifies the existence
    of a user by username and sends a password reset link if the user is active.

    - The link is generated using a `PasswordResetToken` which is sent to the user's registered email.
    - Appropriate success or error messages are displayed based on the user's existence and their account status.

    :param request: The HTTP request object.
    :return: An HttpResponse object rendering the password reset page, or redirecting with a status message.
    """

    if request.method == 'GET':
        return render(request, 'self_service_kiosk/forgot_password.html')

    elif request.method == 'POST':
        mitgliedsnummer = request.POST.get('mitgliedsnummer')
        try:
            user = User.objects.get(username=mitgliedsnummer)
        except User.DoesNotExist:
            messages.error(request, "Kein Nutzer mit dieser Mitgliedsnummer registriert. "
                                    "Bitte nutze >> Noch kein Konto? << wenn du noch kein Konto hast.")
            return redirect("self-service-kiosk:login")
        if not user.is_active:
            messages.error(request, "Nutzer ist noch nicht aktiviert. Bitte nutze >> Noch kein Konto? << " 
                                    "um dein Konto zu aktivieren.")
            return redirect("self-service-kiosk:login")
        PasswordResetToken.objects.filter(user=user).delete()
        token = PasswordResetToken.objects.create(user=user)
        send_emails.sendForgotPasswordEmail(token)
        messages.success(request, "Email, um dein Passwort zurückzusetzen wurde an {} gesendet.".format(user.email))
        return redirect("self-service-kiosk:login")


def set_password(request, token):
    """
    Allows a user to set or reset their password using a valid token received via email. This view supports POST requests
    for form submission of the new password and uses Django's `SetPasswordForm` for validation.

    - The token's validity is checked to ensure it's not expired and matches the user.
    - Upon successful password update, the token is invalidated to prevent reuse, and the user is redirected to the login page.

    :param request: The HTTP request object.
    :param token: The token used for identifying the valid password reset request.
    :return: A redirect to the login page upon successful password reset, or the same form with error messages if unsuccessful.
    """

    # Tokentype: 1 for registration, 2 for password reset
    tokentype = 1
    try:
        token_object = RegistrationToken.objects.get(token=token)

    except RegistrationToken.DoesNotExist:
        try:
            token_object = PasswordResetToken.objects.get(token=token)
            tokentype = 2
        except PasswordResetToken.DoesNotExist:
            messages.error(request, "Der aufgerufene Token wurde nicht gefunden. "
                                    "Bitte fordern Sie einen neuen an.")
            return redirect("self-service-kiosk:login")

    if token_object.is_valid():
        user = token_object.user
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                token_object.delete()

                LoginToken.objects.filter(user=user).delete()
                login_token = LoginToken.objects.create(user=user)
                send_emails.sendNewPasswordSetEmail(login_token)
                # Hier könnte man dem Benutzer mitteilen, dass das Passwort erfolgreich gesetzt wurde
                if tokentype == 1:
                    user.is_active = True
                    user.save()
                    messages.success(request, 'Dein Account wurde erfolgreich aktiviert und dein Passwort gesetzt.')
                else:
                    messages.success(request, 'Dein Passwort wurde erfolgreich geändert.')
                return redirect("self-service-kiosk:login")
        else:
            form = SetPasswordForm(user)

        return render(request, 'self_service_kiosk/set_password.html', {'form': form})
    else:
        messages.error(request, "Der aufgerufene Token wurde bereits verwendet. "
                                "Bitte fordern Sie einen neuen an.")
        return redirect("self-service-kiosk:login")


def payment_problem(request):
    """
    Handles errors during payment processing by interpreting a specific error code passed as a query parameter. This view
    renders a detailed error message explaining the potential cause and suggesting next steps or remedies.

    - Each error code corresponds to a particular payment issue, which is explained to the user.

    :param request: The HTTP request object.
    :return: An HttpResponse object rendering a page that describes the payment error based on the provided code.
    """

    statusCode = int(request.GET.get("code"))
    message = ""
    if statusCode == 1:
        message = "Es hat geklappt, wieso sind wir hier?"
    elif statusCode == 2:
        return render(request, 'self_service_kiosk/payment_failed.html')
    elif statusCode == 3:
        message = "Bitte Ortungsdienste aktivieren."
    elif statusCode == 4:
        message = "Fehlerhafte Eingabeparameter."
    elif statusCode == 5:
        message = "Fehlerhafter Token."
    elif statusCode == 6:
        message = "Verbingung fehlgeschlagen."
    elif statusCode == 7:
        message = "Keine Berechtigung."
    elif statusCode == 8:
        message = "Kein Händler eingeloggt."
    elif statusCode == 9:
        message = "Fehler: Foreign Transaction ID bereits vergeben."
    elif statusCode == 10:
        message = "Fehler: Falscher Affiliate Key."
    elif statusCode == 11:
        message = "Die Zahlung konnte nicht bestätigt werden. (Fehler 11)"
    elif statusCode == 12:
        message = "Die Zahlung konnte nicht bestätigt werden. (Fehler 12)"
    elif statusCode == 13:
        message = "Die Zahlung konnte nicht bestätigt werden. (Fehler 13)"

    return render(request, 'self_service_kiosk/payment_problem.html', {'message': message})


def order_success(request, case):
    """
    Displays a success message to the user after an order has been processed, based on the provided case parameter which indicates
    the specific scenario of the order process. The function handles different cases:

    - Case 1: Order was successfully placed but was not paid directly or fully.
    - Case 2: Order was placed and payment was successfully processed.
    - Other cases may represent various error or informational states related to order processing.

    The appropriate message is displayed to the user based on the case parameter, providing feedback on the order status.

    :param request: The HTTP request object.
    :param case: An integer representing the outcome scenario of the order process.
    :return: An HttpResponse object rendering the order success page with a contextual message based on the case.
    """

    amount = request.session.get("checkout_amount", "")
    if case == 1:
        message = "Bestellung über "+amount+"€ erfolgreich auf Rechnung bestellt."
    elif case == 2:
        message = "Bestellung über "+amount+"€ erfolgreich platziert und bezahlt."
    else:
        message = "Unbekannter Fall."
    return render(request, 'self_service_kiosk/order_success.html', {'message': message})


def qr_code_view(request):
    """
    Processes a QR code value submitted via POST. Depending on the prefix in the QR code, it redirects to different
    functionalities such as logging in, resetting a password, or handling user registration.

    - This method ensures flexibility and user-friendly interactions by using QR codes to initiate complex workflows with simple scans.

    :param request: The HTTP request object.
    :return: A redirect based on the decoded action from the QR code or a JsonResponse indicating an error if the QR code action is invalid.
    """

    if request.method == 'POST':
        qr_code = request.POST.get('qr_code', '')
        if qr_code:
            # Verarbeiten Sie hier den QR-Code-Wert und leiten Sie entsprechend weiter
            if qr_code.startswith('login:'):
                return redirect("self-service-kiosk:login_with_token", token=qr_code[len('login:'):])
            elif qr_code.startswith('reset_password:'):
                return redirect("self-service-kiosk:set_password", token=qr_code[len('reset_password:'):])
            elif qr_code.startswith('register:'):
                return redirect("self-service-kiosk:set_password", token=qr_code[len('register:'):])
            else:
                return JsonResponse({'status': 'error', 'message': 'Ungültige Aktion im QR-Code'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'QR-Code nicht gefunden'}, status=400)

    return HttpResponseForbidden()


def login_with_token(request, token):
    """
    Facilitates user login using a secure token, typically sent to the user via email or embedded in a QR code. Validates
    the token and logs the user in if the token is valid and not expired.

    - This provides an alternative login method that can be more secure and convenient for users, especially for single-use or time-sensitive sessions.

    :param request: The HTTP request object.
    :param token: The token used for the user login attempt.
    :return: A redirect to the main index page on successful login or back to the login page with an error message on token validation failure.
    """

    try:
        login_token = LoginToken.objects.get(token=token)
        if login_token.is_valid():
            login(request, login_token.user)
            return redirect('self-service-kiosk:index')
        else:
            messages.error(request, 'Dieser Token ist abgelaufen. Bitte Passwort zurücksetzen um neuen zu generieren.')
    except LoginToken.DoesNotExist:
        messages.error(request, 'Ungültiger Token.')

    return redirect('self-service-kiosk:login')


@login_required
def process_payment(request):
    """
    Manages the post-payment processing by verifying the payment details such as transaction ID and payment type. Based on
    the verification, it either completes an order or credits an account, handling both "order" and "credit" payment types.

    - Ensures that payments are processed securely and correctly, updates order status, and handles account credits.

    :param request: The HTTP request object.
    :return: A redirect to appropriate views depending on the payment outcome and type.
    """

    tx_id = str(request.GET.get("paid"))
    payment_type = str(request.GET.get("type"))

    # Wenn es bereits Zahlungen mit transaction_id gibt, zeige Fehlermeldung
    x = Payment.objects.all().filter(transaction_id=tx_id)
    if len(x) != 0:
        return redirect(reverse("self-service-kiosk:payment_problem") + "?code=11")

    if payment_type == "order":
        return redirect(reverse("self-service-kiosk:confirm_order")+"?paid="+tx_id)
    elif payment_type == "credit":
        user = request.user
        amount = sumup_api.confirmSumUpTransactionAndGetAmount(tx_id)
        if amount > 0:
            Payment.objects.create(transaction_id=tx_id, user=user, amount=amount)
            return redirect("self-service-kiosk:account_details")
        else:
            return redirect(reverse("self-service-kiosk:payment_problem")+"?code=13")
    else:
        return redirect(reverse("self-service-kiosk:payment_problem")+"?code=12")


@login_required
def invoice_view(request, file_path):
    """
    Securely delivers invoice files to authorized users. Validates if the requested file exists and checks if the user has
    the appropriate permissions to access it. This view handles the display or download of invoices stored within a secure directory.

    - Ensures that access to invoice files is restricted to authorized personnel, preventing unauthorized data access.

    :param request: The HTTP request object.
    :param file_path: The relative path to the invoice file intended for access.
    :return: A FileResponse allowing the authorized download of the invoice, or an HttpResponseForbidden if access is denied.
    """

    base_path = os.path.abspath(os.path.join(settings.BASE_DIR, 'invoices'))
    media_path = os.path.join(base_path, file_path)

    if os.path.exists(media_path):
        if request.user.is_staff:
            return FileResponse(open(media_path, 'rb'))
        else:
            messages.error(request, "Sie haben keine Berechtigung, auf diese Datei zuzugreifen.")
            return redirect("admin:login")
    else:
        messages.error(request, "Die Datei konnte nicht gefunden werden.")
        return redirect("admin:index")


@login_required
def order_detail(request, order_id):
    """
    Displays detailed information about an order specified by the order_id. This view checks if the logged-in user has the
    appropriate permissions to view the order details. The view includes comprehensive information about the order including
    items, quantities, and prices at the time of purchase.

    - Provides a detailed breakdown of the order to support customer service and order management operations.

    :param request: The HTTP request object.
    :param order_id: The identifier of the order to be detailed.
    :return: An HttpResponse object rendering the detailed view of the order if access is permitted, or an HttpResponseForbidden
             if the user is not authorized to view the details.
    """

    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'self_service_kiosk/order.html', {'order': order})


@csrf_protect
def help_page(request):
    """
    Renders a help page where users can submit feedback via a form. This POST endpoint handles the form submission, validates
    the feedback, and sends it via email if valid. A confirmation message is displayed after successful submission.

    - Enhances user support by providing a direct method for feedback submission and immediate response handling.

    :param request: The HTTP request object.
    :return: An HttpResponse object either displaying the form with success confirmation or re-rendering the form for further input.
    """

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_text = form.cleaned_data['feedback_text']
            feedback_sender = form.cleaned_data.get('feedback_sender', 'Anonym')
            sendFeedbackEmail(feedback_text, feedback_sender)
            return render(request, "self_service_kiosk/help_page.html", {'form': None, 'success': True})
    else:
        form = FeedbackForm()

    return render(request, "self_service_kiosk/help_page.html", {'form': form})


@csrf_exempt
def send_feedback(request):
    """
    Receives feedback as a JSON payload via a POST request, processes it, and forwards the feedback via email. This function
    validates the JSON structure, extracts feedback details, and uses an email service to send the feedback to a specified recipient.

    - Facilitates asynchronous feedback collection from users, enhancing user engagement and support.

    :param request: The HTTP request object.
    :return: A JsonResponse indicating the success or failure of the feedback submission.
    """

    if request.method == "POST":
        data = json.loads(request.body)
        feedback_text = data.get('feedback_text')
        feedback_sender = data.get('feedback_sender', 'Anonym')
        if feedback_text:
            sendFeedbackEmail(feedback_text, feedback_sender)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})
