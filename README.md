# My PROJECT TITLE : Set up email handling and automate deployment.
    #### Video Demo:  <URL HERE>
    #### Description:Configure my website so that contact messages are sent to my email address.
**Reason for Choosing This Topic**

I had originally set out to create a personal website by launching a WordPress instance on AWS Lightsail, but I made no real progress over the course of several years. However, after taking the CS50x course, I was able to complete and submit the "Homepage" assignment from Week 8 within just three months.

As I was self-taught and relied solely on generative AI for guidance, I failed to grasp the standard best practices for personal-level development—such as customizing the GitHub Codespaces environment configuration file (`.devcontainer/`) to automatically launch a PostgreSQL container via Docker Compose alongside the Python environment.

I ended up switching to a Django instance simply because ChatGPT recommended it.
However, AWS is an environment designed for corporate IT departments; it involves excessive complexity, with many features that are unnecessary for an individual user. Ideally, I should have developed the site using the standard method mentioned above and connected to an external cloud database only if the need arose.

Had standard development practices been adopted from the start, all other resources could have been covered by the cloud provider's free tier, thereby avoiding costs other than the domain fee. Although the order of operations was reversed, I successfully launched the website. Amazon SES is effectively free (aside from data transfer charges).

There are still tasks to address regarding my webpage, such as verifying the mobile view and fine-tuning the styling. I also anticipate the need to adapt to future specification changes in the software and services I use. I have decided to make the reconstruction of just the "Contact" page—along with the creation of a new GitHub repository for its operation—the theme of my CS50p project. Once this project is complete, I will determine the setup for future development and operations.

To keep this README.md file concise, matters not directly related to the project—such as AI errors, my own mistakes, or misunderstandings—will be documented in References.md.
##### **References: Note (01)  Generative AI can be stubborn and inflexible**
##### **References: Note (02)　Refining the styling is a task for the future**
Gemini's presentation
##### **References: Note (03)  Segmentation of test procedures**

#### **[1]-a  Build upon the work done in CS50x.  **
#### **[1]-a-1  Complete the email sending and receiving functionality for the nearly finished web page**
The first step is to migrate the email sending and receiving functions of the contact page—which are already in live operation—to meet the requirements of this project; however, as part of the process, I will first outline how the currently operational environment was established.


Here is the completed webpage.　<https://michealfamily.com/contact/>

#### **[1]-a-2 Email receiving settings for production deployment**

ChatGPT's presentation
```
views.py
   Refer to
   cs50p/project/Virtual Test/views.py
```
```
ms_contact.html
   Refer to
   cs50p/project/Virtual Test/ms_contact.html
```
Other file.
```
requirements.txt
   Django>=4.2,<5.0
   gunicorn
   python-dotenv
   boto3
   requests
   psycopg2-binary

.env
   # Django基本設定
   DJANGO_SECRET_KEY='-----BEGIN RSA PRIVATE KEY-----
   ．．．
   -----END RSA PRIVATE KEY-----'
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=michealfamily.com,www.michealfamily.com,52.69.81.143,web

   # CSRF設定
   DJANGO_CSRF_TRUSTED_ORIGINS=https://michealfamily.com,https://www.michealfamily.com
   # SSLリダイレクトを有効化
   DJANGO_SECURE_SSL_REDIRECT=True
   EMAIL_MODE=ses
   EMAIL_HOST=smtp.mail.ap-northeast-1.amazonaws.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=...
   EMAIL_HOST_PASSWORD=...

   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   AWS_SES_REGION=ap-northeast-1
   AWS_SES_FROM=h.manabu3742@gmail.com
   # データベース接続情報
   DATABASE_HOST=db
   DATABASE_PORT=5432
   POSTGRES_DB=django_db
   POSTGRES_USER=django_user
   POSTGRES_PASSWORD=...

urls.py
   from django.contrib import admin
   from django.urls import path, include
   from django.conf import settings
   from django.views.static import serve
   from homepage.views import contact_view, contact_send

   urlpatterns = [
      path('admin/', admin.site.urls),
      path('', include('homepage.urls')),
      path('myapp/', include('myapp.urls')),
      path('contact/', contact_view, name='contact'),
      path('contact/send/', contact_send, name='contact_send'),
   ]

   if not settings.DEBUG and settings.IS_LOCAL:
      urlpatterns += [
         path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
      ]


settings.py
   Refer to
   cs50p/project/Virtual Test/settings.py
...
   Creating the SES API Sending Module (via ChatGPT)
...
ses.py
   import boto3
   from botocore.exceptions import ClientError
   from django.conf import settings

   lient = boto3.client(
      "ses",
      region_name=settings.AWS_SES_REGION,
      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
   )

   def send_mail(subject, body, recipient):

      try:
         response = client.send_email(
            Source=settings.AWS_SES_FROM,
            ReturnPath=settings.AWS_SES_FROM,
            Destination={
                "ToAddresses": [recipient],
            },
            Message={
               "Subject": {
                  "Data": subject,
                  "Charset": "UTF-8",
               },
               "Body": {
                  "Text": {
                     "Data": body,
                     "Charset": "UTF-8",
                  }
               },
            },
         )

        return {
            "success": True,
            "message_id": response["MessageId"],
        }

      except ClientError as e:
         return {
            "success": False,
            "error": e.response["Error"]["Message"],
         }

```
#### **[1]-a-4 Amazon SES Configuration**
Gemini suggested using Gmail's SMTP, but a warning regarding outdated security specifications prompted the decision to use the paid Amazon SES service. Eight issues arose during the configuration process.

