import requests
import os

from fetchbim import settings as s
from dotenv import load_dotenv
load_dotenv()

BIMSERVICE_KEY=os.getenv('BIMSERVICE_KEY')

def get_ids(key='Public'):
    response = requests.get(s.BIMSERVICE_ENDPOINTS[key])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print('ERROR!')
    except requests.exceptions.ConnectionError:
        print('CONNECTION ERROR!')

    return response.json()