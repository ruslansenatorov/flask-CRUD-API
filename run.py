from flask import Flask
from auth.routes import authRoutes
from infrastructure.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def root():
    return "Built by sortminder"

authRoutes(app)

if __name__ == "__main__":
    app.run(debug=True)