import streamlit as st
import json
from urllib.parse import quote
from google import genai
from google.genai import types
from prompts import RECEIPT_PROMPT


st.title("SnapSplit")
st.write("One snap. Everyone's share.")


# Gemini setup
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# Save receipt data
if "receipt_data" not in st.session_state:
    st.session_state.receipt_data = None


# Upload receipt
st.subheader("Upload your receipt")

receipt = st.file_uploader(
    "Choose a receipt image",
    type=["jpg", "jpeg", "png"]
)


if receipt is not None:

    st.image(receipt, caption="Uploaded Receipt")

    if st.button("Analyze Receipt"):

        with st.spinner("Reading your receipt..."):

            image = types.Part.from_bytes(
                data=receipt.getvalue(),
                mime_type=receipt.type
            )

            prompt = RECEIPT_PROMPT

            try:

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[prompt, image]
                )

                result = response.text.strip()

                # Remove markdown if Gemini adds it
                if result.startswith("```"):
                    result = result.replace("```json", "")
                    result = result.replace("```", "")
                    result = result.strip()

                if result == "":
                    st.error("Gemini did not return any data.")

                else:
                    data = json.loads(result)
                    st.session_state.receipt_data = data

            except Exception as e:

                st.error("Unable to analyze the receipt.")
                st.write("Please try again.")


# Show receipt information
if st.session_state.receipt_data is not None:

    data = st.session_state.receipt_data

    st.subheader("Receipt Details")

    st.write("Restaurant:", data["restaurant_name"])
    st.write("Category:", data["category"])

    st.subheader("Items")

    for item in data["items"]:

        st.write(
            item["name"],
            "x", item["quantity"],
            "- ₹", item["amount"]
        )

    st.subheader("Bill Summary")

    st.write("Subtotal: ₹", data["subtotal"])
    st.write("Tax: ₹", data["tax"])
    st.write("Total: ₹", data["total"])


    # Number of people
    st.subheader("Split the Bill")

    people = st.number_input(
        "Number of people",
        min_value=1,
        max_value=10,
        value=2
    )


    # Enter names
    names = []

    for i in range(people):

        name = st.text_input(
            "Person " + str(i + 1),
            "Person " + str(i + 1),
            key="person_" + str(i)
        )

        names.append(name)


    # Store each person's item amount
    amounts = {}

    for name in names:
        amounts[name] = 0.0


    st.subheader("Assign Items")


    # Assign items to people
    for i, item in enumerate(data["items"]):

        st.write(
            item["name"],
            "- ₹", item["amount"]
        )

        selected_people = st.multiselect(
            "Who had this item?",
            names,
            key="item_" + str(i)
        )

        if len(selected_people) > 0:

            share = item["amount"] / len(selected_people)

            for person in selected_people:
                amounts[person] += share


    # Add tax according to each person's share
    for person in amounts:

        if data["subtotal"] > 0:

            tax_share = (
                amounts[person]
                / data["subtotal"]
            ) * data["tax"]

            amounts[person] += tax_share


    # Show final amounts
    st.subheader("Individual Amounts")

    total_assigned = 0.0

    for person in amounts:

        amount = round(amounts[person], 2)

        st.write(
            person,
            ": ₹",
            amount
        )

        total_assigned += amount


    total_assigned = round(total_assigned, 2)

    st.write(
        "Assigned Total: ₹",
        total_assigned
    )

    st.write(
        "Receipt Total: ₹",
        data["total"]
    )


    # Check whether everything was assigned
    if abs(total_assigned - data["total"]) < 0.02:

        st.success(
            "Split completed successfully!"
        )


        # Gmail sharing
        st.subheader("Share the Bill")

        message = "SnapSplit Bill\n\n"

        message += (
            "Restaurant: "
            + data["restaurant_name"]
            + "\n"
        )

        message += (
            "Category: "
            + data["category"]
            + "\n"
        )

        message += (
            "Total: ₹"
            + str(data["total"])
            + "\n\n"
        )

        for person in amounts:

            message += (
                person
                + ": ₹"
                + str(round(amounts[person], 2))
                + "\n"
            )

        message += "\nOne snap. Everyone's share."

        gmail_link = (
            "https://mail.google.com/mail/?view=cm&fs=1"
            "&su="
            + quote("SnapSplit Bill")
            + "&body="
            + quote(message)
        )

        st.link_button(
            "Share through Gmail",
            gmail_link
        )

    else:

        st.warning(
            "Please assign all the items."
        )