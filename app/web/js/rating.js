async function setRating(photoId, value) {
  const res = await fetch(`/photos/${photoId}/rating`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({value})
  });

  if (!res.ok) {
    const txt = await res.text();
    alert(txt);
    return;
  }

  const data = await res.json(); // {avg, count}
  document.querySelector(`#rating-avg-${photoId}`).textContent = data.avg.toFixed(2);
  document.querySelector(`#rating-count-${photoId}`).textContent = data.count;
}