1. Amazon SES New User Registration

   Verify the contact email address (xxxx@gmail.com). This step was completed quickly.

2. Create an IAM user specifically for the SES API

   Create a custom policy allowing only `ses:SendEmail` and `ses:SendRawEmail`
```
   Json via ChatGPT
   {
      "Version": "2012-10-17",
      "Statement": [
         {
            "Effect": "Allow",
            "Action": [
               "ses:SendEmail",
               "ses:SendRawEmail"
            ],
            "Resource": "*"
         }
      ]
   }
```

3. Obtain the Access Key ID and Secret Access Key from the "Security credentials" tab
   You must record the displayed information immediately, as it will not be shown again.

4. Registering an Email Address-Type Identity

   Sending a test email to the address (xxxx@gmail.com) automatically registers the identity and completes the process.

5. Registering a Domain-Type Identity

   Three CNAME records are generated. While I am unsure of the procedure if the domain was purchased elsewhere, I used Route 53, so the records were generated there automatically. I then waited for the DKIM verification process to complete. In reality, I had to update the NS records for the registered domain by removing the existing entries and adding the four name server names displayed in the Route 53 hosted zone. Verification did not occur even after waiting 72 hours. Although Gemini didn't have the answer, my past experience struggling with WordPress a few years ago proved helpful. It didn't happen in minutes, but verification was completed overnight.

6. Requesting Production Access

   Approval usually takes within 24 hours, but I received an email requesting additional information. The method for submitting this information was unclear. More than a week wasted due to unnecessary waiting.I haven't received approval for the production application yet.

##### **References: Note (04)** Attempted to skip approval and move on

7. I added a Type A record to the Route 53 hosted zone, obtained approval for production access, and proceeded to the next step.

##### **References: Note (05)**  Reworking the task
##### **References: Note (06)**  Adjusting the Dockerfile and docker-compose configurations.
#### **[1]-a-5 The unnecessary switch to the API method via IAM**
I decided to switch from the simple SMTP method to the API method via IAM within Amazon SES. In hindsight, this appears to have been a completely unnecessary undertaking; however, having completed the switch to the latter method, I am documenting the cause of the initial issue that prompted the change.

