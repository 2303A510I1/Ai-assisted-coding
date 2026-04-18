"""Smart movie booking web app."""
import random
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__, static_folder='movie_images', static_url_path='/static')


def generate_poster_svg(title):
    sanitized = title.replace("'", "\\'").replace('"', "\\\"")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='210' height='300'><rect width='210' height='300' rx='12' ry='12' fill='#2a2a2a'/><text x='50%' y='45%' font-size='20' fill='#fff' text-anchor='middle' font-family='Segoe UI, sans-serif'>{sanitized}</text><text x='50%' y='65%' font-size='14' fill='#ddd' text-anchor='middle'>Movie Poster</text></svg>"""
    import base64
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('utf-8')

MOVIES = {
    1: {
        "title": "RRR",
        "industry": "Tollywood",
        "duration": "2h 55m",
        "showtimes": ["11:00", "14:30", "18:00"],
        "poster": "/static/OIP.jpg",
        "seats": {"11:00": set(range(1, 51)), "14:30": set(range(1, 51)), "18:00": set(range(1, 51))},
    },
    2: {
        "title": "Pushpa",
        "industry": "Tollywood",
        "duration": "2h 35m",
        "showtimes": ["12:30", "16:00", "20:00"],
        "poster": "/static/Allu-Arjun-Pushpa-2.png",
        "seats": {"12:30": set(range(1, 46)), "16:00": set(range(1, 46)), "20:00": set(range(1, 46))},
    },
    3: {
        "title": "Pathaan",
        "industry": "Bollywood",
        "duration": "2h 40m",
        "showtimes": ["11:45", "15:15", "19:30"],
        "poster": "/static/th.jpg",
        "seats": {"11:45": set(range(1, 60)), "15:15": set(range(1, 60)), "19:30": set(range(1, 60))},
    },
    4: {
        "title": "Dunki",
        "industry": "Bollywood",
        "duration": "2h 30m",
        "showtimes": ["13:00", "17:00", "21:00"],
        "poster": "/static/Untitled-design-2022-11-02T123439.191.webp",
        "seats": {"13:00": set(range(1, 55)), "17:00": set(range(1, 55)), "21:00": set(range(1, 55))},
    },
}

BOOKINGS = []


def to_12h(t: str) -> str:
    """Convert HH:MM (24h) to 12-hour display with AM/PM."""
    parts = t.split(":")
    h, m = int(parts[0]), parts[1]
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m} {suffix}"


def generate_poster_svg(title):
    sanitized = title.replace("'", "\'").replace('"', "\"")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='210' height='300'><rect width='210' height='300' rx='12' ry='12' fill='#2a2a2a'/><text x='50%' y='45%' font-size='20' fill='#fff' text-anchor='middle' font-family='Segoe UI, sans-serif'>{sanitized}</text><text x='50%' y='65%' font-size='14' fill='#ddd' text-anchor='middle'>Movie Poster</text></svg>"""
    import base64
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('utf-8')


