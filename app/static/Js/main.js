function control(domain, action) {
    fetch(`/panel/${domain}/action`, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({action: action})
    })
    .then(res => res.json())
    .then(data => alert(JSON.stringify(data)))
    .catch(err => alert("Error: " + err));
}

function showLogs(domain) {
    fetch(`/panel/${domain}/logs`)
    .then(res => res.json())
    .then(data => {
        document.getElementById("logs").textContent = data.logs || data.error;
    });
}

function testEmail(domain) {
    fetch(`/panel/${domain}/email_test`, {method: "POST"})
    .then(res => res.json())
    .then(data => alert(JSON.stringify(data)));
}
