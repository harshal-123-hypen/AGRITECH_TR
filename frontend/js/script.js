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

async function recommendCrop() {

    const district = document.getElementById("cropDistrict").value;
    const rainfall = document.getElementById("cropRainfall").value;
    const temperature = document.getElementById("cropTemperature").value;
    const area = document.getElementById("cropArea").value;
    const marketPrice = document.getElementById("cropMarketPrice").value;

    if (
        district === "" ||
        rainfall === "" ||
        temperature === "" ||
        area === "" ||
        marketPrice === ""
    ) {
        alert("Please fill all fields.");
        return;
    }

    document.getElementById("cropLoading").style.display = "block";
    document.getElementById("cropResult").style.display = "none";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/crop_recommendation",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    district: district,
                    rainfall: Number(rainfall),
                    temperature: Number(temperature),
                    area: Number(area),
                    market_price: Number(marketPrice)

                })

            }
        );

        const data = await response.json();

        document.getElementById("cropLoading").style.display = "none";

        document.getElementById("cropResult").style.display = "block";

        document.getElementById("cropResult").innerHTML = `

            <h2>🌾 Recommended Crop</h2>

            <p><strong>${data.recommended_crop}</strong></p>

            <hr>

            <p>✅ Suitable for current rainfall</p>

            <p>✅ Suitable temperature</p>

            <p>✅ Good market opportunity</p>

        `;

    }

    catch(error){

        document.getElementById("cropLoading").style.display="none";

        alert("Server Error");

        console.log(error);

    }

}