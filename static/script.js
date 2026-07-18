const searchInput = document.getElementById("search-input");
const movieList = document.getElementById("movie-list");
let debounceTimer = null;

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderMovies(movies) {
  if (!movies.length) {
    movieList.innerHTML = `
      <div class="empty-state">
        <strong>No titles here.</strong><br>
        Try a different search, or log a new rating above.
      </div>`;
    return;
  }

  movieList.innerHTML = movies.map(m => `
    <div class="ticket">
      <div class="ticket-main">
        <h3>${escapeHtml(m.display_title)}</h3>
        <div class="meta">${m.votes} vote${m.votes !== 1 ? "s" : ""}</div>
      </div>
      <div class="ticket-stub">
        <div class="score">${m.avg_rating}<span>/10</span></div>
        <form action="/delete/${encodeURIComponent(m.title)}" method="post"
              onsubmit="return confirm('Remove ${escapeHtml(m.display_title)}?');">
          <button type="submit" class="btn-danger">Remove</button>
        </form>
      </div>
    </div>
  `).join("");
}

if (searchInput) {
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const q = searchInput.value;

    debounceTimer = setTimeout(async () => {
      const params = new URLSearchParams({ q, sort: currentSort });
      try {
        const res = await fetch(`/api/search?${params.toString()}`);
        const data = await res.json();
        renderMovies(data);

        // keep the URL/search state shareable without a full reload
        const url = new URL(window.location);
        url.searchParams.set("q", q);
        window.history.replaceState({}, "", url);
      } catch (err) {
        console.error("Search failed:", err);
      }
    }, 250);
  });
}
