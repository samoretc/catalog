This is a web application catalog. It uses flask and SQLAlchemy for the backend and bootstrap for the front end. Flask version 0.9 must be used. The easiest way to install this is to install pip and run the command 'pip install flask==0.9'. 

Users can log on to the web application via google plus to add sports items. In order to set this up on your envinronment, you will need to create an app engine project on the google developer's console, and then replace client_secret.json with the client_secret for your app.   

Additionally, a database must be created and populated with data. To create the database, run the database_setup.py file. Next, run the the populate.py file to populate the database with several categories and items. 

Finally, run the project.py to start the web server locally. If you visit localhost:5000, you should be able to see the web app, log on via google plus, and add, edit, and delete items!

There are two public request that return data in JSON format. The first public request is at /category/all which will return all of the categories and their IDs in JSON format. The second public request is at /category/<int:category_id>/items/JSON, which will return all relevant information about the item, including the item name and item ID, as well as the category ID for which the item belongs and the user ID of the user who created the item. 