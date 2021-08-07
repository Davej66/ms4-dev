# MS4-FreelanceMeetups


Credits:
- Render to string with JsonResponse - BeryCZ https://stackoverflow.com/questions/64688157/django-render-json-response-html



## Tools
- [Django Secret Key Generator](https://miniwebtool.com/django-secret-key-generator/) for generating Django secret key to store in environment variables in Gitpod and Heroku


## Deployment

### Github
### Deploy to Production environment in Heroku
1. Navigate to Heroku dashboard and click 'create new app' from the dropdown option.
#### Provision a new Postgres database in production
2. Under the 'Resources' tab, provision a new Postgres database (select the 'hobby' plan when prompted).
3. On the CLI in your development environment, install the following modules:
`pip3 install dj_database_url` and `pip3 install psycopg2-binary` 
4. Add the modules to your dependencies file with: 
`pip3 freeze --local > requirements.txt`
5. In **settings.py**:
    a. Import the module `import dj_database_url`. 
    b. Find and copy the `DATABASE_URL` Config Var in Heroku by clicking 'settings' then 'Reveal Config Vars'.
    c. Configure the **DATABASES** settings with the value copied from Heroku: 
    `DATABASES = {
        'default': dj_database_url.parse('YOUR CONFIG VAR VALUE HERE')
     }`
6. With the new database connected, apply the outstanding migrations to the new database with `python3 manage.py migrate`.
7. Load development data into the new database with `python3 manage.py loaddata YOUR_APP_NAME`
8. Install **gunicorn** to act as web server - `pip3 install gunicorn`.
9. Add the modules to your dependencies file with: 
`pip3 freeze --local > requirements.txt`
10. Create a new **Procfile** in the root directory and add instructions to start a new web Dyno on Heroku: `web: gunicorn YOUR-DJANGO-PROJECT.wsgi:application`
11. Log into Heroku with `heroku login -i`
12. Disable Heroku from collecting static files by entering this into the CLI: `heroku config:set DISABLE_COLLECTSTATIC=1 --app YOUR-HEROKU-APP-NAME`
13. Add Heroku to the 'ALLOWED_HOSTS' list in **settings.py**: `ALLOWED_HOSTS = ['YOUR-HEROKU-APP-NAME.herokuapp.com']`
14. After committing and pushing changes to GitHub, connect your GitHub repo to Heroku with `heroku git:remote -a YOUR-HEROKU-APP-NAME` and push to the Heroku deployment with `git push heroku main`.
15. Setup auto-deploy from GitHub in Heroku by clicking on the 'Deploy' tab, select 'GitHub', search for your respository, click 'connect' and then 'Enable Automatic Deploys'.
16. Generate a new Django SECRET_KEY using a key generator and add to Heroku - select 'settings', 'Reveal Config Vars' and add a new key 'SECRET_KEY' and value as the generated key. 

#### Setting up AWS to host static files and media
1. Signup for a free [AWS account](https://aws.amazon.com/) or login.
2. In the services searchbar at the top, type and select 'S3'.
3. Create a new 'bucket'. Use your Heroku app name to ensure it is clearly identifiable.
4. Select the region closest to you, uncheck the 'Block all public access' box and check the acknowledgement box at the bottom. Finally select 'create bucket'.
5. Configure the new bucket - click into the bucket and select the 'Properties' tab, and 'Static website hosting' option to create a new endpoint (enter default values into the prompts and click save).
6. Under the 'Permissions' tab, update the CORS configuration, by adding the below snippet: `[
  {
      "AllowedHeaders": [
          "Authorization"
      ],
      "AllowedMethods": [
          "GET"
      ],
      "AllowedOrigins": [
          "*"
      ],
      "ExposeHeaders": []
  }
]`
7. Under 'Bucket Policy' select 'Policy Generator' at the bottom of the editor to create a new policy for the bucket:
    a. Select 'S3 Bucket Policy' as the type
    b. Use '*' to allow all principals
    c. Select 'Get Object' as the **action**
    d. Paste in the **ARN** found at the top of the 'Bucket Policy Editor' tab. 
    e. Click add policy, then 'generate policy', finally copy and paste the generated policy into the policy editor on the previous page.
    f. Before saving changes, allow all resources by adding `/*` to the end of the 'Resources' value. e.g `"Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"`
8. Finally, set the access control to public for this bucket by clicking 'Access Control List', then selecting 'Everyone (and list objects)' under 'Public Access'.


Create a new user and to access the bucket under 'IAM' management 
1. Back in the services menu, select 'IAM'
2. Under 'User Groups' create a new group with the name of the Django Project.
3. Create a new group policy by selecting 'Polices' on the left pane, and 'Create Policy'
    a. Select 'JSON' tab, and click 'Import managed policy'
    b. Search for 'S3' and select 'S3 Full Access Policy'
    c. To restrict access to the bucket created in the previous step, replace the 'Resource' value with the 'ARN' value created in the previous step.
    d. Click 'Next: Tags' and again to 'Review Policy', provide a name and description then click 'Create Policy'.
4. Attach the policy to the group by selecting the group name under 'User Groups', select 'Attach Policy' and select the newly created policy.
5. Under 'Users' create a new user to add to the group: 
    a. Create a user with the name of the project, and append `-staticfiles-user` to identify the user type. 
    b. Select 'Programmatic Access', under 'Permissions' on the next page, select the group previously created. 
    c. Click through the next pages and 'Create User'.
    d. **IMPORTANT**: On the final step, download the .csv to access the users secret keys, required to authenticate with the Django Project


### Libraries
- Multiselect JS Library by [sa-si-dev](https://github.com/sa-si-dev/virtual-select)

## Credits

### Images
- Photography Example Event Image by [ATC Comm Photo](https://www.pexels.com/@atccommphoto?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from Pexels
- Example Attendee Image by [Andrea Piacquadio](https://www.pexels.com/@olly?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from Pexels
- Example Attendee Image by [Justin Sheifer](https://www.pexels.com/@justin-shaifer-501272?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from Pexels
- Example Attendee Image by [Daniel Xavier](https://www.pexels.com/@danxavier?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from Pexels
- Example Attendee Image by [Hamed Gharaee](https://www.pexels.com/@hamed-gharaee-1120343?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from Pexels
- London skyline on homepage by [Pixabay](https://www.pexels.com/@pixabay) on Pexels

### Tutorials and Guides
- [Markdown cheatsheet](https://www.markdownguide.org/basic-syntax/)
- [How to get a footer to stick to the bottom of the page](https://dev.to/nehalahmadkhan/how-to-make-footer-stick-to-bottom-of-web-page-3i14)
- [How to set nav link to active based on url - Siddharth Pant's answer in this StackOverflow thread](https://stackoverflow.com/questions/46617375/how-do-i-show-an-active-link-in-a-django-navigation-bar-dropdown-list)
- [How to preview image before upload using jQuery - answer from Suresh Pattu in this StackOverflow thread](https://stackoverflow.com/questions/18694437/how-to-preview-image-before-uploading-in-jquery/19649483)
- [Syntax to center any image to the center of it's parent div - Answer provided by 'hyounis' in this StackOverflow thread](https://stackoverflow.com/questions/14562457/center-oversized-image-in-div)
- [Syntax support to serialize Django QuerySet to JSON for use in template, answer provided by 'Yannic Hamann' in this StackOverflow thread](https://stackoverflow.com/questions/47204188/is-there-any-way-convert-django-model-queryset-to-json-or-json-string-in-templat)
- [How to load fonts without render blocking on page load guide by CSS-Tricks](https://css-tricks.com/how-to-load-fonts-in-a-way-that-fights-fout-and-makes-lighthouse-happy/)
- Dropdown menu on hover guided by StackOverflow answer by Aram Mkrchtyan in [this thread](https://stackoverflow.com/questions/8775860/jquery-drop-down-hover-menu)