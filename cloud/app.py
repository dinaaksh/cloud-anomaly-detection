from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mail import Mail, Message 
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mail import Mail, Message 
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from langchain_community.document_loaders import WebBaseLoader
import os
import sqlite3
from chain import chain

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

#add your information in the next blocks of code
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '<insert_email>'  
app.config['MAIL_PASSWORD'] = '<insert_password'  
app.config['MAIL_DEFAULT_SENDER'] = '<insert_email>'  

mail = Mail(app)
chain=chain()

AZURE_TENANT_ID = '<insert_tenant_id>'
AZURE_CLIENT_ID = '<insert_client_id>'
AZURE_CLIENT_SECRET = '<insert_client_secret>'
AZURE_SUBSCRIPTION_ID = '<insert_subscription_id>'
resource_id = "<insert_resource_id"
os.environ['USER_AGENT'] = 'MyFlaskApp/1.0'

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'main.db')
    return sqlite3.connect(db_path)

def send_email(anomalies_df):
    summary = chain.generate(anomalies_df['cpu_usage'] , anomalies_df['network_in'], anomalies_df['network_out'], anomalies_df['disk_read'] , anomalies_df['disk_write'] )
    msg = Message("Cloud Rocket has detected an anomaly in your system",
                  recipients=["palampur228@gmail.com"])  #can change to your recipients
    msg.body = f"An anomaly was detected in your Azure resources:\n{anomalies_df.to_string(index=False)}\n Remedial: {summary}"
    mail.send(msg)
    return "Email sent!"

def get_azure_client():
    credentials = ClientSecretCredential(
        tenant_id=AZURE_TENANT_ID,
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_CLIENT_SECRET
    )
    client = MonitorManagementClient(credentials, AZURE_SUBSCRIPTION_ID)
    return client

def fetch_azure_data():
    metric_names = [
        "Percentage CPU",
        "Network In",
        "Network Out",
        "Disk Read Operations/Sec",
        "Disk Write Operations/Sec"
    ]

    monitor_client = get_azure_client()
    metrics_dict = {}

    for metric_name in metric_names:
        metrics_data = monitor_client.metrics.list(
            resource_id,
            timespan='PT24H',  
            interval='PT30M',  
            metricnames=metric_name,
            aggregation='Average'
        )
        
        for metric in metrics_data.value:
            for timeseries in metric.timeseries:
                for data_point in timeseries.data:
                    timestamp = data_point.time_stamp
                    if timestamp not in metrics_dict:
                        metrics_dict[timestamp] = {"TimeStamp": timestamp}
                    
                    metrics_dict[timestamp][metric_name] = data_point.average

    df = pd.DataFrame(list(metrics_dict.values()))

    df.rename(columns={
        "Percentage CPU": "cpu_usage",
        "Network In": "network_in",
        "Network Out": "network_out",
        "Disk Read Operations/Sec": "disk_read",
        "Disk Write Operations/Sec": "disk_write"
    }, inplace=True)

    columns_order = ['TimeStamp', 'cpu_usage', 'network_in', 'network_out', 'disk_read', 'disk_write']
    df = df[columns_order]
    df.fillna(0, inplace=True)

    return df

def train_and_detect_anomalies(df):
    X = df[['cpu_usage', 'network_in', 'network_out', 'disk_read', 'disk_write']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    iso_forest = IsolationForest(contamination=0.01)
    iso_forest.fit(X_scaled)
    y_pred = iso_forest.predict(X_scaled)
    y_pred = np.where(y_pred == 1, 0, 1)
    anomalies_df = df[y_pred == 1]
    if not anomalies_df.empty:
        send_email(anomalies_df)      
    return df, anomalies_df


@app.route('/')
def home():
    return redirect(url_for('login_page'))  # Redirect to the login page

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    db.close()

    if user:
        session['username'] = username  # Save username in session
        return redirect(url_for('dashboard'))  # Redirect to dashboard on successful login
    else:
        return jsonify({'message': 'Invalid username or password'}), 401  # Failed login

@app.route('/register', methods=['GET', 'POST'])
def register_user():  
    if request.method == 'POST':
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM user WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            db.close()
            return jsonify({'message': 'User  already exists'}), 409 

        cursor.execute('INSERT INTO user (first_name, last_name, phone, email, username, password) VALUES (?, ?, ?, ?, ?, ?)',
                       (first_name, last_name, phone, email, username, password))
        db.commit()
        db.close()
        session['username'] = username
        return jsonify({'message': 'Registration successful'}), 201  
    else:
        return render_template('register.html')  

@app.route('/azure_credentials', methods=['POST'])
def save_azure_credentials():
    data = request.json
    username = session.get('username')
    tenant_id = data.get('Tenant_ID')
    AZURE_TENANT_ID=tenant_id
    client_id = data.get('Client_ID')
    AZURE_CLIENT_ID=client_id
    client_secret = data.get('Client_Secret')
    AZURE_CLIENT_SECRET=client_secret
    subscription_id = data.get('Subscription_ID')
    AZURE_SUBSCRIPTION_ID=subscription_id

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('INSERT INTO Metrics (username, Tenant_ID, Client_ID, Client_Secret, Subscription_ID) VALUES (?, ?, ?, ?, ?)',
                       (username, tenant_id, client_id, client_secret, subscription_id))
        db.commit()
        return jsonify({'message': 'Azure credentials saved successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Credentials for this user already exist'}), 409
    finally:
        db.close()


@app.route('/dashboard')
def dashboard():
    df = fetch_azure_data()
    df, anomalies = train_and_detect_anomalies(df)
    print(anomalies)
    return render_template('dashboard.html', anomalies=anomalies)

@app.route('/fetch-data')
def fetch_data():
    df = fetch_azure_data()
    df, anomalies = train_and_detect_anomalies(df)
    data = df.to_dict(orient='records')
    return jsonify(data)


@app.route('/login.html')
def login_page():
    return render_template('login.html')  

@app.route('/register.html')
def register_page():
    return render_template('register.html')  

@app.route('/azure_credentials.html')
def azure_credentials_1():
    return render_template('azure_credentials.html') 

if __name__ == '__main__':
    app.run(debug=True)