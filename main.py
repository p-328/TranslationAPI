import translators as ts
from flask import Flask, jsonify, request
from flask_cors import CORS


desc_split = '----------------------------------------------------------------'
def loadLangs():
  # Reading in compat.txt as a file
  with open("compat.txt", "r") as f:
    # trim delimiters and split each line into language and language mapping
    lines = [line.strip().split() for line in f.readlines()]
    m = {line[0]: line[1] for line in lines}
    # accounting for capital letters
    for key, value in m.copy().items():
      m[key.capitalize()] = value
    # accounting for abbreviations
    for _, value in m.copy().items():
      m[value] = value

    return m

lang_maps = loadLangs()

app = Flask(__name__)
# allows for CORS if front-end uses this API (needed)
CORS(app)

@app.route('/', methods=['GET'])
def index():
  # Load route names and their descriptions
  with open("routes.txt", "r") as routes:
    # Trim delimiters
    paths = [route.strip() for route in routes.readlines()]
    with open("descriptions.txt", "r") as descs:
      description_texts = descs.read().split(desc_split)
    # Getting rid of routes with missing fields to make arrays zippable
    if len(paths) < len(description_texts):
      while len(description_texts) != len(paths):
        description_texts.pop()
    else:
      while len(paths) != len(description_texts):
        paths.pop()
    # strip delimiters and zip arrays together
    pairs = zip(paths, [text.strip() for text in description_texts])
  # Return JSON of documentation for this API.
  return jsonify({"message": "Hello!", "currentRoutes": [{"route": r, "description": d} for r, d in pairs]})


@app.route('/translate/<from_lang>/<to_lang>', methods=['POST'])
def translate(from_lang, to_lang):
  # Check whether both languages exist
  if from_lang not in lang_maps or to_lang not in lang_maps:
    return jsonify({'error': 'Languages not found!', 'mappings': lang_maps})
  # Get JSON data from request
  json_data = request.get_json()
  # Check for whether 'text' field is within JSON data
  if 'text' not in json_data:
    return jsonify({'error': 'No \'text\' field in JSON!', 'mappings': lang_maps})
  
  return jsonify({'translation': ts.google(query_text=json_data['text'], from_language=lang_maps[from_lang], to_language=lang_maps[to_lang])})


@app.route('/translate/<to_lang>', methods=['POST'])
def translate_default(to_lang):
  # Checking if language exists
  if to_lang not in lang_maps:
    return jsonify({'error': 'Language not found!', 'mappings': lang_maps})
  # Get JSON data from request  
  json_data = request.get_json()
  # Check if 'text' field is within JSON data.
  if 'text' not in json_data:
    return jsonify({'error': 'No \'text\' field in JSON!', 'mappings': lang_maps})
  
  return jsonify({'translation': ts.google(query_text=json_data['text'], to_language=lang_maps[to_lang])})
  
@app.route('/translate', methods=['POST'])
def translate_all_default():
  # Get JSON data from request
  json_data = request.get_json()
  # Check if 'text' field is within JSON data.
  if 'text' not in json_data:
    return jsonify({'error': 'No \'text\' field in JSON!', 'mappings': lang_maps})

  return jsonify({'translation': ts.google(query_text=json_data['text'])})
  
@app.route('/mappings', methods=['GET'])
def mappings():
  return jsonify({'mappings': lang_maps})

if __name__ == "__main__":
  app.run('0.0.0.0', debug=True)
  