During the initial stages of investigating the cause, I (temporarily) changed the following line in the Dockerfile:
```
Before change
   RUN pip install --no-cache-dir -r requirements.txt
After change
　 RUN --network=host pip install --no-cache-dir -r requirements.txt
```
As a side note regarding an issue with outbound communication from the Docker bridge—where DNS resolution or network routing conflicted with AWS—Gemini suggested setting `network=host` in `deploy-docs.yml`. When I pointed out that this violated the principle of separating development and operational environments, it agreed, but failed to identify the root cause, let alone provide a solution. ChatGPT fared no better. Ultimately, we settled on using `network=host` only for the Docker Compose build process.
```
deploy-docs.yml
   ...
   services:
   web:
    build:
      context: /opt/bitnami/projects/my-django-app
      network: host
   ...
```
In reality, the issue stemmed from a `network=host` setting within the Dockerfile itself—something that could never have been discovered by investigating Docker Compose configurations or internet connectivity settings. Yet, the generative AI had correctly identified the cause. However, before I could implement that fix, the true culprit came to light: simply reverting a single line in the Dockerfile resolved everything. The `network=host` setting for the build in `deploy-docs.yml` was no longer necessary.

Amidst this ordeal, I refactored the functionality within `deploy-docs.yml`. Details regarding "Improvements to deployment automation" are provided later in section [1]-b-2.


#### **[1]-a-6 Email sending/receiving test on the staging server**

A system mechanism (notification setting) to automatically detect errors where emails fail to reach my address (i.e., bounce)
```

```

### **[1]-b Automation of Deployment and  the Final Development and Operational Environment for Local, Staging, and Production**
#### **[1]-b-1 Solution for broken display in production only (styles not loaded, images not displayed)**
Besides cookies, speed improvements are achieved everywhere through process optimization (following past practices) (Docker, Django, Apache), and simply modifying the code or configuration is often ineffective. Furthermore, even if it works locally, the display may break in the server environment, requiring modifications to settings (such as .env, *-vhost.conf and Complete reset and restart) to handle the differences between local and online environments.

#### **[1]-b-2 Creating deploy-docs.yml**

Deployment involves re-executing a series of processes in addition to GitHub Pull.

The deployment process will be configured to start from a local environment, via StagingSSH connection, or GitHub Actions, allowing users to choose between deploying only the first half (Staging), only the second half (Production), or both, depending on the situation.

The following is the code I finally arrived at.
Decoupling GitHub Actions workflows from deployment functions.
```
deploy-docs.yml
    name: Deploy Documentation / App

    on:
        push:
            branches:
            - main

            paths-ignore:
            - 'backups/**'
        workflow_dispatch:
            inputs:
                target_env:
                    description: 'デプロイ対象を選択してください'
                    required: true
                    default: 'all'
                    type: choice
                    options:
                        - 'all'
                        - 'staging'
                        - 'production'

    jobs:
        deploy-staging:
            environment: Staging
            runs-on: ubuntu-latest
            if: |
                (github.event_name == 'workflow_dispatch' && (inputs.target_env == 'all' || inputs.target_env == 'staging')) ||
                (github.event_name == 'push' && !contains(github.event.head_commit.message, '[skip staging]'))
            steps:
                - name: Deploy to Server via SSH
                  uses: appleboy/ssh-action@master
                  with:
                    host: ${{ vars.SERVER_HOST }}
                    username: ${{ vars.SERVER_USER }}
                    key: ${{ secrets.SSH_PRIVATE_KEY2 }}
                    script: |
                        cd ${{ vars.REMOTE_PATH }}
                        echo "===== Check Server Working Tree ====="
                        if [[ -n "$(git status --porcelain)" ]]; then
                            echo "ERROR: Unexpected local changes detected."
                            git status --short
                            echo "===== Deployment Aborted ====="
                            exit 1
                        fi
                        echo "===== Update Repository ====="
                        git pull origin ${{ github.ref_name }}
                        echo "===== Execute Deploy Script ====="
                        ./scripts/deploy.sh

        deploy-production:
            environment: Production
            runs-on: ubuntu-latest
            if: |
                (github.event_name == 'workflow_dispatch' && (inputs.target_env == 'all' || inputs.target_env == 'production')) ||
                (github.event_name == 'push' && !contains(github.event.head_commit.message, '[only staging]'))
            steps:
              - name: Deploy to Production Server via SSH
                uses: appleboy/ssh-action@master
                with:
                    host: ${{ vars.SERVER_HOST }}
                    username: ${{ vars.SERVER_USER }}
                    key: ${{ secrets.SSH_PRIVATE_KEY1 }}
                    script: |
                        cd ${{ vars.REMOTE_PATH }}
                        echo "===== Check Server Working Tree ====="
                        if [[ -n "$(git status --porcelain)" ]]; then
                            echo "ERROR: Unexpected local changes detected."
                            git status --short
                            echo "===== Deployment Aborted ====="
                            exit 1
                        fi
                        echo "===== Update Repository ====="
                        git pull origin ${{ github.ref_name }}
                        echo "===== Execute Deploy Script ====="
                        ./scripts/deploy.sh
```
```
scripts/deploy.sh
   ##### Common Deploy Script

   echo "============================================================="
   set -Eeuo pipefail

    echo "===== Deploy Start ====="

    echo "===== STEP 1 : Permission ====="

    sudo chown -R bitnami:bitnami .

    echo "===== STEP 2 : Build  containers ====="

    docker compose build

    echo "===== STEP 3 : Start containers ====="

    docker compose up -d

    echo "===== STEP 4 : Wait for web container ====="
    docker compose ps

    echo "===== STEP 5 : Apply database migrations ====="

    docker compose exec -T web python manage.py migrate --noinput

    echo "===== STEP 6 : Collect static files ====="

    docker compose exec -T web python manage.py collectstatic --noinput

    echo "===== STEP 7 : Restart Apache ====="

    sudo /opt/bitnami/ctlscript.sh restart apache


    echo " Deploy Finished Successfully"
    echo "=============================================================="

```
#### **[1]-c Converting the Contact Page **
#### **[1]-b-1 The first step in the conversion process**
 It is to separate the "HTML display section" from the "Python processing section" within "ms_contact.html"
