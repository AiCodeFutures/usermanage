import streamlit as st
import database  # 使用 database.py 中的所有数据库操作函数
import pandas as pd
import datetime

# 设置页面配置
st.set_page_config(
    page_title="用户管理系统",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E3F2FD;
        margin-bottom: 2rem;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .error-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .info-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
    }
    .stButton>button {
        background-color: #1976D2;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化数据库及表
database.init_db()

# 使用自定义样式的标题
st.markdown('<h1 class="main-header">用户管理系统</h1>', unsafe_allow_html=True)

# 侧边栏设计
with st.sidebar:
    st.image("https://www.svgrepo.com/show/530443/user-management.svg", width=80)
    st.markdown("### 导航菜单")
    menu = st.selectbox("请选择操作", ("列出所有用户", "添加用户", "更新用户", "删除用户", "搜索用户"))
    
    st.markdown("---")
    st.markdown("### 系统信息")
    st.info(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**版本:** 1.0.0")
    st.markdown("**作者:** Boyji")
    st.markdown("---")
    st.markdown("<small>© 2023 用户管理系统</small>", unsafe_allow_html=True)

if menu == "列出所有用户":
    st.markdown('<h2 class="sub-header">用户列表</h2>', unsafe_allow_html=True)
    
    # 获取用户数据并转换为DataFrame以美化显示
    users = database.get_all_users()
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
        st.markdown(f"<div class='info-msg'>系统中共有 <b>{len(users)}</b> 个用户</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-msg'>系统中还没有用户，请添加新用户</div>", unsafe_allow_html=True)

elif menu == "添加用户":
    st.markdown('<h2 class="sub-header">添加新用户</h2>', unsafe_allow_html=True)
    
    # 使用列布局美化表单
    col1, col2 = st.columns(2)
    
    with st.form("add_user_form", border=False):
        with col1:
            username = st.text_input("👤 用户名", placeholder="请输入用户名")
        with col2:
            email = st.text_input("📧 邮箱", placeholder="请输入邮箱地址")
        
        remark = st.text_area("📝 备注", placeholder="请输入备注信息（可选）", height=100)
        
        # 添加分隔线
        st.markdown("---")
        
        submitted = st.form_submit_button("✅ 添加用户", use_container_width=True)
        if submitted:
            if not username or not email:
                st.markdown("<div class='error-msg'>用户名和邮箱不能为空！</div>", unsafe_allow_html=True)
            elif '@' not in email:
                st.markdown("<div class='error-msg'>请输入有效的邮箱地址！</div>", unsafe_allow_html=True)
            else:
                try:
                    new_id = database.create_user(username, email, remark)
                    st.markdown(f"<div class='success-msg'>用户已成功添加！<br>用户ID: <b>{new_id}</b></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='error-msg'>添加用户失败: {str(e)}</div>", unsafe_allow_html=True)

elif menu == "更新用户":
    st.markdown('<h2 class="sub-header">更新用户信息</h2>', unsafe_allow_html=True)
    
    # 获取所有用户，用于选择
    users = database.get_all_users()
    if not users:
        st.markdown("<div class='info-msg'>系统中还没有用户，请先添加用户</div>", unsafe_allow_html=True)
    else:
        # 创建用户ID选择器
        user_options = {f"{user['id']} - {user['username']}": user['id'] for user in users}
        selected_user_option = st.selectbox("👤 选择要更新的用户", options=list(user_options.keys()))
        selected_user_id = user_options[selected_user_option]
        
        # 获取当前用户信息
        current_user = database.get_user_by_id(selected_user_id)
        
        if current_user:
            st.markdown("### 当前用户信息")
            current_info = f"**ID:** {current_user['id']}\n**用户名:** {current_user['username']}\n**邮箱:** {current_user['email']}\n**备注:** {current_user['remark'] or '无'}\n**创建时间:** {current_user['created_at']}"
            st.markdown(f"<div class='info-msg'>{current_info}</div>", unsafe_allow_html=True)
            
            st.markdown("### 输入新信息")
            with st.form("update_user_form", border=False):
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("👤 新用户名", placeholder="留空不更新", value="")
                with col2:
                    email = st.text_input("📧 新邮箱", placeholder="留空不更新", value="")
                
                remark = st.text_area("📝 新备注", placeholder="留空不更新", height=100, value="")
                
                st.markdown("---")
                submitted = st.form_submit_button("🔄 更新用户信息", use_container_width=True)
                
                if submitted:
                    username = username if username.strip() != "" else None
                    email = email if email.strip() != "" else None
                    remark = remark if remark.strip() != "" else None
                    
                    if not username and not email and not remark:
                        st.markdown("<div class='error-msg'>请至少填写一项要更新的信息</div>", unsafe_allow_html=True)
                    elif email and '@' not in email:
                        st.markdown("<div class='error-msg'>请输入有效的邮箱地址</div>", unsafe_allow_html=True)
                    else:
                        try:
                            updated = database.update_user(selected_user_id, username, email, remark)
                            if updated:
                                st.markdown("<div class='success-msg'>用户信息已成功更新！</div>", unsafe_allow_html=True)
                                # 刷新页面以显示更新后的信息
                                st.rerun()
                            else:
                                st.markdown("<div class='error-msg'>更新失败，没有更新的字段或用户不存在</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f"<div class='error-msg'>更新用户失败: {str(e)}</div>", unsafe_allow_html=True)

elif menu == "删除用户":
    st.markdown('<h2 class="sub-header">删除用户</h2>', unsafe_allow_html=True)
    
    # 获取所有用户，用于选择
    users = database.get_all_users()
    if not users:
        st.markdown("<div class='info-msg'>系统中还没有用户，请先添加用户</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ 警告：删除操作不可恢复，请谨慎操作！")
        
        # 创建用户ID选择器
        user_options = {f"{user['id']} - {user['username']} ({user['email']})": user['id'] for user in users}
        selected_user_option = st.selectbox("👤 选择要删除的用户", options=list(user_options.keys()))
        selected_user_id = user_options[selected_user_option]
        
        # 获取当前用户信息
        current_user = database.get_user_by_id(selected_user_id)
        
        if current_user:
            st.markdown("### 用户信息确认")
            current_info = f"**ID:** {current_user['id']}\n**用户名:** {current_user['username']}\n**邮箱:** {current_user['email']}\n**备注:** {current_user['remark'] or '无'}\n**创建时间:** {current_user['created_at']}"
            st.markdown(f"<div class='error-msg'>{current_info}</div>", unsafe_allow_html=True)
            
            # 使用确认机制
            confirm = st.checkbox("我确认要删除此用户，此操作不可恢复")
            
            if confirm:
                if st.button("🗑️ 确认删除", type="primary", use_container_width=True):
                    try:
                        if database.delete_user(selected_user_id):
                            st.markdown("<div class='success-msg'>用户已成功删除！</div>", unsafe_allow_html=True)
                            # 短暂延迟后刷新页面
                            st.rerun()
                        else:
                            st.markdown("<div class='error-msg'>删除失败，用户可能不存在</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"<div class='error-msg'>删除用户失败: {str(e)}</div>", unsafe_allow_html=True)
            else:
                st.button("🗑️ 确认删除", disabled=True, use_container_width=True)

elif menu == "搜索用户":
    st.markdown('<h2 class="sub-header">搜索用户</h2>', unsafe_allow_html=True)
    
    # 创建搜索表单
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 请输入用户名或邮箱关键字", placeholder="输入关键字进行搜索")
    with col2:
        search_button = st.button("🔍 搜索", use_container_width=True)
    
    # 添加搜索选项
    search_options = st.radio(
        "搜索范围",
        options=["全部字段", "仅用户名", "仅邮箱", "仅备注"],
        horizontal=True
    )
    
    if search_button or search_query:  # 允许在输入时自动搜索
        if not search_query.strip():
            st.markdown("<div class='info-msg'>请输入搜索关键字</div>", unsafe_allow_html=True)
        else:
            users = database.get_all_users()
            
            # 根据搜索选项过滤
            if search_options == "全部字段":
                filtered = [user for user in users 
                           if search_query.lower() in user.get("username", "").lower() 
                           or search_query.lower() in user.get("email", "").lower()
                           or (user.get("remark") and search_query.lower() in user.get("remark", "").lower())]
            elif search_options == "仅用户名":
                filtered = [user for user in users if search_query.lower() in user.get("username", "").lower()]
            elif search_options == "仅邮箱":
                filtered = [user for user in users if search_query.lower() in user.get("email", "").lower()]
            elif search_options == "仅备注":
                filtered = [user for user in users if user.get("remark") and search_query.lower() in user.get("remark", "").lower()]
            
            if filtered:
                st.markdown(f"<div class='success-msg'>找到 {len(filtered)} 个匹配的用户</div>", unsafe_allow_html=True)
                
                # 转换为DataFrame以美化显示
                df = pd.DataFrame(filtered)
                # 重新排列列的顺序
                columns_order = ['id', 'username', 'email', 'remark', 'created_at']
                df = df[columns_order]
                # 重命名列
                df.columns = ['ID', '用户名', '邮箱', '备注', '创建时间']
                
                # 高亮显示匹配的关键字（这里只是示意，实际无法在dataframe中高亮）
                st.dataframe(df, use_container_width=True)
            else:
                st.markdown("<div class='info-msg'>未找到匹配的用户</div>", unsafe_allow_html=True)
# 主程序已经在文件顶部设置，不需要额外的main函数