BASE_PAGE = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'/>
  <title>Smart Movie Booking</title>
  <style>
    body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; background: #f1f3f6; margin: 0; padding: 0; }
    .topbar { display:flex; align-items:center; justify-content:space-between; background:#fff; border-bottom:1px solid #ddd; padding:.8rem 1.5rem; }
    .brand { font-size:1.4rem; font-weight:bold; color:#ff2f6d; }
    .search input { width: 360px; padding:.5rem .8rem; border:1px solid #ccc; border-radius:4px; }
    .actions .login { background:#ff2f6d;color:#fff;border:none;padding:.5rem 1rem;border-radius:4px; cursor:pointer; }
    .menu { background:#fff; border-bottom:1px solid #ddd; display:flex; gap:.8rem; padding:.6rem 1.5rem; }
    .menu a { color:#333; text-decoration:none; font-weight:600; }
    .menu a:hover { color:#ff2f6d; }
    .container { max-width: 1040px; margin: 1rem auto; background: #fff; border-radius: 8px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); padding: 1rem 1.5rem; }
    .movie-card { border: 1px solid #e1e1e1; border-radius: 8px; margin-bottom: 1rem; padding: 1rem; background: #fafafa; overflow: auto; }
    .ticket-card { border: 1px solid #ddd; border-radius:12px; padding:1rem; background:#fff; margin-top:1rem; box-shadow:0 8px 22px rgba(0,0,0,.1); }
    .ticket-card h2 { margin:0 0 .5rem; }
    .ticket-row { display:flex; justify-content:space-between; margin-bottom:.4rem; }
    .ticket-qr { display:flex; align-items:center; gap:.75rem; margin-top:1rem; }
    .rewards-card { border-radius:12px; padding:1rem; background: linear-gradient(135deg,#5f4ade,#7e5dff); color:#fff; margin-top:1rem; }
    .reward-box { display:inline-block; width:calc(50%-.6rem); background:rgba(255,255,255,.2); border-radius:10px; text-align:center; padding:.7rem; margin:.3rem .15rem; }
    .movie-title { margin: 0; font-weight: 700; font-size: 1.3rem; }
    .showtimes a { margin: 0 .35rem; padding: .35rem .75rem; border-radius: 4px; background: #e4e5ff; color: #2c2d72; text-decoration: none; font-weight: 600; }
    .showtimes a:hover { background:#c7c9ff; }
    .book-form { margin-top: 1rem; }
    .button { background: #ff3f6c; color: white; border: 0; border-radius: 5px; padding: .6rem 1rem; cursor: pointer; }
    .seat-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 6px; margin-top: 12px; }
    .seat-cell { border: 1px solid #ddd; border-radius: 4px; width: 100%; min-height: 36px; display:flex; align-items:center; justify-content:center; font-size:0.86rem; }
    .seat-cell input[type=checkbox], .seat-cell input[type=radio] { display: none; }
    .seat-cell.available { background: #f0f9f0; cursor:pointer; }
    .seat-cell.available:hover { background: #def7de; }
    .seat-cell.selected { background: #4caf50; color: white; }
    .seat-cell.sold { background: #f2f2f2; color: #999; cursor: not-allowed; }
    .button:hover { background: #e33760; }
    .error { color: #b00020; margin-top: .6rem; }
    .nav { margin-top: 1rem; }
    .notice { margin: 1rem 0; color: #333; }
  </style>
</head>
<body>
  <div class='topbar'>
    <div class='brand'>SmartMovie</div>
    <div class='search'><input type='text' placeholder='Search for Movies, Events, Plays, Sports'></div>
    <div class='actions'><button class='login'>Sign In</button></div>
  </div>
  <div class='menu'>
    <a href='/'>Movies</a><a href='/'>Stream</a><a href='/'>Events</a><a href='/'>Plays</a><a href='/'>Sports</a><a href='/'>Activities</a>
  </div>
  <div class='container'>
    <h2>Recommended Movies</h2>
    __CONTENT__
    <div class='nav'><a href='__HOME__'>Home</a> | <a href='/bookings'>My Bookings</a> | <a href='/checkout'>Checkout</a></div>
  </div>
</body>
</html>
"""


def render(page_body: str, source: str = ""):
    rendered = BASE_PAGE.replace("__CONTENT__", page_body).replace("__HOME__", source or "/")
    return render_template_string(rendered)


@app.route("/")
def index():
    cards = []
    fallback_poster = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxMjAnIGhlaWdodD0nMTcwJz48cmVjdCB3aWR0aD0nMTIwJyBoZWlnaHQ9JzE3MCcgZmlsbD0nI2RkZCcvPjx0ZXh0IHg9JzUwJScgeT0nNTAlJyBkb21pbmFudC1iYXNlbGluZT0nbWlkZGxlJyB0ZXh0LWFuY2hvcj0nbWlkZGxlJyBmb250LXNpemU9JzE0JyBmaWxsPScjNTU1Jz5ObyBJbWFnZTwvdGV4dD48L3N2Zz4="
    for movie_id, movie in MOVIES.items():
        showtime_links = "".join([f"<a href='/movie/{movie_id}?showtime={st}'>{to_12h(st)}</a>" for st in movie["showtimes"]])
        cards.append(
            f"""
            <div class='movie-card'>
              <img src='{movie['poster']}' onerror="this.src='{fallback_poster}'" alt='{movie['title']}' style='float:right; width:120px; height:170px; object-fit:cover; border-radius:6px; margin-left:12px;'>
              <h2 class='movie-title'>{movie['title']}</h2>
              <p class='notice'>{movie['industry']} | {movie['duration']}</p>
              <div class='showtimes'>{showtime_links}</div>
            </div>
            """
        )
    page = "".join(cards)
    return render(page, source="")


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not BOOKINGS:
        page_body = "<h2>Checkout</h2><p>No booking selected yet. Please book a seat first.</p>"
        return render(page_body, source="/checkout")

    price_per_ticket = 295
    total_tickets = len(BOOKINGS)
    total_amount = total_tickets * price_per_ticket
    fees = total_tickets * 15
    booking_items = "".join([
        f"<li>{b['movie_title']} - {b['showtime']} - Seat {b['seat']} (₹{price_per_ticket})</li>" for b in BOOKINGS
    ])

    discount = 0
    coupon_code = ""
    email = ""
    phone = ""
    message = ""

    if request.method == "POST":
        coupon_code = request.form.get("coupon", "").strip().upper()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if coupon_code == "SAVE50":
            discount = 50
            message = "Coupon applied: ₹50 off."
        else:
            if coupon_code:
                message = "Invalid coupon code."

        total_pay = max(0, total_amount - discount) + fees
        booking_id = f"BMS{random.randint(100000,999999)}"
        seats = ", ".join(str(b["seat"]) for b in BOOKINGS)
        movie_names = ", ".join(b["movie_title"] for b in BOOKINGS)
        showtimes = ", ".join(to_12h(b["showtime"]) for b in BOOKINGS)
        booking_status = ""

        ticket_card = f"""
        <div class='ticket-card'>
          <h2>Your Ticket</h2>
          <div class='ticket-row'><strong>{movie_names}</strong><span>{booking_status}</span></div>
          <div class='ticket-row'><small>{showtimes}</small><small>{len(BOOKINGS)} Ticket(s)</small></div>
          <div class='ticket-row'><small>Seats: {seats}</small><small>Booking ID: {booking_id}</small></div>
          <div class='ticket-row'><small>Amount: ₹{total_pay:.2f}</small><small>Status: Confirmed</small></div>
          <div class='ticket-qr'>
            <img src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNDAnIGhlaWdodD0nMTQwJz48cmVjdCB3aWR0aD0nMTQwJyBoZWlnaHQ9JzE0MCcgZmlsbD0nI2ZmZicvPjxyZWN0IHg9JzEwJyB5PScxMCcgd2lkdGg9JzQwJyBoZWlnaHQ9JzQwJyBmaWxsPScjMDAwJy8+PHJlY3QgeD0nOTAnIHk9JzEwJyB3aWR0aD0nNDAnIGhlaWdodD0nNDAnIGZpbGw9JyMwMDAnLz48cmVjdCB4PScxMCcgeT0nOTAnIHdpZHRoPSc0MCcgaGVpZ2h0PSc0MCcgZmlsbD0nIzAwMCcvPjxyZWN0IHg9JzcwJyB5PSc3MCcgd2lkdGg9JzEwJyBoZWlnaHQ9JzEwJyBmaWxsPScjMDAwJy8+PHJlY3QgeD0nODInIHk9JzgyJyB3aWR0aD0nMTAnIGhlaWdodD0nMTAnIGZpbGw9JyMwMDAnLz48cmVjdCB4PSc3MCcgeT0nODInIHdpZHRoPScxMCcgaGVpZ2h0PScxMCcgZmlsbD0nIzAwMCcvPjxyZWN0IHg9JzgyJyB5PSc3MCcgd2lkdGg9JzEwJyBoZWlnaHQ9JzEwJyBmaWxsPScjMDAwJy8+PHRleHQgeD0nNzAnIHk9JzEzMicgZmlsbD0nIzU1NScgZm9udC1zaXplPScxMicgdGV4dC1hbmNob3I9J21pZGRsZSc+UVIgLyBVUEk8L3RleHQ+PC9zdmc+' alt='QR code' style='width:120px;height:120px;border:2px solid #444; padding:4px;'>
            <div><strong>Scan QR to show at theatre</strong></div>
          </div>
        </div>
        <div class='rewards-card'>
          <h3>You've won {random.randint(1,3)} Rewards!</h3>
          <div class='reward-box'>Free Popcorn</div>
          <div class='reward-box'>15% OFF</div>
        </div>
        """
        return render(ticket_card, source="/confirmation")

    page_body = f"""
    <h2>Checkout</h2>
    <div style='display:grid; grid-template-columns: 2fr 1fr; gap:1rem;'>
      <div style='border:1px solid #ddd; border-radius:8px; background:#fff; padding:1rem;'>
        <h3>Complete Payment</h3>
        <p>Your booking is ready. Click below to complete payment and view your ticket.</p>
        <form method='post' action='/checkout' style='margin-top:1rem;'>
          <p><label>Phone number<br><input name='phone' value='{phone}' placeholder='Enter phone' style='width:100%; padding:.4rem;'></label></p>
          <p><label>Email<br><input name='email' value='{email}' placeholder='Enter email' style='width:100%; padding:.4rem;'></label></p>
          <p style='color:green;'>{message}</p>
          <button class='button' type='submit' style='width:100%; margin-top:1rem;'>Pay Now</button>
        </form>
      </div>

      <div style='border:1px solid #ddd; border-radius:8px; background:#fff; padding:1rem;'>
        <h3>Order Summary</h3>
        <p><strong>{total_tickets}</strong> tickets selected</p>
        <ul style='padding-left:1.2rem;'>{booking_items}</ul>
        <hr>
        <p>Ticket price: &#x20B9;{total_amount}</p>
        <p>Convenience fee: &#x20B9;{fees}</p>
        <p>Discount: &#x20B9;{discount}</p>
        <p style='font-weight:700;'>Total payable: &#x20B9;{total_amount + fees - discount}</p>
        <div style='margin-top:1rem; padding:.8rem; border:1px solid #eee; border-radius:6px; background:#f9f9f9;'>
          <p style='margin:0; font-size:0.9rem;'>Click Pay Now to confirm your booking.</p>
        </div>
      </div>
    </div>
    """

    return render(page_body, source="/checkout")


@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    showtime = request.args.get("showtime")
    if movie_id not in MOVIES or not showtime:
        return redirect(url_for("index"))

    movie_data = MOVIES[movie_id]
    if showtime not in movie_data["showtimes"]:
        return redirect(url_for("index"))

    seats = sorted(movie_data["seats"][showtime])
    seat_list = ", ".join(map(str, seats[:20])) + ("..." if len(seats) > 20 else "")
    showtime_12h = to_12h(showtime)
    max_seat = max((r for r in range(1, 101)), default=60)

    page_body = f"""
      <div class='movie-card'>
        <h2 class='movie-title'>{movie_data['title']}</h2>
        <p class='notice'>{movie_data['industry']} | {movie_data['duration']} | Showtime {showtime_12h}</p>
        <p>Available seats <strong>{len(seats)}</strong></p>
        <form class='book-form' method='post' action='/book/{movie_id}/{showtime}'>
          <div class='seat-grid'>
"""

    for seat_num in range(1, 61):
        if seat_num in movie_data['seats'][showtime]:
            page_body += f"<label class='seat-cell available'><input type='checkbox' name='seat' value='{seat_num}'>{seat_num}</label>"
        else:
            page_body += f"<div class='seat-cell sold'>{seat_num}</div>"

    page_body += """
          </div>
          <p><small>Tip: Select multiple seats then press Book Now (max 8 seats).</small></p>
          <button class='button' type='submit'>Book Now</button>
        </form>
      </div>
      <script>
        document.querySelectorAll('.seat-cell.available input[type=checkbox]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const parent = checkbox.closest('.seat-cell');
                if (checkbox.checked) {
                    parent.classList.add('selected');
                } else {
                    parent.classList.remove('selected');
                }
            });
        });
      </script>
    """

    return render(page_body, source="")


@app.route("/book/<int:movie_id>/<showtime>", methods=["POST"])
def book(movie_id, showtime):
    if movie_id not in MOVIES or showtime not in MOVIES[movie_id]["showtimes"]:
        return redirect(url_for("index"))

    selected_seats = request.form.getlist("seat")
    if not selected_seats:
        return "Select at least one seat", 400

    seats = []
    for seat_str in selected_seats:
        try:
            seat_num = int(seat_str)
        except ValueError:
            return "Invalid seat selection", 400
        if seat_num < 1 or seat_num > 100:
            return "Seat must be between 1 and 100", 400
        seats.append(seat_num)

    if len(set(seats)) != len(seats):
        return "Duplicate seat selection", 400
    if len(seats) > 8:
        return "You can book up to 8 seats at once", 400

    unavailable = [s for s in seats if s not in MOVIES[movie_id]["seats"][showtime]]
    if unavailable:
        return render(f"<h2>{MOVIES[movie_id]['title']} - {to_12h(showtime)}</h2><p>Seats {', '.join(map(str, unavailable))} are unavailable.</p><p>Please try again.</p>", source="")

    for seat_num in seats:
        MOVIES[movie_id]["seats"][showtime].remove(seat_num)
        BOOKINGS.append({"movie_title": MOVIES[movie_id]["title"], "showtime": showtime, "seat": seat_num, "name": "Guest"})

    return redirect(url_for("view_bookings"))


@app.route("/bookings")
def view_bookings():
    if not BOOKINGS:
        page_body = "<p>No bookings yet.</p>"
    else:
        items = "".join([f"<div class='movie-card'><p><strong>{b['movie_title']} ({b['showtime']})</strong></p><p>Seat {b['seat']} - {b['name']}</p></div>" for b in BOOKINGS])
        page_body = f"<h2>My Bookings</h2>{items}"

    return render(page_body, source="")


if __name__ == "__main__":
    app.run(debug=True, port=5000)