```
   Framework of ms_contact.html
      Django processing
      CSS         (<style>...</style>)
      HTML body   (<main>...</main>)
      JavaScript  (<script>...</script>)

```
 Disassemble it into three parts. Divide the roles so that finally, execution starts from `project.py`.
```
   ① HTML:contact.html
   ② CSS:contact.css
         Note that the styles common to all pages will be used as-is.:style.css
   ③ JavaScript:contact.json,language.js
```
Furthermore, regarding the data imported into `contact.json`, retain only the data itself and move the browser-side processing to `contact.js` and `language.js`.

Move form submission to the Python function `send_contact()`.

At this stage, the basic Python structure looks like this:
```
   project.py
      import json

      def main():
         load_contact_data()
         start_web_app()


      def load_contact_data():
         """Load contact.json"""
         pass


      def start_web_app():
         """Launch the web page"""
         pass


      def send_contact():
         """Process the contact form"""
         pass


      def switch_language():
         """Switch the display language"""
         pass


      if __name__ == "__main__":
         main()
```
#### **[1]-b-2 Specification change:**
1. Use Flask to launch the web page.
2. The header menu will not be used this time.

Move the functionality currently in `base.html` to a `.js` file.
```
   base.html
      Refer to
      cs50p/project/Virtual Test/base.html
```
･ Update the form submission JavaScript to align with the Flask implementation.

･ While Flask allows passing `contact_data` to the HTML template, JavaScript cannot directly access Python variables. ⇒ Change in processing flow.
```
   Shift `contact.js` from "holding" `contactData` and "using" it
   To `contactData` flow Python → HTML → JavaScript
   Place the `contact.html` loading point immediately before the `</body>` tag.
```
･ Integrate the open-source CSS framework Bootstrap, custom CSS, and fonts into `contact.html`, and add a footer and a language-switching button.

･ Move the "language switching logic" to `language.js`.

#### **[1]-b-3 Additional integration: Connect `send_contact()` to the actual Amazon SES sending process**
･ Integrate  from `ses.py` and the `contact_send` function of `views.py` to project.py.
･ Verify the data sent by `contact.js` against the data expected by `send_contact()`.

**This completes the coding for sending emails from the web page using Python, HTML, and JavaScript.**

