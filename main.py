import streamlit as st
import pandas as pd
import datetime
import hashlib
import requests
import os

# --- API Configuration ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- Page Configuration ---
st.set_page_config(
    page_title="用户管理系统",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

def hash_password(password):
    """
    Hashes a password using SHA256. 
    This is now only used for client-side password verification for critical actions.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def handle_api_error(response, context="操作"):
    """Generic error handler for API responses."""
    try:
        detail = response.json().get("detail", "未知错误")
    except requests.exceptions.JSONDecodeError:
        detail = response.text
    st.error(f"{context}失败: {detail} (状态码: {response.status_code})")

# --- Authentication Pages ---

def login_page():
    st.header("用户登录")
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("邮箱", placeholder="请输入邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submitted = st.form_submit_button("登录")

        if submitted:
            try:
                response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                if response.ok:
                    user = response.json()
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user['username']
                    st.session_state['user_id'] = user['id']
                    st.session_state['email'] = user['email'] # Store email in session state
                    st.session_state['is_admin'] = bool(user.get('is_admin', False))
                    st.success(f"欢迎回来, {user['username']}!")
                    st.rerun()
                else:
                    handle_api_error(response, "登录")
            except requests.exceptions.RequestException as e:
                st.error(f"登录请求失败: {e}")

def logout():
    st.session_state.clear()
    st.info("您已退出登录。")
    st.rerun()

def register_page():
    st.header("用户注册")
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("用户名", placeholder="请输入用户名")
        email = st.text_input("邮箱", placeholder="请输入邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            height = st.number_input("身高 (cm)", min_value=0.0, format="%.1f")
        with col2:
            weight = st.number_input("体重 (kg)", min_value=0.0, format="%.1f")
        with col3:
            age = st.number_input("年龄", min_value=0, format="%d")

        remark = st.text_area("备注 (可选)", placeholder="请输入备注信息")
        submitted = st.form_submit_button("注册")

        if submitted:
            if not all([username, email, password, confirm_password]):
                st.error("所有必填项都不能为空！")
            elif password != confirm_password:
                st.error("两次输入的密码不一致！")
            elif '@' not in email:
                st.error("请输入有效的邮箱地址！")
            else:
                user_data = {
                    "username": username,
                    "email": email,
                    "password": password, # Sending plain password to API
                    "remark": remark,
                    "height": height,
                    "weight": weight,
                    "age": age,
                }
                try:
                    response = requests.post(f"{API_URL}/users", json=user_data)
                    if response.status_code == 201:
                        new_user = response.json()
                        st.success(f"用户 {new_user['username']} 注册成功！用户ID: {new_user['id']}")
                    else:
                        handle_api_error(response, "注册")
                except requests.exceptions.RequestException as e:
                    st.error(f"注册请求失败: {e}")

# --- Main Application Logic ---

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("用户管理系统")
    st.sidebar.markdown("### 认证")
    auth_menu = st.sidebar.radio("", ("登录", "注册"))
    if auth_menu == "登录":
        login_page()
    else:
        register_page()
else:
    st.title("用户管理系统")

    # Sidebar
    with st.sidebar:
        st.image("https://www.svgrepo.com/show/530443/user-management.svg", width=80)
        st.markdown(f"### 欢迎, {st.session_state['username']}!")
        
        menu_options = ["列出所有用户", "添加用户", "更新用户", "搜索用户"]
        if st.session_state.get('is_admin'):
            menu_options.extend(["删除用户", "管理用户权限"])
        menu_options.append("智能身材方案")  # Add AI plan menu for logged in users
            
        menu = st.selectbox("请选择操作", menu_options)
        st.button("退出登录", on_click=logout)

        st.markdown("---")
        st.info(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("<small>© 2024 用户管理系统 API版</small>", unsafe_allow_html=True)

    # --- Page Content ---

    if menu == "列出所有用户":
        st.header("用户列表")
        try:
            count_response = requests.get(f"{API_URL}/users/count")
            if not count_response.ok:
                handle_api_error(count_response, "获取用户总数")
                st.stop()
            total_users = count_response.json()

            if total_users > 0:
                page_size = st.slider("每页显示用户数", 5, 50, 10)
                total_pages = (total_users + page_size - 1) // page_size
                current_page = st.number_input('页码', min_value=1, max_value=total_pages, value=1)
                
                skip = (current_page - 1) * page_size
                users_response = requests.get(f"{API_URL}/users", params={"skip": skip, "limit": page_size})
                
                if users_response.ok:
                    users = users_response.json()
                    df = pd.DataFrame(users)
                    st.dataframe(df[['id', 'username', 'email', 'remark', 'is_admin', 'height', 'weight', 'age', 'created_at']], use_container_width=True)
                    st.info(f"显示第 {current_page}/{total_pages} 页，共 {total_users} 个用户")
                else:
                    handle_api_error(users_response, "获取用户列表")
            else:
                st.info("系统中还没有用户，请添加新用户。")

        except requests.exceptions.RequestException as e:
            st.error(f"无法连接到API: {e}")

    elif menu == "添加用户":
        st.header("添加新用户")
        with st.form("add_user_form", border=False):
            username = st.text_input("👤 用户名")
            email = st.text_input("📧 邮箱")
            password = st.text_input("🔑 密码", type="password")
            remark = st.text_area("📝 备注")
            submitted = st.form_submit_button("✅ 添加用户")
            if submitted:
                if not all([username, email, password]):
                    st.error("用户名、邮箱和密码不能为空！")
                else:
                    try:
                        response = requests.post(f"{API_URL}/users", json={"username": username, "email": email, "password": password, "remark": remark})
                        if response.status_code == 201:
                            st.success(f"用户 {username} 已成功添加！")
                        else:
                            handle_api_error(response, "添加用户")
                    except requests.exceptions.RequestException as e:
                        st.error(f"请求失败: {e}")

    elif menu == "更新用户":
        st.header("更新用户信息")
        try:
            users_response = requests.get(f"{API_URL}/users", params={"limit": 1000}) # Fetch all for dropdown
            if not users_response.ok:
                handle_api_error(users_response, "获取用户列表")
                st.stop()
            
            users = users_response.json()
            if not users:
                st.info("系统中还没有用户。")
            else:
                user_options = {f"{user['id']} - {user['username']}": user['id'] for user in users}
                selected_key = st.selectbox("👤 选择要更新的用户", options=list(user_options.keys()))
                selected_id = user_options[selected_key]

                with st.form("update_user_form"):
                    st.write(f"正在更新用户ID: {selected_id}")
                    username = st.text_input("新用户名", placeholder="留空不更新")
                    email = st.text_input("新邮箱", placeholder="留空不更新")
                    password = st.text_input("新密码", type="password", placeholder="留空不更新")
                    remark = st.text_area("新备注", placeholder="留空不更新")
                    submitted = st.form_submit_button("🔄 更新用户信息")

                    if submitted:
                        update_data = {k: v for k, v in {
                            "username": username, "email": email, "password": password, "remark": remark
                        }.items() if v}
                        
                        if not update_data:
                            st.warning("未输入任何要更新的信息。")
                        else:
                            response = requests.put(f"{API_URL}/users/{selected_id}", json=update_data)
                            if response.ok:
                                st.success("用户信息已成功更新！")
                                st.rerun()
                            else:
                                handle_api_error(response, "更新用户")
        except requests.exceptions.RequestException as e:
            st.error(f"无法连接到API: {e}")

    elif menu == "删除用户" and st.session_state.get('is_admin'):
        st.header("删除用户")
        try:
            users_response = requests.get(f"{API_URL}/users", params={"limit": 1000})
            if not users_response.ok:
                handle_api_error(users_response, "获取用户列表")
                st.stop()

            users = users_response.json()
            if not users:
                st.info("系统中还没有用户。")
            else:
                st.warning("⚠️ 警告：删除操作不可恢复！")
                user_options = {f"{user['id']} - {user['username']}": user['id'] for user in users}
                selected_id = user_options[st.selectbox("👤 选择要删除的用户", options=list(user_options.keys()))]
                
                password_to_confirm = st.text_input("🔑 请输入您的登录密码以确认删除", type="password")

                if st.button("❌ 确认删除"):
                    if not password_to_confirm:
                        st.error("请输入您的密码以确认操作。")
                    else:
                        # Authenticate admin before deleting
                        admin_email = st.session_state.get('email')
                        if not admin_email:
                            st.error("无法获取管理员邮箱，请重新登录。")
                            st.stop()

                        login_response = requests.post(f"{API_URL}/login", json={"email": admin_email, "password": password_to_confirm})
                        if login_response.ok:
                            delete_response = requests.delete(f"{API_URL}/users/{selected_id}")
                            if delete_response.status_code == 204:
                                st.success("用户已成功删除！")
                                st.rerun()
                            else:
                                handle_api_error(delete_response, "删除用户")
                        else:
                            st.error("密码不正确，无法授权删除操作。")

        except requests.exceptions.RequestException as e:
            st.error(f"无法连接到API: {e}")


    elif menu == "搜索用户":
        st.header("搜索用户")
        search_query = st.text_input("🔍 输入用户名或邮箱进行搜索")
        if search_query:
            try:
                response = requests.get(f"{API_URL}/users/search", params={"query": search_query})
                if response.ok:
                    results = response.json()
                    if results:
                        st.dataframe(pd.DataFrame(results), use_container_width=True)
                    else:
                        st.info("没有找到匹配的用户。")
                else:
                    handle_api_error(response, "搜索用户")
            except requests.exceptions.RequestException as e:
                st.error(f"请求失败: {e}")

    elif menu == "管理用户权限" and st.session_state.get('is_admin'):
        st.header("管理用户权限")
        try:
            response = requests.get(f"{API_URL}/users", params={"limit": 1000})
            if not response.ok:
                handle_api_error(response, "获取用户列表")
                st.stop()

            users = response.json()
            for user in users:
                is_admin_current = bool(user['is_admin'])
                # Admin cannot change their own status
                if user['id'] == st.session_state['user_id']:
                    st.checkbox(f"{user['username']} ({user['email']})", value=is_admin_current, disabled=True, key=f"admin_{user['id']}")
                else:
                    if st.checkbox(f"{user['username']} ({user['email']})", value=is_admin_current, key=f"admin_{user['id']}") != is_admin_current:
                        update_response = requests.put(f"{API_URL}/users/{user['id']}", json={"is_admin": not is_admin_current})
                        if update_response.ok:
                            st.success(f"用户 {user['username']} 的权限已更新。")
                            st.rerun()
                        else:
                            handle_api_error(update_response, "更新权限")
        except requests.exceptions.RequestException as e:
            st.error(f"无法连接到API: {e}")

    elif menu == "智能身材方案":
        st.header("智能身材控制方案 (DeepSeek)")
        st.markdown("输入你的基本数据，获取 BMI 与 AI 生成的 7 日方案。")
        with st.form("bmi_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                height = st.number_input("身高(cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
            with col2:
                weight = st.number_input("体重(kg)", min_value=20.0, max_value=300.0, value=65.0, step=0.1)
            with col3:
                age = st.number_input("年龄", min_value=5, max_value=100, value=30, step=1)
            gender = st.selectbox("性别", ["未提供", "男", "女"], index=0)
            
            goal_options = {
                "未明确": "not_specified",
                "减脂": "fat_loss",
                "增肌": "muscle_gain",
                "身体重组": "recomposition"
            }
            selected_goal_label = st.selectbox("目标", list(goal_options.keys()), index=0)
            goal = goal_options[selected_goal_label]

            submitted = st.form_submit_button("生成方案")
        if submitted:
            
            gender_map = {"男": "male", "女": "female"}
            
            payload = {
                "height": height,
                "weight": weight,
                "age": age,
                "gender": gender_map.get(gender),
                "goal": None if goal == "not_specified" else goal,
                "user_id": st.session_state['user_id']  # 关联当前用户
            }
            try:
                resp = requests.post(f"{API_URL}/bmi/plan", json=payload, timeout=60)
                if resp.ok:
                    data = resp.json()
                    st.subheader("基础指标")
                    st.write(f"BMI: {data['bmi']} ({data['bmi_category']})")
                    st.info(data['suggestion'])
                    if data.get('ai_plan'):
                        st.subheader("AI 方案")
                        st.markdown(data['ai_plan'])
                    else:
                        st.warning("未生成 AI 方案 (可能未配置密钥)")
                else:
                    try:
                        detail = resp.json().get('detail')
                    except Exception:
                        detail = resp.text
                    st.error(f"生成失败: {detail}")
            except requests.exceptions.RequestException as e:
                st.error(f"请求异常: {e}")

        # 显示历史方案
        st.markdown("---")
        st.subheader("历史方案记录")
        try:
            plans_response = requests.get(f"{API_URL}/users/{st.session_state['user_id']}/plans")
            if plans_response.ok:
                plans = plans_response.json()
                if not plans:
                    st.info("暂无历史方案记录。")
                else:
                    for i, plan in enumerate(plans):
                        with st.expander(f"方案 {i+1} - {plan['created_at']}"):
                            st.write(f"**BMI:** {plan['bmi']} ({plan['bmi_category']})")
                            st.write(f"**基础建议:** {plan['suggestion']}")
                            st.markdown("**AI 方案:**")
                            st.markdown(plan['ai_plan'])
                            
                            # 准备下载内容
                            download_content = f"""
# 智能身材方案 ({plan['created_at']})

## 基础指标
- **BMI:** {plan['bmi']} ({plan['bmi_category']})
- **基础建议:** {plan['suggestion']}

## AI 智能方案
{plan['ai_plan']}
"""
                            st.download_button(
                                label="下载此方案 (Markdown)",
                                data=download_content,
                                file_name=f"plan_{plan['id']}_{plan['created_at']}.md",
                                mime="text/markdown",
                                key=f"download_{plan['id']}"
                            )
            else:
                handle_api_error(plans_response, "获取历史方案")
        except requests.exceptions.RequestException as e:
            st.error(f"获取历史方案失败: {e}")
