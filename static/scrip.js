function submitForm() {
    // Get form values
    var description = document.getElementById("description").value;
    var targetDate = document.getElementById("targetDate").value;
    var targetWeight = document.getElementById("targetWeight").value;

    // Perform basic validation
    if (!description || !targetDate || !targetWeight) {
        alert("Please fill in all fields");
        return;
    }

    // Log form values (you can send them to the server or perform other actions)
    console.log("Description:", description);
    console.log("Target Date:", targetDate);
    console.log("Target Weight:", targetWeight);

    // Optionally, you can reset the form
    document.getElementById("goalForm").reset();
}
