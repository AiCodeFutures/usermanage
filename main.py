import streamlit as st
import database  # 使用 database.py 中的所有数据库操作函数
import pandas as pd
import datetime
import hashlib

# 设置页面配置
st.set_page_config(
    page_title="用户管理系统",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库及表
database.init_db()

# 密码哈希函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 登录函数
def login_page():
    st.header("用户登录")
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("邮箱", placeholder="请输入邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        submitted = st.form_submit_button("登录")

        if submitted:
            hashed_password = hash_password(password)
            user = database.authenticate_user(email, hashed_password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = user['username']
                st.session_state['user_id'] = user['id']
                # 存储 is_admin 状态
                st.session_state['is_admin'] = bool(user.get('is_admin', 0))
                st.success(f"欢迎回来, {user['username']}!")
                st.rerun()
            else:
                st.error("邮箱或密码错误")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['user_id'] = None
    # 清除 is_admin 状态
    if 'is_admin' in st.session_state:
        del st.session_state['is_admin']
    st.info("您已退出登录。")
    st.rerun()

# 管理用户权限函数
def manage_user_permissions_page():
    st.header("管理用户权限")

    if not st.session_state.get('is_admin'):
        st.warning("您没有权限访问此页面。")
        return

    users = database.get_all_users()
    if not users:
        st.info("系统中还没有用户。")
        return

    st.markdown("请勾选或取消勾选以设置用户的管理员权限：")

    for user in users:
        # 避免管理员自己取消自己的管理员权限，或者普通用户修改权限
        if user['id'] == st.session_state['user_id']:
            st.checkbox(f"用户ID: {user['id']} - {user['username']} ({user['email']}) - (您自己)", value=bool(user['is_admin']), disabled=True, key=f"admin_checkbox_{user['id']}")
        else:
            is_admin_current = bool(user['is_admin'])
            is_admin_new = st.checkbox(f"用户ID: {user['id']} - {user['username']} ({user['email']})", value=is_admin_current, key=f"admin_checkbox_{user['id']}")

            if is_admin_new != is_admin_current:
                # 更新用户的 is_admin 状态
                try:
                    # database.update_user 应该能够处理 is_admin 字段的更新
                    # 假设 update_user 接受 is_admin 参数
                    updated = database.update_user(user['id'], is_admin=is_admin_new)
                    if updated:
                        st.success(f"用户 {user['username']} 的管理员权限已更新为: {is_admin_new}")
                        st.rerun() # 刷新页面以显示最新状态
                    else:
                        st.error(f"更新用户 {user['username']} 的管理员权限失败。")
                except Exception as e:
                    st.error(f"更新权限时发生错误: {e}")


# 注册函数
def register_page():
    st.header("用户注册")
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("用户名", placeholder="请输入用户名")
        email = st.text_input("邮箱", placeholder="请输入邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        # 添加身高、体重、年龄输入字段
        col_h_w_a1, col_h_w_a2, col_h_w_a3 = st.columns(3)
        with col_h_w_a1:
            height = st.number_input("身高 (cm)", min_value=0.0, format="%.1f", help="请输入您的身高（厘米）")
        with col_h_w_a2:
            weight = st.number_input("体重 (kg)", min_value=0.0, format="%.1f", help="请输入您的体重（千克）")
        with col_h_w_a3:
            age = st.number_input("年龄", min_value=0, format="%d", help="请输入您的年龄")

        remark = st.text_area("备注 (可选)", placeholder="请输入备注信息")
        submitted = st.form_submit_button("注册")

        if submitted:
            if not username or not email or not password or not confirm_password:
                st.error("所有必填项都不能为空！")
            elif password != confirm_password:
                st.error("两次输入的密码不一致！")
            elif '@' not in email:
                st.error("请输入有效的邮箱地址！")
            else:
                try:
                    hashed_password = hash_password(password)
                    
                    # 格式化身高、体重、年龄信息
                    personal_info = f"身高:{height:.1f}cm,体重:{weight:.1f}kg,年龄:{age}岁"
                    
                    # 将个人信息添加到备注中
                    if remark.strip():
                        final_remark = f"{remark.strip()}; {personal_info}"
                    else:
                        final_remark = personal_info

                    # 传递身高、体重、年龄参数给 create_user 函数
                    new_id = database.create_user(username, email, hashed_password, final_remark, height=height, weight=weight, age=age)
                    st.success(f"用户 {username} 注册成功！用户ID: {new_id}")
                except Exception as e:
                    st.error(f"注册失败: {str(e)}")

# 主应用逻辑
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("用户管理系统")
    st.sidebar.markdown("### 认证")
    auth_menu = st.sidebar.radio("", ("登录", "注册"))
    if auth_menu == "登录":
        login_page()
    elif auth_menu == "注册":
        register_page()
else:
    # 使用自定义样式的标题
    st.title("用户管理系统")

    # 侧边栏设计
    with st.sidebar:
        st.image("https://www.svgrepo.com/show/530443/user-management.svg", width=80)
        st.markdown(f"### 欢迎, {st.session_state['username']}!")
        st.markdown("### 导航菜单")
        
        # 根据用户是否为管理员来构建菜单选项
        menu_options = ["列出所有用户", "添加用户", "更新用户", "搜索用户"]
        if st.session_state.get('is_admin'): # 检查session_state中是否有is_admin且为True
            menu_options.append("删除用户")
            menu_options.append("管理用户权限") # 添加新的管理员菜单项
            
        menu = st.selectbox("请选择操作", menu_options)
        st.button("退出登录", on_click=logout)

        st.markdown("---")
        st.markdown("### 系统信息")
        st.info(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("**版本:** 1.0.0")
        st.markdown("**作者:** Boyji")
        st.markdown("---")
        st.markdown("<small>© 2023 用户管理系统</small>", unsafe_allow_html=True)

    if menu == "列出所有用户":
        st.header("用户列表")

        # 分页逻辑
        page_size = st.slider("每页显示用户数", 5, 50, 10)
        total_users = database.get_total_users_count()
        total_pages = (total_users + page_size - 1) // page_size

        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 1

        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("上一页", disabled=(st.session_state['current_page'] == 1)):
                st.session_state['current_page'] -= 1
                st.rerun()
        with col_info:
            st.markdown(f"<div style='text-align:center;'>第 <b>{st.session_state['current_page']}</b> / <b>{total_pages}</b> 页</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("下一页", disabled=(st.session_state['current_page'] == total_pages)):
                st.session_state['current_page'] += 1
                st.rerun()

        skip = (st.session_state['current_page'] - 1) * page_size
        limit = page_size

        # 获取用户数据并转换为DataFrame以美化显示
        users = database.get_all_users(skip=skip, limit=limit)
        if users:
            df = pd.DataFrame(users)
            # 重新排列列的顺序
            columns_order = ['id', 'username', 'email', 'remark', 'created_at']
            df = df[columns_order]
            # 重命名列
            df.columns = ['ID', '用户名', '邮箱', '备注', '创建时间']

            # 添加操作按钮的占位符
            st.dataframe(df, use_container_width=True)

            # 显示用户总数
            st.info(f"系统中共有 **{total_users}** 个用户")
        else:
            st.info("当前页没有用户数据。")
            if total_users == 0:
                st.info("系统中还没有用户，请添加新用户")

    elif menu == "添加用户":
        st.header("添加新用户")

        # 使用列布局美化表单
        col1, col2 = st.columns(2)

        with st.form("add_user_form", border=False):
            with col1:
                username = st.text_input("👤 用户名", placeholder="请输入用户名")
            with col2:
                email = st.text_input("📧 邮箱", placeholder="请输入邮箱地址")
            password = st.text_input("🔑 密码", type="password", placeholder="请输入密码")
            remark = st.text_area("📝 备注", placeholder="请输入备注信息（可选）", height=100)

            # 添加分隔线
            st.markdown("---")

            submitted = st.form_submit_button("✅ 添加用户", use_container_width=True)
            if submitted:
                if not username or not email or not password:
                    st.error("用户名、邮箱和密码不能为空！")
                elif '@' not in email:
                    st.error("请输入有效的邮箱地址！")
                else:
                    try:
                        hashed_password = hash_password(password)
                        new_id = database.create_user(username, email, hashed_password, remark)
                        st.success(f"用户已成功添加！\n用户ID: **{new_id}**")
                    except Exception as e:
                        st.error(f"添加用户失败: {str(e)}")

    elif menu == "更新用户":
        st.header("更新用户信息")

        # 获取所有用户，用于选择
        users = database.get_all_users()
        if not users:
            st.info("系统中还没有用户，请先添加用户")
        else:
            # 创建用户ID选择器
            user_options = {f"{user['id']} - {user['username']}": user['id'] for user in users} 
            selected_user_option = st.selectbox("👤 选择要更新的用户", options=list(user_options.keys()))
            selected_user_id = user_options[selected_user_option]

            # 获取当前用户信息
            current_user = database.get_user_by_id(selected_user_id)

            if current_user:
                st.subheader("当前用户信息")
                current_info = f"**ID:** {current_user['id']}\n**用户名:** {current_user['username']}\n**邮箱:** {current_user['email']}\n**备注:** {current_user['remark'] or '无'}\n**创建时间:** {current_user['created_at']}"
                st.info(current_info)

                st.subheader("输入新信息")
                with st.form("update_user_form", border=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        username = st.text_input("👤 新用户名", placeholder="留空不更新", value="")
                    with col2:
                        email = st.text_input("📧 新邮箱", placeholder="留空不更新", value="")

                    password = st.text_input("🔑 新密码", type="password", placeholder="留空不更新", value="")
                    remark = st.text_area("📝 新备注", placeholder="留空不更新", height=100, value="")

                    st.markdown("---")
                    submitted = st.form_submit_button("🔄 更新用户信息", use_container_width=True)

                    if submitted:
                        username = username if username.strip() != "" else None
                        email = email if email.strip() != "" else None
                        password = hash_password(password) if password.strip() != "" else None
                        remark = remark if remark.strip() != "" else None

                        if not username and not email and not password and not remark:
                            st.error("请至少填写一项要更新的信息")
                        elif email and '@' not in email:
                            st.error("请输入有效的邮箱地址")
                        else:
                            try:
                                updated = database.update_user(selected_user_id, username, email, password, remark)
                                if updated:
                                    st.success("用户信息已成功更新！")
                                    # 刷新页面以显示更新后的信息
                                    st.rerun()
                                else:
                                    st.error("更新失败，没有更新的字段或用户不存在")
                            except Exception as e:
                                st.error(f"更新用户失败: {str(e)}")

    elif menu == "删除用户":
        st.header("删除用户")

        # 获取所有用户，用于选择
        users = database.get_all_users()
        if not users:
            st.info("系统中还没有用户，请先添加用户")
        else:
            st.warning("⚠️ 警告：删除操作不可恢复，请谨慎操作！")

            # 创建用户ID选择器
            user_options = {f"{user['id']} - {user['username']} ({user['email']})": user['id'] for user in users}
            selected_user_option = st.selectbox("👤 选择要删除的用户", options=list(user_options.keys()))
            selected_user_id = user_options[selected_user_option]

            # 添加密码输入框
            password_to_confirm = st.text_input("🔑 请输入您的密码以确认删除", type="password")

            if st.button("❌ 确认删除", use_container_width=True):
                # 获取当前登录用户的ID
                current_user_id = st.session_state.get('user_id')
                if current_user_id is None:
                    st.error("请先登录才能执行删除操作。")
                else:
                    # 获取当前登录用户的完整信息，包括密码
                    current_user_data = database.get_user_by_id(current_user_id)
                    if current_user_data and 'password' in current_user_data:
                        hashed_input_password = hashlib.sha256(password_to_confirm.encode()).hexdigest()
                        if hashed_input_password == current_user_data['password']:
                            try:
                                deleted = database.delete_user(selected_user_id)
                                if deleted:
                                    st.success("用户已成功删除！")
                                    st.rerun()
                                else:
                                    st.error("删除失败，用户不存在")
                            except Exception as e:
                                st.error(f"删除用户失败: {str(e)}")
                        else:
                            st.error("密码不正确，无法删除用户。")
                    else:
                        st.error("无法获取当前登录用户的信息或密码，请联系管理员。")

    elif menu == "搜索用户":
        st.header("搜索用户")
        search_query = st.text_input("🔍 输入用户名或邮箱进行搜索", placeholder="支持模糊搜索")

        if search_query:
            search_results = database.search_users(search_query)
            if search_results:
                df_search = pd.DataFrame(search_results)
                columns_order = ['id', 'username', 'email', 'remark', 'created_at']
                df_search = df_search[columns_order]
                df_search.columns = ['ID', '用户名', '邮箱', '备注', '创建时间']
                st.dataframe(df_search, use_container_width=True)
            else:
                st.info("没有找到匹配的用户。")
    elif menu == "管理用户权限": # 新增的菜单项处理
        manage_user_permissions_page()
