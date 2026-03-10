async function loadDocuments() {

    const list = document.getElementById("documentList");
    list.innerHTML = "";

    const docs = await apiGet("/documents");

    docs.forEach(doc => {

        const li = document.createElement("li");
        li.innerText = doc.url || doc.title || "Document";

        list.appendChild(li);

    });
}