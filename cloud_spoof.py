from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
from core.modules.googleapis import oauth
from spoof2 import Data

def tpe_execute(fn=[]):
    with ThreadPoolExecutor(max_workers=3) as executor:
        future = executor.submit(fn=fn)
        dnd = wait(fs=[future])
        if not dnd.done:
            dnd = wait(fs=[future], timeout=120, return_when=FIRST_EXCEPTION)
        print(dnd)
        results = future.result()
        if results:
            print("Yay!")
            print(results)
        else:
            print("Not Found.")


def connect_to_googleapis_via_api():
    data = Data()
    aad_session = oauth.aad(
        client_id=data.oauth["googleapis"]["client_id"],
        client_secret=oauth["googleapis"]["client_secret"]
    )
    print(aad_session)


if __name__ == '__main__':
    connect_to_googleapis_via_api()


