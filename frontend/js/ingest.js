async function ingestURL() {

    const url = document.getElementById("urlInput").value;
    const status = document.getElementById("ingestStatus");

    status.innerText = "Processing...";

    try {

        const result = await apiPost("/ingest", { url: url });

        status.innerText = "Ingestion complete.";

    } catch (err) {

        status.innerText = "Error ingesting URL.";
        console.error(err);

    }
}