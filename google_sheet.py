import gspread
from oauth2client.service_account import ServiceAccountCredentials

def add_order_to_sheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1pX1YW3E5H3vIPaw1spssEVMF05eDpWvDZndIMa6yEV0/edit#gid=0").sheet1
    sheet.append_row([data["Имя"], data["Телефон"], data["Сообщение"]])
