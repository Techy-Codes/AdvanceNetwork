from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    details_of_form = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")
    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})

    details_of_form['action'] = action
    details_of_form['method'] = method
    details_of_form['inputs'] = inputs
    return details_of_form

def vulnerable(response):
    # Simulate a vulnerable condition
    return "vulnerable" in response.content.decode().lower()

@app.route('/', methods=['GET', 'POST'])
def index():
    vulnerability_status = None
    is_vulnerable = False  # Initialize as False

    if request.method == 'POST':
        url = request.form['url']
        forms = get_forms(url)
        print(f"[+] Detected {len(forms)} forms on {url}.")
        
        for form in forms:
            details = form_details(form)
            for i in "\"'":
                data = {}
                for input_tag in details["inputs"]:
                    if input_tag["type"] == "hidden" or input_tag["value"]:
                        data[input_tag['name']] = input_tag["value"] + i
                    elif input_tag["type"] != "submit":
                        data[input_tag['name']] = f"test{i}"

                if details["method"] == "post":
                    res = s.post(url, data=data)
                elif details["method"] == "get":
                    res = s.get(url, params=data)
                if vulnerable(res):
                    vulnerability_status = f"SQL injection attack vulnerability in link: {url}"
                    is_vulnerable = True  # Set to True if vulnerability detected
                    break  # Exit the loop if vulnerability detected
                else:
                    vulnerability_status = "No SQL injection attack vulnerability detected"
                    is_vulnerable = False  # Set to False if no vulnerability detected

    return render_template('index.html', vulnerability_status=vulnerability_status, is_vulnerable=is_vulnerable)

if __name__ == '__main__':
    app.run(debug=True)
