from flask import Flask, render_template_string, request, session
import praw
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure PRAW
reddit = praw.Reddit(
    client_id='client_id',
    client_secret='client_secret',
    user_agent='SubredditGuessGame/0.1 by testingbot321'
)

# Subreddits list
subreddits = [
    "funny", "AskReddit", "gaming", "aww", "Music",
    "pics", "science", "videos", "todayilearned", "movies",
    "news", "Showerthoughts", "EarthPorn", "gifs", "IAmA", "food",
    "askscience", "Jokes", "LifeProTips", "explainlikeimfive", "Art",
    "books", "mildlyinteresting", "nottheonion", "DIY", "sports",
    "space"
]

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Guess the Subreddit</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background: #000;
        color: #e0e6f8;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        margin: 0;
        overflow-x: hidden;
      }
      .container {
        width: 90%;
        max-width: 600px;
        padding: 2rem;
        background: #0a0a1f;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.3);
        text-align: center;
        position: relative;
      }
      h1 { font-weight: normal; margin-bottom: 2rem; color: #a0c4ff; }
      .post { font-size: 1.2rem; margin-bottom: 1rem; }
      .image { margin-bottom: 1rem; max-height: 250px; overflow: hidden; }
      .image img {
        max-width: 100%;
        max-height: 250px;
        width: auto;
        height: auto;
        border-radius: 6px;
        object-fit: contain;
      }
      input[type=text] {
        width: 100%;
        padding: 0.5rem;
        border: none;
        border-radius: 4px;
        margin-bottom: 1rem;
        background: #1f2b3d;
        color: #eee;
      }
      input[type=submit] {
        background: #0056b3;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
        width: 100%;
      }
      .result { margin-top: 1rem; font-weight: bold; font-size: 1.1rem; }
      .emoji { font-size: 2rem; margin-top: 0.5rem; }
      .scoreboard {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #122033;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        color: #a0c4ff;
      }
      .subreddit-banner {
        margin-top: 1rem;
        background-color: #0d1a2b;
        color: #a0c4ff;
        padding: 0.5rem;
        border-radius: 5px;
        overflow-x: auto;
        white-space: nowrap;
      }
      .subreddit-tag {
        padding: 0.2rem 0.5rem;
        background: #1f2b3d;
        border-radius: 4px;
        font-size: 0.85rem;
        margin: 0 0.2rem;
        display: inline-block;
      }
    </style>
    <script>
      function delayAndSubmit() {
        const form = document.getElementById('next-form');
        setTimeout(() => form.submit(), 2000);
      }
    </script>
  </head>
  <body>
    <div class="container">
      <div class="scoreboard">Points: {{ points }}</div>
      <h1>Guess the Subreddit</h1>
      <div class="post">"{{ post_title }}"</div>
      {% if post_image %}
        <div class="image"><img src="{{ post_image }}" alt="Reddit post image"></div>
      {% endif %}
      {% if result %}
        <div class="result">{{ result }}</div>
        {% if correct %}
          <div class="emoji">🎉🌟🥳</div>
        {% else %}
          <div class="emoji">😞</div>
        {% endif %}
        <form id="next-form" method="get" action="/"></form>
        <script>delayAndSubmit();</script>
      {% else %}
        <form method="post">
          <input type="text" name="guess" placeholder="Enter subreddit name (no r/)" required>
          <input type="submit" value="Submit Guess">
        </form>
        <div class="subreddit-banner">
          {% for sr in subreddit_list %}
            <span class="subreddit-tag">{{ sr }}</span>
          {% endfor %}
        </div>
      {% endif %}
    </div>
  </body>
</html>
"""

def generate_new_post():
    chosen_sub = random.choice(subreddits)
    posts = list(reddit.subreddit(chosen_sub).hot(limit=50))
    post = random.choice([p for p in posts if not p.stickied])
    session['answer'] = chosen_sub
    session['post_title'] = post.title
    if hasattr(post, 'url') and (post.url.endswith('.jpg') or post.url.endswith('.png') or post.url.endswith('.jpeg')):
        session['post_image'] = post.url
    else:
        session['post_image'] = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'points' not in session:
        session['points'] = 0

    if request.method == 'POST':
        guess = request.form['guess'].strip().lower()
        answer = session.get('answer', '').lower()
        correct = (guess == answer)
        result = f"Correct! It was r/{answer}." if correct else f"Wrong! It was r/{answer}."

        if correct:
            session['points'] += 1

        post_title = session.get('post_title', 'Unknown post')
        post_image = session.get('post_image')
        return render_template_string(HTML_TEMPLATE,
                                      post_title=post_title,
                                      post_image=post_image,
                                      result=result,
                                      correct=correct,
                                      points=session['points'],
                                      subreddit_list=subreddits)
    else:
        generate_new_post()
        post_title = session.get('post_title', 'Unknown post')
        post_image = session.get('post_image')
        return render_template_string(HTML_TEMPLATE,
                                      post_title=post_title,
                                      post_image=post_image,
                                      result=None,
                                      correct=None,
                                      points=session['points'],
                                      subreddit_list=subreddits)

if __name__ == '__main__':
    app.run(debug=True)
