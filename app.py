import streamlit as st

from src.vision import analyze_room


st.set_page_config(
    page_title="AI Home Decorator",
    page_icon="🏠",
    layout="wide"
)


st.title("🏠 AI Home Decorator Assistant")

st.write(
    "Create a practical decoration plan based on your room, "
    "existing furniture, preferences, and budget."
)


st.header("Room Information")


room_type = st.selectbox(
    "Room Type",
    [
        "Bedroom",
        "Living Room",
        "Study Room",
        "Dining Room",
        "Other"
    ]
)


dimensions = st.text_input(
    "Room Dimensions",
    placeholder="Example: 10 × 12 ft"
)


budget = st.number_input(
    "Budget",
    min_value=0,
    step=1000
)


currency = st.selectbox(
    "Currency",
    [
        "PKR",
        "USD",
        "EUR",
        "GBP"
    ]
)


style = st.selectbox(
    "Preferred Style",
    [
        "Modern",
        "Minimalist",
        "Modern Minimal",
        "Scandinavian",
        "Industrial",
        "Bohemian",
        "Traditional",
        "Contemporary"
    ]
)


existing_furniture = st.text_area(
    "Existing Furniture",
    placeholder=(
        "Example: Bed, wardrobe, study table, chair"
    )
)


requirements = st.text_area(
    "What do you want to improve?",
    placeholder=(
        "Example: I need more storage and better lighting."
    )
)


room_image = st.file_uploader(
    "Upload Room Photo",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


if st.button("Analyze My Room"):

    if not dimensions.strip():

        st.warning(
            "Please enter room dimensions."
        )

    elif budget <= 0:

        st.warning(
            "Please enter a valid budget."
        )

    elif not existing_furniture.strip():

        st.warning(
            "Please tell us what furniture you already have."
        )

    elif not requirements.strip():

        st.warning(
            "Please describe what you want to improve."
        )

    elif room_image is None:

        st.warning(
            "Please upload a room photo."
        )

    else:

        st.image(
            room_image,
            caption="Uploaded Room",
            use_container_width=True
        )

        with st.spinner(
            "Analyzing your room..."
        ):

            analysis = analyze_room(
                room_image.getvalue(),
                room_image.type
            )

        st.success(
            "Room analysis completed!"
        )

        st.subheader("Room Analysis")

        st.write(
            "Room Type:",
            analysis.room_type
        )

        st.write(
            "Furniture:",
            ", ".join(
                analysis.visible_furniture
            )
        )

        st.write(
            "Colors:",
            ", ".join(
                analysis.colors
            )
        )

        st.write(
            "Lighting:",
            analysis.lighting
        )

        st.write(
            "Storage:",
            ", ".join(
                analysis.storage
            )
        )

        st.write("Layout Issues")

        for issue in analysis.layout_issues:

            st.write(
                f"- {issue}"
            )

        st.write("Opportunities")

        for opportunity in analysis.opportunities:

            st.write(
                f"- {opportunity}"
            )