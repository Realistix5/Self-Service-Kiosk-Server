import requests
import os


def confirmSumUpTransactionAndGetAmount(transaction_id):
    try:
        headers = {'Authorization': 'Bearer ' + os.environ.get('SUMUP_API_KEY'), }
        params = {'transaction_code': transaction_id, }
        response = requests.get('https://api.sumup.com/v0.1/me/transactions/history', params=params, headers=headers)
        result = response.json()
        try:
            payment = result["items"][0]
            status = payment["status"]
            if status != "SUCCESSFUL":
                return 0
            else:
                return float(payment["amount"])
        except IndexError:
            return -1

    except requests.RequestException:
        return -1