Next, to verify the operation of each step—`contact.js` → `/contact_send` → `send_contact()` → actual Amazon SES transmission—write `test_project.py` using `pytest` to test each stage.
### **[1]-c Debugging functions in project.py**
#### **[1]-c-1 Test items**
```
load_contact_data():
   1. Loading contact.json
start_web_app(contact_data):
   2. / → Displaying contact.html
   3. /contact_send → Calling send_contact()
send_contact():
   4. Checking required fields
   5. send_contact() → Passing data to send_mail()
send_mail(subject, body, recipient):
   6. send_mail() → Calling boto3 SES client.send_email()
   7. Response upon SES success
   8. Response upon SES failure
switch_language(contact_data):
   9. /switch_language → Switching between Japanese and English
```
ChatGPT responded immediately when I simply instructed it to create test_project.py for debugging purposes.

test_project.py created by ChatGPT
```
   Refer to
   cs50p/project/Virtual Test/ezam_projectVersion1.py

```
I had anticipated that debugging efficiency would improve by mutually correcting errors in both sets of code; at this stage, I had ChatGPT double-check the code I had entered into Visual Studio Code for CS50. It found a few errors, but after fixing them, test_project.py worked perfectly, and I was also able to correct a few JSON syntax errors in project.py.

#### **[1]-c-2 Executing pip install -r requirements.txt**
```
Refer to requirements.txt
```
#### **[1]-c-3 Executing `pytest -v test_project.py`**
In the first test, an amazing 8 out of 9 passed.
```
platform linux -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3.13 cachedir: .pytest_cache rootdir: /workspaces/86801581/cs50p/project plugins: typeguard-4.6.0 collected 9 items test_project.py::test_load_contact_data FAILED [ 11%] test_project.py::test_start_web_app_page PASSED [ 22%] test_project.py::test_send_contact_success PASSED [ 33%] test_project.py::test_send_contact_fields_missing PASSED [ 44%] test_project.py::test_send_mail_error PASSED [ 55%] test_project.py::test_send_mail_success PASSED [ 66%] test_project.py::test_send_mail_client_error PASSED [ 77%] test_project.py::test_switch_language_ja PASSED [ 88%] test_project.py::test_switch_language_invalid PASSED [100%]
================== 1 failed, 8 passed in 0.81s
```
In JSON, backticks (``) cannot be used to enclose strings (double quotes ("") must be used), and line breaks within strings must be represented as (\n). Fixing these two issues completed the preliminary testing.

#### **[1]-c-4 browser Test items**
The next step is to add E2E tests for final verification using a web browser.
```
   1. Form display test in the browser
   2. Japanese/English language toggle test
   3. Form input test
   4. Submit button functionality test
   5. Integration test covering the flow up to "/contact_send"
```
Minor adjustments required for `project.py` (data retrieval from `contact.json`) and `contact.js` (payload).

Created `test_browser.py` (via ChatGPT).
```
   Refer to
   test_browser.py file
```
Remove redundant browser tests from `test_project.py`.
```
   Refer to
   test_project.py file
```
Prepare for using Playwright
```
   python -m playwright install chromium
   python -m playwright install-deps chromium
```
Final test resultscs 50p/project/ $ pytest -v
```
============= test session starts =============
platform linux -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3.13
cachedir: .pytest_cache
rootdir: /workspaces/86801581/cs50p/project
plugins: base-url-2.1.0, playwright-0.9.0, typeguard-4.6.0
collected 10 items

test_browser.py::test_contact_send_integration PASSED [ 10%]
test_project .py::test_load_contact_data PASSED [ 20%]
test_project .py::test_start_web_app_page PASSED [ 30%]
test_project .py::test_send_contact_success PASSED [ 40%]
test_project .py::test_send_contact_fields_missing PASSED [ 50%]
test_project .py::test_send_mail_error PASSED [ 60%]
test_project .py::test_send_mail_real PASSED [ 70%]
test_project .py::test_send_mail_client_error PASSED [ 80%]
test_project .py::test_switch_language_ja PASSED [ 90%]
test_project .py::test_switch_language_invalid PASSED [100%]

============== 10 passed in 4.27s =============
```
### **[1]-d Consideration and implementation regarding the scope and nature of continued work**
#### **[1]-d-1 Evaluation**
As mentioned earlier, the web page—along with its development and operations environment—is already up and running on AWS Lightsail. I do not feel it is necessary to convert the system to use FRSK instead of Django  (as I did here) simply to save a negligible amount of money. However, I do believe that building a GitHub-based development and operations environment—independent of AWS—is a valuable exercise for acquiring knowledge, even without the specific "Visual Studio Code for CS50" setup.

