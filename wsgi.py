from app import create_app

# Create the application instance
application = create_app()
# For compatibility with both gunicorn and Flask
app = application

if __name__ == "__main__":
    app.run()