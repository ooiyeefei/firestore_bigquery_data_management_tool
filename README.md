# cfmt_host
sample project for company funding management tool

## How to run the application locally
- `cd cfmt_host/server/src`
- `pip install -r requirements.txt`
- Set up your Firebase Cloud Firestore database and create new collection or use existing collection https://firebase.google.com/docs/firestore/quickstart
- Retrieve your own Firebase key for authentication https://firebase.google.com/docs/admin/setup#:~:text=To%20generate%20a,Settings%20%3E%20Service%20Accounts.
- replace the context of your private key json file with the file `key.json.sample` and rename to `key.json`
- `python3 app.py`

## Reference architecture
<img src="https://github.com/ooiyeefei/cfmt_host/blob/main/cfmt_archi.jpeg?raw=true" />
