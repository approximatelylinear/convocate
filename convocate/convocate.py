# -*- coding: utf-8 -*-

"""Main module."""

from flask import Flask, render_template
import connexion

app_name = __name__.split('.')[0]
app = connexion.App(app_name, specification_dir="./")
print(app.root_path)

# app.config['MODEL_DATA_DIR'] = os.path.dirname(
#     os.path.join(os.path.abspath(__file__, 'data')))
#
# training_data = load_data('data/examples/rasa/demo-rasa.json')



app.add_api('swagger.yml')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
