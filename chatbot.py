import streamlit as st
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

data = pd.read_csv("delivery_data.csv")
X = data[["pizza_size", "distance_km"]]
y = data["delivery_time_min"]
regression_model = LinearRegression()
regression_model.fit(X, y)

size_map = {"small": 0, "medium": 1, "large": 2}
menu = {"small": 50, "medium": 80, "large": 120}
image_files = {
    "small": "small pizza.jpg",
    "medium": "medium pizza.jpeg",
    "large": "large pizza.jpg"
    }

defaults = {
    "orders": [],
    "order": None,
    "name": "",
    "address": "",
    "asking_name": False,
    "asking_address": False,
    "asking_more": False,
    "distance_km": 2,
    "delivered": False,
    "tracking_started": False,
    "est_time": None,
    }
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

def predict_delivery_time(size, distance):
    size_encoded = size_map.get(size, 1)
    input_data = pd.DataFrame([[size_encoded, distance]], columns=["pizza_size", "distance_km"])
    return regression_model.predict(input_data)[0]

st.title("PizzaBot CODEWORK")
st.write("Welcome! Choose a pizza below or view the menu.")

with st.expander("Show Menu"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(image_files["small"], caption="Small - ₹50", width=120)
    with col2:
        st.image(image_files["medium"], caption="Medium - ₹80", width=120)
    with col3:
        st.image(image_files["large"], caption="Large - ₹120", width=120)

if not st.session_state.order and not st.session_state.asking_more and not st.session_state.asking_name and not st.session_state.tracking_started:
    st.markdown("Choose your pizza size:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Small"):
            st.session_state.order = "small"
    with col2:
        if st.button("Medium"):
            st.session_state.order = "medium"
    with col3:
        if st.button("Large"):
            st.session_state.order = "large"

if st.session_state.order:
    size = st.session_state.order
    st.markdown(f"You selected a {size} pizza. Confirm order?**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm"):
            st.session_state.orders.append(size)
            st.session_state.order = None
            st.session_state.asking_more = True
    with col2:
        if st.button("Cancel"):
            st.session_state.order = None

if st.session_state.asking_more:
    st.markdown("Would you like to order another pizza?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            st.session_state.asking_more = False
    with col2:
        if st.button("No, proceed"):
            st.session_state.asking_more = False
            if not st.session_state.name:
                st.session_state.asking_name = True

if st.session_state.asking_name:
    st.session_state.name = st.text_input("Enter your name:")
    if st.session_state.name:
        st.session_state.asking_name = False
        st.session_state.asking_address = True

if st.session_state.asking_address:
    st.session_state.address = st.text_input("Enter your delivery address:")
    if st.session_state.address:
        st.session_state.asking_address = False
        st.session_state.tracking_started = True

        times = [predict_delivery_time(size, st.session_state.distance_km) for size in st.session_state.orders]
        st.session_state.est_time = int(max(times) if times else 20)

if st.session_state.tracking_started and not st.session_state.delivered:
    with st.status("Preparing your order...", expanded=True) as status:
        time.sleep(2)
        st.write("Step 1: Preparing your pizza")
        time.sleep(2)
        st.write("Step 2: Pizza is baking in the oven")
        time.sleep(2)
        status.update(label="Out for delivery...", state="running")
        st.write("Step 3: Out for delivery")

        eta = st.session_state.est_time
        placeholder = st.empty()

        for remaining in range(eta, -1, -1):
            placeholder.info(f"ETA: {remaining} minute(s)")
            time.sleep(0.5)

        status.update(label="Delivered!", state="complete")
        st.success(f"Delivered to {st.session_state.address}. Enjoy your meal, {st.session_state.name}!")
        st.balloons()
        st.session_state.delivered = True

with st.sidebar:
    st.header("Order Summary")
    if st.session_state.orders:
        for item in st.session_state.orders:
            st.write(f"{item.capitalize()} - ₹{menu[item]}")
        total = sum(menu[size] for size in st.session_state.orders)
        st.markdown(f"Total: ₹{total}")
    else:
        st.write("No items in your order yet.")
    if st.button("Reset Order"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
