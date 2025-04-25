from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def show_results():
    search_term = request.args.get('query', '')

    recommended_product = {
        'name': f"{search_term}",
        'price': '₹150',
        'description': f'Recommended product for "{search_term}"',
    }
    return recommended_product



if __name__ == "__main__":
    app.run(debug=True)
