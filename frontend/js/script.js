async function predict() {

    const crop = document.getElementById("crop").value;
    const district = document.getElementById("district").value;
    const area = document.getElementById("area").value;

    const response = await fetch(
        "http://127.0.0.1:5000/predict",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                crop: crop,
                district: district,
                area: area
            })
        }
    );

    const data = await response.json();

    document.getElementById("result").innerHTML =
        data.prediction;
}