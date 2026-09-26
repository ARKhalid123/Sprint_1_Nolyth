

import streamlit as st
import requests
from datetime import date, datetime
import pandas as pd


API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon=":material/account_balance_wallet:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Font Awesome 6 for professional vector icon styling
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    """,
    unsafe_allow_html=True
)

CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Utilities",
    "Entertainment & Leisure",
    "Shopping & Groceries",
    "Health & Medical",
    "Education",
    "Personal Care",
    "Bills & Subscriptions",
    "Other"
]


if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "edit_expense_id" not in st.session_state:
    st.session_state["edit_expense_id"] = None


def make_api_request(method: str, endpoint: str, data: dict = None, params: dict = None, auth: bool = True):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}

    if auth and st.session_state["token"]:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return False, "Unsupported HTTP method"

        if response.status_code in [200, 201]:
            return True, response.json()
        elif response.status_code == 401:
            st.session_state["token"] = None
            st.session_state["user"] = None
            return False, "Session expired. Please log in again."
        else:
            try:
                error_detail = response.json().get("detail", response.text)
                if isinstance(error_detail, list):
                    # Pydantic validation errors
                    messages = [f"{err.get('loc', ['field'])[-1]}: {err.get('msg')}" for err in error_detail]
                    return False, " | ".join(messages)
                return False, str(error_detail)
            except Exception:
                return False, f"Server Error ({response.status_code})"

    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to the FastAPI backend. Make sure it is running on http://127.0.0.1:8000."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"




def check_backend_status():

    try:
        # Check backend reachability via OpenAPI endpoint (no dedicated health route required)
        res = requests.get(f"{API_BASE_URL}/openapi.json", timeout=2)
        return res.status_code == 200
    except Exception:
        return False



def render_auth_page():
    st.title(":material/account_balance_wallet: Personal Expense Tracker")
    st.subheader("Manage and monitor your daily finances easily")

    # Backend status banner
    backend_live = check_backend_status()
    if not backend_live:
        st.warning("Backend is offline or unreachable. Please start the FastAPI server via `uvicorn main:app --reload`.", icon=":material/wifi_off:")

    tab_login, tab_register = st.tabs([":material/login: Sign In", ":material/person_add: Create Account"])

    # --- TAB 1: LOGIN ---
    with tab_login:
        st.markdown("### Welcome Back")
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username or Email", placeholder="e.g. john_doe").strip()
            password_input = st.text_input("Password", type="password", placeholder="Enter your password").strip()
            submit_login = st.form_submit_button("Sign In", use_container_width=True)

            if submit_login:
                # Client-side form validation
                if not username_input:
                    st.error("Please enter your username or email.")
                elif not password_input:
                    st.error("Please enter your password.")
                else:
                    payload = {"username": username_input, "password": password_input}
                    success, result = make_api_request("POST", "/auth/login", data=payload, auth=False)

                    if success:
                        st.session_state["token"] = result["access_token"]
                        # Fetch profile
                        user_ok, user_profile = make_api_request("GET", "/auth/me", auth=True)
                        if user_ok:
                            st.session_state["user"] = user_profile
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result}")

    # --- TAB 2: REGISTER ---
    with tab_register:
        st.markdown("### New User Registration")
        with st.form("register_form", clear_on_submit=True):
            reg_username = st.text_input("Choose Username", placeholder="At least 3 characters").strip()
            reg_email = st.text_input("Email Address", placeholder="name@example.com").strip()
            reg_password = st.text_input("Password", type="password", placeholder="At least 6 characters").strip()
            reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password").strip()
            submit_register = st.form_submit_button("Create Account", use_container_width=True)

            if submit_register:
                # Client-side form validation
                if len(reg_username) < 3:
                    st.error("Username must be at least 3 characters long.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid email address.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match. Please re-enter carefully.")
                else:
                    reg_payload = {
                        "username": reg_username,
                        "email": reg_email,
                        "password": reg_password
                    }
                    success, result = make_api_request("POST", "/auth/register", data=reg_payload, auth=False)

                    if success:
                        st.success("Account created successfully! You can now sign in using the 'Sign In' tab.")
                    else:
                        st.error(f"Registration failed: {result}")


# ==========================================
# Authenticated Views
# ==========================================
def render_dashboard():
    st.header(":material/insights: Spending Overview & Analytics")

    # Fetch summary from backend
    success, summary = make_api_request("GET", "/expenses/summary")
    if not success:
        st.error(f"Could not load analytics summary: {summary}")
        return

    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    total_spent = summary.get("total_amount", 0.0)
    total_count = summary.get("total_count", 0)
    avg_spent = summary.get("average_amount", 0.0)
    category_breakdown = summary.get("category_breakdown", {})

    top_category = "N/A"
    if category_breakdown:
        top_category = max(category_breakdown, key=category_breakdown.get)

    col1.metric("Total Spent", f"${total_spent:,.2f}")
    col2.metric("Total Transactions", total_count)
    col3.metric("Average Transaction", f"${avg_spent:,.2f}")
    col4.metric("Top Category", top_category)

    st.markdown("---")

    # Visual Charts
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.subheader("Category Distribution")
        if category_breakdown:
            cat_df = pd.DataFrame(
                list(category_breakdown.items()),
                columns=["Category", "Amount ($)"]
            ).sort_values(by="Amount ($)", ascending=False)
            st.bar_chart(cat_df.set_index("Category"))
        else:
            st.info("No expense data recorded yet to display category charts.")

    with col_chart2:
        st.subheader("Category Breakdown Breakdown")
        if category_breakdown:
            st.dataframe(cat_df, use_container_width=True, hide_index=True)
        else:
            st.info("Start adding expenses to view detailed breakdowns.")

    st.markdown("---")
    st.subheader("Recent Expenses")
    recent = summary.get("recent_expenses", [])
    if recent:
        df_recent = pd.DataFrame(recent)[["date", "title", "category", "amount", "description"]]
        df_recent.columns = ["Date", "Title", "Category", "Amount ($)", "Notes"]
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("No recent expenses found.")


def render_add_expense():
    st.header(":material/add_circle: Add New Expense")
    st.markdown("Fill out the form below to record a new personal expense.")

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Expense Title *", placeholder="e.g. Grocery shopping, Gas, Netflix").strip()
            amount = st.number_input("Amount ($) *", min_value=0.01, step=1.0, format="%.2f")
            category = st.selectbox("Category *", CATEGORIES)

        with col2:
            expense_date = st.date_input("Date of Expense *", value=date.today())
            description = st.text_area("Notes / Description (Optional)", placeholder="Add any details, invoice notes, or store name").strip()

        submitted = st.form_submit_button("Save Expense", use_container_width=True)

        if submitted:
            # Form validation
            if not title:
                st.error("Please enter a title for the expense.")
            elif amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                payload = {
                    "title": title,
                    "amount": float(amount),
                    "category": category,
                    "date": expense_date.isoformat(),
                    "description": description if description else None
                }
                success, result = make_api_request("POST", "/expenses/", data=payload)
                if success:
                    st.success(f"Expense '{title}' of ${amount:.2f} successfully saved!")
                else:
                    st.error(f"Failed to create expense: {result}")


def render_manage_expenses():
    st.header(":material/receipt_long: View, Filter & Manage Expenses")

    # Filter section
    with st.expander("Search & Filter Options", expanded=True, icon=":material/search:"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_category = st.selectbox("Filter Category", ["All"] + CATEGORIES)
        with col2:
            start_d = st.date_input("From Date", value=None)
        with col3:
            end_d = st.date_input("To Date", value=None)
        with col4:
            search_query = st.text_input("Keyword Search", placeholder="Title or notes...").strip()

    # Query params for backend API
    params = {}
    if selected_category and selected_category != "All":
        params["category"] = selected_category
    if start_d:
        params["start_date"] = start_d.isoformat()
    if end_d:
        params["end_date"] = end_d.isoformat()
    if search_query:
        params["search"] = search_query

    # Fetch filtered expenses
    success, expenses = make_api_request("GET", "/expenses/", params=params)

    if not success:
        st.error(f"Error fetching expenses: {expenses}")
        return

    if not expenses:
        st.info("No expenses found matching the selected criteria. Try adjusting your filters or add a new expense!")
        return

    # Convert to pandas DataFrame for clean tabular display
    df = pd.DataFrame(expenses)
    display_df = df[["id", "date", "title", "category", "amount", "description"]].copy()
    display_df.columns = ["ID", "Date", "Title", "Category", "Amount ($)", "Notes"]
    display_df["Amount ($)"] = display_df["Amount ($)"].map(lambda x: f"${x:,.2f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(expenses)} expense record(s).")

    # Edit & Delete Action Panel
    st.markdown("---")
    st.subheader(":material/tune: Manage Selected Expense")
    expense_ids = [e["id"] for e in expenses]

    col_select, col_actions = st.columns([1, 2])
    with col_select:
        selected_id = st.selectbox("Select Expense ID to Edit or Delete", expense_ids)

    # Find the selected item
    selected_expense = next((e for e in expenses if e["id"] == selected_id), None)

    if selected_expense:
        tab_edit, tab_delete = st.tabs([":material/edit: Edit Expense", ":material/delete: Delete Expense"])

        # --- EDIT FORM ---
        with tab_edit:
            with st.form(f"edit_form_{selected_id}"):
                c1, c2 = st.columns(2)
                with c1:
                    new_title = st.text_input("Title", value=selected_expense["title"]).strip()
                    new_amount = st.number_input(
                        "Amount ($)",
                        value=float(selected_expense["amount"]),
                        min_value=0.01,
                        step=1.0,
                        format="%.2f"
                    )
                    default_cat_index = CATEGORIES.index(selected_expense["category"]) if selected_expense["category"] in CATEGORIES else 0
                    new_category = st.selectbox("Category", CATEGORIES, index=default_cat_index)

                with c2:
                    current_date_val = datetime.strptime(selected_expense["date"], "%Y-%m-%d").date()
                    new_date = st.date_input("Date", value=current_date_val)
                    new_description = st.text_area("Notes", value=selected_expense.get("description") or "").strip()

                save_update = st.form_submit_button("Update Expense", use_container_width=True)

                if save_update:
                    if not new_title:
                        st.error("Title cannot be empty.")
                    elif new_amount <= 0:
                        st.error("Amount must be greater than zero.")
                    else:
                        update_payload = {
                            "title": new_title,
                            "amount": float(new_amount),
                            "category": new_category,
                            "date": new_date.isoformat(),
                            "description": new_description if new_description else None
                        }
                        update_ok, update_res = make_api_request("PUT", f"/expenses/{selected_id}", data=update_payload)
                        if update_ok:
                            st.success(f"Expense #{selected_id} updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to update expense: {update_res}")

        # --- DELETE ACTION ---
        with tab_delete:
            st.warning(f"Are you sure you want to delete **'{selected_expense['title']}'** (${selected_expense['amount']:.2f})?")
            if st.button("Confirm Delete", type="primary", use_container_width=True):
                del_ok, del_res = make_api_request("DELETE", f"/expenses/{selected_id}")
                if del_ok:
                    st.success(f"Expense #{selected_id} deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to delete expense: {del_res}")


# ==========================================
# Main App Router
# ==========================================
def main():
    # If user is not authenticated, show login/register
    if not st.session_state["token"]:
        render_auth_page()
        return

    # User is logged in: show sidebar & navigation
    user_info = st.session_state.get("user") or {}
    username = user_info.get("username", "User")
    email = user_info.get("email", "")

    # Sidebar
    with st.sidebar:
        st.markdown("### :material/account_balance_wallet: Expense Tracker")
        st.write(f"Logged in as: **{username}**")
        if email:
            st.caption(f"Email: {email}")

        st.markdown("---")
        menu_selection = st.radio(
            "Navigation",
            [":material/dashboard: Dashboard", ":material/add_circle: Add Expense", ":material/receipt_long: Manage Expenses"],
            index=0
        )

        st.markdown("---")
        if st.button("Sign Out", icon=":material/logout:", use_container_width=True):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()

        st.markdown("---")
        st.caption("Sprint 01 - Nolyth Backend Foundations")
        st.caption("FastAPI • SQLite • Streamlit")

    # Render selected view
    if menu_selection == ":material/dashboard: Dashboard":
        render_dashboard()
    elif menu_selection == ":material/add_circle: Add Expense":
        render_add_expense()
    elif menu_selection == ":material/receipt_long: Manage Expenses":
        render_manage_expenses()


if __name__ == "__main__":
    main()
