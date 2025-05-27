<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Clarity - Results</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="results-container">
    <h2>Tier 1</h2>
    <p id="tier1-result">Loading...</p>
    <h2>Tier 2</h2>
    <p id="tier2-result">Loading...</p>
    <h2>Tier 3</h2>
    <p id="tier3-result">Loading...</p>
  </div>

  <script>
    const params = new URLSearchParams(window.location.search);
    const v1 = params.get('variable1');
    const v2 = params.get('variable2');
    const v3 = params.get('variable3');

    fetch('https://clarity-do5e.onrender.com/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ variables: [v1, v2, v3] })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById('tier1-result').textContent = data.synthesis || "No synthesis result";
      document.getElementById('tier2-result').textContent = data.message || "No system message";
      document.getElementById('tier3-result').textContent = "✅";
    })
    .catch(err => {
      console.error("Fetch error:", err);
      document.getElementById('tier1-result').textContent = "Error loading results.";
      document.getElementById('tier2-result').textContent = "Please try again later.";
      document.getElementById('tier3-result').textContent = "";
    });
  </script>
</body>
</html>
