from flask import Flask, request, jsonify, render_template_string
import spacy

app = Flask(__name__)

POS_COLORS = {
    'NOUN':   '#ff4444',   # red
    'PROPN':  '#ff4444',   # proper noun (same as noun)
    'VERB':   '#44cc44',   # green
    'AUX':    '#44aa44',   # auxiliary verbs (green tone)
    'ADJ':    '#4488ff',   # blue
    'ADV':    '#ffaa44',   # orange
    'PRON':   '#b266ff',   # purple
    'CONJ':   '#00cccc',
    'SCONJ':  '#00cccc',   # subordinating conj.
    'ADP':    '#bbcc44',   # prepositions
    'DET':    '#66bb66',   # determiners
    'INTJ':   '#ff66cc',   # interjections
    'NUM':    '#fa8072',   # numerals (salmon)
    'PART':   '#a9a9a9',   # particles (grey)
    'PUNCT':  '#000000',   # black
    'SYM':    '#d2691e',
    'X':      '#888888',
    'SPACE':  '',          # not shown
}

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


@app.route("/")
def index():
    # Inline HTML/JS/CSS for simplicity.
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>POS Color Tagger</title>
<style>
body { font-family: Arial, sans-serif; padding: 2em; background: #f7f7fa; }
#inputBox, #outputBox { width: 100%; font-size: 18px; }
#inputBox { height: 90px; }
#outputBox { border: 1px solid #ccc; background: #fff; min-height: 90px; padding: 1em; }
.word { padding: 1px 2px; border-radius: 3px; margin: 1px; display: inline-block; }
#legend { margin-top:1.5em;font-size: 15px; }
.legend-block { display:inline-block; padding:3px 7px; margin-right:6px; border-radius:3px; }
</style>
</head>
<body>
<h2>POS Color Tagger</h2>
<p>Type or paste English text below. Each word will be colored by its part of speech.</p>
<textarea id="inputBox" placeholder="Enter text..."></textarea>
<div id="outputBox"></div>
<div id="legend"></div>
<script>
const POS_COLORS = {{ pos_colors | safe }};

function renderLegend() {
    let html = '';
    for (let pos in POS_COLORS) {
        if (!POS_COLORS[pos]) continue;
        html += '<span class="legend-block" style="background:' + POS_COLORS[pos] + '">' + pos + '</span>';
    }
    document.getElementById('legend').innerHTML = '<b>Legend:</b> ' + html;
}

renderLegend();

function renderOutput(words) {
    let html = '';
    for (let {text, pos, color} of words) {
        if (text.trim() === "") {
            html += text.replace(/\\n/g, "<br>"); // keep newlines
            continue;
        }
        html += `<span class="word" style="background:${color || '#eeeeee'}" title="${pos}">${text}</span> `;
    }
    document.getElementById('outputBox').innerHTML = html;
}

let debounceTimer;
document.getElementById('inputBox').addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const val = this.value;
    debounceTimer = setTimeout(()=> {
        fetch('/tag', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({text: val})
        })
        .then(resp => resp.json())
        .then(renderOutput)
    }, 180);
});
</script>
</body>
</html>
""", pos_colors=POS_COLORS)


@app.route("/tag", methods=["POST"])
def tag():
    data = request.get_json(force=True)
    txt = data['text']
    doc = nlp(txt)
    words = []
    for w in doc:
        if w.is_space:
            words.append({'text': w.text, 'pos': w.pos_, 'color': ""})
            continue
        color = POS_COLORS.get(w.pos_, "#bbbbbb")
        words.append({'text': w.text, 'pos': w.pos_, 'color': color})
    return jsonify(words)


if __name__ == "__main__":
    app.run(port=5050, debug=True)
