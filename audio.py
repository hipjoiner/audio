import functools
import os
import random
import re
import unicodedata


from flask import Flask, Response, render_template


app = Flask(__name__)


audio_exts = {
    '.mp3': 'mp3',
    '.ogg': 'ogg',
    '.wav': 'x-wav',
}


def slugify(string):
    norm = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
    sub1 = re.sub(r'[^\w\s-]', '', str(norm))
    sub1 = sub1.strip()
    sub1 = sub1.lower()
    sub1 = str(sub1)
    sub2 = re.sub(r'[-\s]+', '-', sub1)
    return sub2


@functools.lru_cache()
def audio_files():
    """Return hash by slug of all available audio files
    """
    result = {}
    root = os.path.join(os.getenv('USERPROFILE'), 'Music')
    for base, dirs, files in os.walk(root):
        for fname in files:
            f, ext = os.path.splitext(fname)
            if ext.lower() not in audio_exts:
                continue
            fpath = os.path.join(base, fname)
            slug = slugify(fpath)
            result[slug] = fpath
    return result


@functools.lru_cache()
def audio_list():
    return sorted(audio_files().values())


@functools.lru_cache()
def audio_slugs():
    return sorted(audio_files().keys())


def get_audio(slug=None):
    if slug is None:
        i = random.randint(0, len(audio_slugs()))
        slug = audio_slugs()[i]
    fname = audio_files().get(slug)
    return slug, fname


@app.route('/')
def player():
    slug, fname = get_audio()
    return render_template('audio.html', **locals())


@app.route('/list')
def get_list():
    return '<br/>'.join(audio_files())


@app.route('/list/<slug>')
def get_item(slug=None):
    if slug is None:
        return '<br/>'.join(audio_files())
    try:
        i = int(slug)
        fname = audio_list()[i]
    except:
        fname = audio_files().get(slug, '<Not Found>')
    return fname


@app.route('/play/<slug>')
def stream(slug):
    fname = audio_files().get(slug)
    f, ext = os.path.splitext(fname)

    def generate():
        with open(fname, 'rb') as fp:
            data = fp.read(1024)
            while data:
                yield data
                data = fp.read(1024)
    ftype = audio_exts.get(ext, 'unknown')
    return Response(generate(), mimetype='audio/%s' % ftype)


if __name__ == "__main__":
    app.run(debug=True)