Regarding "Visual Studio Code for CS50," I wonder if I can continue using it after completing the course, considering the rules governing its global availability for anyone to use. Given this, setting up a personal development and operational environment seems like a necessary step.

A personal GitHub Free account includes a monthly allowance for Codespaces—currently 120 hours of compute time and 15 GB-months of storage. However, this does not serve as a substitute for a dedicated, always-on server for general users; it cannot host a Flask application publicly on the internet 24/7. I therefore asked a generative AI to compare using Render against AWS Lightsail; the conclusion was that Render offers no distinct advantage, and certainly isn't worth the effort of a system migration.
#### **[1]-d-2 Proposed structure for the new repository**
No PostgreSQL implementation
```
   python-docker-project/
   ├── Flask
   │　　　└── project.py
   ├── requirements.txt
   ├── Dockerfile
   ├── compose.yaml
   ├── .gitignore
   ├──　Web
   │     ├── contact.html
   │     └──static
   │           ├── contact.css
   │           ├── style.css
   │           ├── language.js
   │           ├── contact.js
   │           └── contact.json
   ├── tests/
   │   ├── test_project.py
   │   └── test_browser.py
   ├── Python packages
   │     └── requirements.txt
   ├── Secret
   │      └── .env
   └── .github/
       └── workflows/
            └── tests.yml
```
Work tasks

Docker Desktop already installed and in use.

   1.Launch the Flask app using local Docker Desktop.

   2.Edit code via VS Code Desktop.

   3.Launch PostgreSQL using Docker as needed.

   4.Run tests using pytest and Playwright.

   5.Automate testing with GitHub Actions.
#### **[1]-d-3 Download from the CS50p Codespace to the local project.**
Folder Name : python-docker-project

When downloading the folder, GitHub-related folders and files are automatically generated

**Create a new, empty repository on GitHub**

repository Name : python-docker-project

**Connect the two**

Modify the `.gitignore` file which currently contains only `.env`.

via ChatGPT
```
   # Environment variables / secrets
   .env
   .env.*
   !.env.example

   # Python
   __pycache__/
   *.py[cod]
   *.pyo
   .pytest_cache/
   .mypy_cache/

   # Virtual environments
   .venv/
   venv/
   env/

   # VS Code
   .vscode/

   # OS
   .DS_Store
   Thumbs.db
```
Place the local folder under Git version control.

Using the VS Code terminal locally
```
   PS C:\projects\python-docker-project> git init
      Initialized empty Git repository in
      C:/projects/python-docker-project/.git/
```
(Same as above)
```
   git add .
   git commit -m "Initial commit"
```
On the repository page, you will see a URL like `https://github.com/your-username/python-docker-project.git`; copy your username

(Same as above)
```
   git remote add origin https://github.com
   /your-username/python-docker-project.git

   git remote -v
      origin
      Honda-Manabu/python-docker-project.git (fetch)
      origin
      Honda-Manabu/python-docker-project.git (push)

   git push -u origin main
      Enumerating objects: 17, done.
      Counting objects: 100% (17/17), done.
      Delta compression using up to 12 threads
      Compressing objects: 100% (17/17), done.
      Writing objects: 100% (17/17), 23.73 KiB | 2.97 MiB/s, done.
      Total 17 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0) remote: Resolving deltas: 100% (1/1), done.
      To Honda-Manabu/python-docker-project.git *
      [new branch] main -> main
      branch 'main' set up to track 'origin/main'.
```
On the repository page, verify the initial commit.
#### **[1]-d-4 Create a Dockerfile.**
Docker Desktop works even without creating an account or logging in after installation. You are all set if the "Engine running" indicator in the bottom-left corner is green.

