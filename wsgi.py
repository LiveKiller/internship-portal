from application import app

# Create the application instance
application = app
# For compatibility with both gunicorn and Flask
app = application

if __name__ == "__main__":
    app.run()