**Check the Flask startup section in `project.py` and modify it for Docker.**
```
   app.run(debug=True)
      ↓
   app.run(host="0.0.0.0", port=5000, debug=True)

   test_project.py
   def fake_run(self, debug=True):
      ↓
   def fake_run(self, host="127.0.0.1", port=5000, debug=True):
```
Install `pytest` in my local Windows environment and run the tests.
```
   python -m pytest -v test_project.py
      9 passed in 1.35s ==
```
**Dockerfile** via ChatGPT
```
   FROM python:3.13-slim

   WORKDIR /app

   COPY requirements.txt .

   RUN pip install --no-cache-dir -r requirements.txt

   COPY project.py .
   COPY contact.html .
   COPY static/ ./static/

   EXPOSE 5000

   CMD ["python", "project.py"]
```
**Build the Docker image.**
```
   PS C:\projects\python-docker-project>
      docker build -t flask-contact-app .
```
A screenshot from Docker Desktop obtained by clicking the URL generated upon a successful build

![screenshot of Docker Desktop](images/Docker-Desktop-screenshot-1.png)
(Same as above:Using the VS Code terminal PowerShell)
```
   docker run --name flask-contact-container -p 5000:5000 flask-contact-app
      * Serving Flask app 'project'
      * Debug mode: on
      WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
      * Running on all addresses (0.0.0.0)
      * Running on http://127.0.0.1:5000
      * Running on http://172.17.0.2:5000
      Press CTRL+C to quit
      * Restarting with stat
      * Debugger is active!
      * Debugger PIN: 488-037-849
```
With the container running, visit `http://localhost:5000` in your browser to verify.
#### **[1]-d-5 Use AWS SES from within Docker.**
**Create a .dockerignore file and securely pass environment variables.**
```
   .dockerignore
      .env
      .git
      __pycache__
      .pytest_cache
```
Rebuild the Docker image.

PowerShell
```
   PS C:\projects\python-docker-project>(The rest is the same.)
   docker ps -a
      ...
      flask-contact-container
   docker stop flask-contact-container
      flask-contact-container
   docker rm flask-contact-container
      flask-contact-container
   docker build -t flask-contact-app .
```
Verify success (same as the previous step
 'Build the Docker image.')
Verify the output 'http://127.0.0.1:5000'
```
Stop and start the Flask container
   Ctrl + C

   docker start <container name>
```
Github push
```
   git add .
   git commit -m "Commit name"
   git push origin main
      Enumerating objects: 8, done.
      Counting objects: 100% (8/8), done.
      Delta compression using up to 12 threads
      Compressing objects: 100% (5/5), done.
      Writing objects: 100% (6/6), 2.58 KiB | 1.29 MiB/s, done.
      Total 6 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0) remote:
      Resolving deltas: 100% (2/2), completed with 2 local objects.
      To Honda-Manabu/python-docker-project.git
      5ce58c9..3148e7f main -> main
```
Check the results on the GitHub page
#### **[1]-d-6 Set up a test environment using GitHub Actions**
Set up a Python environment and automatically run pytest using GitHub Actions.

Create a `.github/workflows/tests.yml` file within my local project.
```
   tests.yml via ChatGPT

   name: Python tests

   on:
      push:
      branches: [ "main" ]
   pull_request:
      branches: [ "main" ]

   jobs:
      test:
         runs-on: ubuntu-latest

         steps:
           - name: Checkout repository
             uses: actions/checkout@v4

           - name: Set up Python
             uses: actions/setup-python@v5
             with:
               python-version: "3.13"

           - name: Install dependencies
             run: |
               python -m pip install --upgrade pip
               pip install -r requirements.txt

           - name: Install Playwright browsers
             run: playwright install chromium

           - name: Run tests
             run: pytest -v

```
Execute git add, commit, push

Although I encountered an issue with the GitHub UI not updating immediately, the process completed successfully.
### **[1]-e Closing with a look at future prospects.**
This concludes the requirements for the CS50P project. Furthermore, for the maintenance and operation of a personal webpage, utilizing the free tier of a database service like PostgreSQL on Render would be more than sufficient. I have already established a Django Docker environment; considering factors such as continuous operation and future scalability—including potential community use—I have determined that there is no advantage to replacing my existing Django setup on AWS Lightsail with a Flask-based setup on a platform like Render. Therefore, I am concluding the project here.
